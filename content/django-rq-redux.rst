django-rq redux: advanced techniques and tools
##############################################

:date: 2015-09-01 14:20
:tags: django, python, tasks, jobs, rq, django-rq, asynchronous, scheduling, redis
:category: django
:slug: django-rq-redux
:author: Serafeim Papastefanos
:summary: Another article about django-rq with some more advanced techniques and tools!

.. contents::

Introduction
============

In the `previous django-rq article <{filename}async-tasks-with-django-rq.rst>`_
we presented a quick introduction to asynchronous job queues and created a
small (but complete) project that used rq and django-rq to implement asynchronous
job queues in a django project. 

In this article, we will present some more advanced techniques and tools 
for improving the capabilities of our asynchronous tasks and
integrate them to the https://github.com/spapas/django-test-rq project (please
checkout tag django-rq-redux
``git checkout django-rq-redux``)



Displaying your task progress
=============================

Sometimes, especially for long-running tasks it is useful to let 
the user (task initiator) know what is the status of each task he's started. For this,
I recommend creating a task-description model that will hold the required information for this 
task with more or less the following fields (please also check ``LongTask`` model of
django-test-rq): 

.. code::

  class LongTask(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128, help_text='Enter a unique name for the task',)
    progress = models.PositiveIntegerField(default=0)
    result = models.CharField(max_length=128, blank=True, null=True)
    
Now, when the view that starts the task is ``POST`` ed, you'll first create 
the ``LongTask`` model instance with a result of ``'QUEUED'`` and a progress
of 0 (and a name that identifies your task) and then you'll start the real task
asynchronously by passing the LongTask instance, something like this (also check 
``LongTaskCreateView``):

.. code::

    long_task = LongTask.objects.create(...)
    long_runnig_task.delay(long_task)

In your asynchronous job, the first thing you'll need to do is to set its result
to 'STARTED' and save it so that the user will immediately see when he's job is
actually started. Also, if you can estimate its progress, you can update its
progress value with the current value so that the user will know how close he
is to finishing. Finally, when the job finished (or if it throws an expectable
exception) you'll update its status accordingly. Here's an example of my
long_running_task that just waits for the specifid amount of seconds:

.. code::

  @job('django-test-rq-low')
  def long_runnig_task(task):
    job = get_current_job()
    task.job_id = job.get_id()
    
    task.result = 'STARTED'
    
    duration_in_second_persentages = task.duration*1.0 / 100
    for i in range(100):
        task.progress = i
        task.save()
        print task.progress
        time.sleep(duration_in_second_persentages)
    
    task.result = 'FINISHED'
    task.save()
    return task.result
    
To have proper feedback I propose to have your task-description model instance 
created by the view that starts the asynchronous task and *not* by the 
actual task! This is important since the worker may be full so the asynchronous
task will need a lot of time until is actually started (or maybe there are no
running workers - more on this later) and the user will not be able to see
his task instance anywhere (unless of course you provide him access to the actual task
queue but I don't recommend this).

Displaying your queue statistics
================================

django-rq has a really nice dashboard with a lot of queue statistics (
instructions here 
https://github.com/ui/django-rq#queue-statistics and also on django-test-rq 
project) which I recommend to always enable. 

Also, there's the individual use django-rq-dashboard_ project that could
be installed to display some more statistics, however the only extra
statistic that you can see throuh django-rq-dashboard is the status of
your scheduled jobs so I don't recommend installing it if you don't
use scheduling.


Making sure that workers for your queue are actually running
============================================================

Using the django-rq dashboard you can make sure that all queues
have at least one worker. However, sometimes workers fail, or
maybe you've forgotten to start your workers or not configured
your application correctly (this happens to me all the time for
test/uat projects). So, for tasks that you want to display feedback
to the user, you can easily add a check to make sure that there are
active workers using the following code:

.. code::

    from rq import Worker
    import django_rq

    redis_conn = django_rq.get_connection('default')
    if len([
        x for x in Worker.all(connection=redis_conn) 
            if 'django-test-rq-low' in x.queue_names()
    ]) == 0:
        # Error -- no workers 
            
With ``Worker.all()`` you get all workers for a connection and the ``queue_names()``
method returns the names that each worker serves. So we check that we have at least one
worker for that queue. 

This check can be added when the job is started and display a feedback error
to the user (check example in django-test-rq).

For quick tasks (for example sending emails etc) you should not display anything
to the user even if no workers are running (since the task *will* be queued and
will be executed eventually when the workers are started) but instead send an email to the administrators
so that they will start the workers.

Checking how many jobs are in the queue
=======================================

To find out programatically how many jobs are actually in the queue (and display a message
if the queue has too many jobs etc) you'll need to use the ``Queue`` class, something like this:

.. code::

  from rq import Queue
  
  redis_conn = django_rq.get_connection('default')
  queue = Queue('django-test-rq-default', connection=redis_conn)
  print queue.name
  print len(queue.jobs)
  
  
Better exception handling
=========================

When a job fails, rq will put it in a failed jobs queue and finish with it. You (as administrator) 
won't get any feedback and the user (unless he has access to that failed jobs queue) won't be 
able to do anything aboutt this job. 

In almost all cases you can't rely only on this behavior but instead you have to 
`install a custom exception handler`_. Using the custom exception handler you can
do whatever you want for each failed job. For instance, you can create a new instance
of a ``FailedTask`` model which will have information about the failure and the 
original task allow the user (or administrator) to restart the failed task after
he's fixed the error conditions. 

Or, if you want to be informed when a job is failed, you can just send an email
to ``ADMINS`` and fall back to the default behavior to enqueue the failed task the
failed jobs queue (since job exception handlers can be chained).

A simple management command that starts a worker for a specific queue and installs 
a custom exception handler follows: 

.. code:: 

    from django.conf import settings
    from django.core.management.base import BaseCommand

    import django_rq
    from rq import Queue, Worker

    def my_handler(job, *exc_info):
        print "FAILURE"
        print job
        print exc_info

    class Command(BaseCommand):
        def handle(self, *args, **options):
            redis_conn = django_rq.get_connection('default')
            
            q = Queue(settings.DJANGO_TEST_RQ_LOW_QUEUE, connection=redis_conn)
            worker = Worker([q], exc_handler=my_handler, connection=redis_conn)
            worker.work()

This handler is for demonstration purposes since it just prints a message to the console 
(so please do not use it)!

Multiple django-apps, single redis db
=====================================

One thing to keep in mind is that the only thing that seperates the queues are
their name. If you have many django applications that define a "default" (or "low", "hight" etc)
and they all use the *same* redis database to store their queue, the workers
of each application won't know which jobs belong to them and they'll end up
dequeuing the wrong job types. This will lead to an exception or, if you
are really unlucky to a very nasty bug!

To avoid this, you can either use a different redis database (not database server)
for each of your apps or add a prefix with the name of your app to your queue names:

Each redis database server can host a number of databases that are identified
by a number (that's what the /0 you see in ``redis://127.0.0.1:6379/0`` means)
and each one of them has a totally different keyspace. So, if you use /0 in an
application and /1 in another application, you'll have no problems. This solution
has the disadvantage that you need to be really careful to use different database
numbers for your projects and also the number of possible databases that redis
can use is limited by a configuration file (so if you reach the maximum you'll
need to also increase that number)!

Instead of this, you can avoid using the 'default' queue, and use queues that
contain your application name in their name, for example, for the sample project
you could create something like 'django-test-rq-default', 'django-test-rq-low',
'django-test-rq-high' etc. You need to configure the extra queues by adding them
to the ``RQ_QUEUES`` dictionary (check settings.py of django-test-rq) and then
put the jobs to these queues using for example the job decorator 
(``@job('django-test-rq-default')``)
and run your workers so that they will retrieve jobs from these queues
(``python manage.py rqworker django-test-rq-default``) and not the
default one (which may contain jobs of other applications).

If you use the default queue, and because you'll need to use its name to
many places, I recommend to add a (f.i) ``QUEUE_NAME = 'django-test-rq-default'`` 
setting and use this instead of just a string to be totally DRY.

**Update 13/09/2015**: Please notice that using a *single* redis database server
(either with multiple numeric databases or in the same database using a keyword
in keys to differentiate the apps) `is not recommended`_ as commenter 
Itamar Haber pointed out to me! 

This is because for speed reasons redis uses a single thread to handle all requests
(regardless if they are in the same or different numerical databases), so all 
resources may be used by a single, redis hungry, application and leave all others to starve!

Therefore, the recommended solution is to have a *different redis* server for each different
application. This does not mean that you need to have different servers, just to run
different instances of redis binding to different IP ports. Redis uses very little
resourecs when it is idle (`empty instance uses ~ 1 MB RAM`_) so you can run a lot
of instances in a single server.

Long story short, my proposal is to have a redis.conf *inside* your application root tree
(next to manage.py and requirements.txt) which has the redis options for each
application. The options in redis.conf that need to be changed per application
is the port that this redis instance will bind (this port also needs to be passed to 
django settings.py) and the pid filename if you daemonize redis -- I recommend using
a tool like supervisord_ instead so that you won't need any daemonizing and pid files for 
each per-app-redis-instance!

Low level debugging
===================

In this section I'll present some commands that you can issue to your redis
server using a simple telnet connection to get various info about your queues. You
probably will never need to issue these commands to actually debug, but they
will answer some of your (scientific) questions! In the following, ``>`` is
things I type, ``#`` are comments, ``[...]`` is more output and everything else is the output I get: 

.. code::

    > telnet 127.0.0.1 6379

    # You won't see anything at first but you'll be connected and you can try typing things

    > INFO

    $1020
    redis_version:2.4.10
    redis_git_sha1:00000000
    # [...]
    db0:keys=83,expires=2
    db1:keys=26,expires=1 # My redis server has two databases

    # Now you'll see what you type!

    > SELECT 1 
    + OK # Now queries will be issued to database 1
    > SELECT 0 
    + OK # Now queries will be issued to database 0

    KEYS rq* # List all rq related queues
    *25
    $43
    rq:job:1d7afa32-3f90-4502-912f-d58eaa049fb1
    $43
    rq:queue:django-test-rq-low
    $43
    [...]

    > SMEMBERS rq:workers # See workers
    *1
    $26
    rq:worker:SERAFEIM-PC.6892

    > LRANGE rq:queue:django-test-rq-low 0 100 # Check queued jobs
    *2
    $36
    def896f4-84cb-4833-be6a-54d917f05271
    $36
    53cb1367-2fb5-46b3-99b2-7680397203b9

    > HGETALL rq:job:def896f4-84cb-4833-be6a-54d917f05271 # Get info about this job
    *16 
    $6
    status
    $6
    queued
    $11
    description
    $57
    tasks.tasks.long_runnig_task(<LongTask: LongTask object>)
    $10
    created_at
    $20
    2015-09-01T09:04:38Z
    $7
    timeout
    $3
    180
    $6
    origin
    $18
    django-test-rq-low
    $11
    enqueued_at
    $20
    2015-09-01T09:04:38Z
    $4
    data
    $409
    [...] # data is the pickled parameters passed to the job !

    > HGET rq:job:def896f4-84cb-4833-be6a-54d917f05271 status # Get only status
    $6
    queued

For more info on querying redis you can check the `redis documentation`_ and especially 
http://redis.io/topics/data-types and http://redis.io/commands.

Conclusion
==========

Using some of the above techniques will help you in your asynchronous
task adventures with rq. I'll try to keep this article updated with
any new techniques or tools I find in the future!


.. _celery: http://www.celeryproject.org/
.. _RQ: http://python-rq.org/
.. _`many dependencies`: http://celery.readthedocs.org/en/latest/faq.html#does-celery-have-many-dependencies
.. _`install a custom exception handler`: http://python-rq.org/docs/exceptions/
.. _django-rq: https://github.com/ui/django-rq
.. _django-rq-dashboard: https://github.com/brutasse/django-rq-dashboard
.. _rq-scheduler: https://github.com/ui/rq-scheduler
.. _Vagrant: https://www.vagrantup.com/
.. _supervisord: http://supervisord.org/
.. _`redis documentation`: http://redis.io/documentation
.. _`is not recommended`: https://redislabs.com/blog/benchmark-shared-vs-dedicated-redis-instances#.VfUl0xHtmko
.. _`empty instance uses ~ 1 MB RAM`: http://redis.io/topics/faq
