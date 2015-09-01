Asynchronous tasks in django with django-rq
###########################################

:date: 2015-01-27 14:20
:tags: django, python, tasks, jobs, rq, django-rq, asynchronous, scheduling, redis
:category: django
:slug: async-tasks-with-django-rq
:author: Serafeim Papastefanos
:summary: Using django-rq to add queuing jobs (asynchronous tasks) and scheduling (cron-like) capabilities to a django project.

.. contents::

**Update 01/09/15**: I've written a new post about rq and django with some
`more advanced techniques <{filename}django-rq-redux.rst>`_
! 

Introduction
============



Job queuing (asynchronous tasks) is a common requirement for non-trivial django projects. Whenever an operation
can take more than half a second it should be put to a job queue in order to be run asynchronously by a
seperate worker. This is really important since the response to a user request needs to be immediate
or else the users will experience laggy behavior and start complaining! 
Even for fairly quick tasks (like sending email through an SMTP server) you need to use an asynchronous task 
if you care about your users since
the time required for such a task is not really limited. 

Using job queues is involved not only for the developers of the application (who need to create the
asynchronous tasks and give feedback to the users when the've finished since they can't use the normal
HTTP response) and but also for the administrators, since, in order to support job queues at least two
more componets will be needed:

* One job queue that will store the jobs to be executed next in a first in first queue. This could be the normal database of the project however it's not recommended for performance reasons and most of thetimes it is a specific component called "Message Broker" 
* One (or more) workers that will monitor the job queue and when there is work to do they will dequeue and execute it

These can all run in the same server but if it gets saturated they can easily be seperated (even more work for
administrators).

Beyond job queuing, another relative requirement for many projects is to schedule a task to be run in the future
(similar to the ``at`` unix command) or at specific time intervals (similar to the ``cron`` unix command). For
instance, if a user is registered today we may need to check after one or two days if he's logged in and used our application -
if he hasn't then probably he's having problems and we can call him to help him. Also, we could check every night
to see if any users that have registered to our application don't have activated their account through email activation
and delete these accounts. Scheduled tasks should be also run by the workers mentioned above.


Job queues in python
====================

The most known application for using job queues in python is celery_ which is a really great project that supports
many brokers,  integrates nicely
with python/django (but can be used even with other languages) and has
many more features (most of them are only useful on really big, enterprise projects). I've already used
it in a previous application, however, because celery is really complex I found it rather difficult to
configure it successfully and I never was perfectly sure that my asynchronous task would actually work or
that I'd used the correct configuration for my needs!

Celery also has `many dependencies`_ in order to be able to talk with the different broker backends it supports,
improve multithreading support etc. They may be required in enterprise apps but not for most Django web based projects.

So, for small-to-average projects I recommend using a different asynchronous task solution instead of celery, particularly
(as you've already guessed from the title of this post) RQ_. RQ is simpler than celery, it integrates great with django
using the excellent django-rq_ package and doesn't actually have any more dependencies beyond redis support which is
used as a broker (however most modern django projects already use redis for their caching needs as an  alternative
to memcached). 

It even supports supports job scheduling through the rq-scheduler_ package (celery also supports
job scheduling through celery beat): Run a different process (scheduler) that polls the job
scheduling queue for any jobs that need to be run because of scheduling and if yes put them to 
the normal job queue.

Although RQ and frieds are really easy to use (and have nice documentation) I wasn't able to find
a *complete* example of using it with django, so I've implemented one 
(found at https://github.com/spapas/django-test-rq -- since I've updated this project a bit
with new stuff, 
please checkout tag django-test-rq-simple ``git checkout django-test-rq-simple``) mainly for my own testing
purposes. To help others that want to also use RQ in their project but don't know from where
to start, I'll present it in the following paragraphs, along with some comments on
how to actually use RQ in your production environment. 

django-test-rq
==============

This is a simple django project that can be used to asynchronously
run and schedule jobs and examine their behavior. The job to be scheduled just downloads a provided
URL and counts its length. There is only one django application (tasks) that contains two views, one
to display existing tasks and create new ones and one to display some info for the jobs.


models.py
---------

Two models (``Task`` and ``ScheduledTask``) for saving individual tasks and
scheduled tasks and one model (``ScheduledTaskInstance``) to save scheduled
instances of each scheduled task.

.. code-block:: python

    from django.db import models
    import requests
    from rq import get_current_job


    class Task(models.Model):
        # A model to save information about an asynchronous task
        created_on = models.DateTimeField(auto_now_add=True)
        name = models.CharField(max_length=128)
        job_id = models.CharField(max_length=128)
        result = models.CharField(max_length=128, blank=True, null=True)


    class ScheduledTask(models.Model):
        # A model to save information about a scheduled task
        created_on = models.DateTimeField(auto_now_add=True)
        name = models.CharField(max_length=128)
        # A scheduled task has a common job id for all its occurences
        job_id = models.CharField(max_length=128)


    class ScheduledTaskInstance(models.Model):
        # A model to save information about instances of a scheduled task
        scheduled_task = models.ForeignKey('ScheduledTask')
        created_on = models.DateTimeField(auto_now_add=True)
        result = models.CharField(max_length=128, blank=True, null=True)



forms.py
--------

A very simple form to create a new task.

.. code-block:: python

    from django import forms

    class TaskForm(forms.Form):
        """ A simple form to read a url from the user in order to find out its length
        and either run it asynchronously or schedule it schedule_times times,
        every schedule_interval seconds.
        """
        url = forms.CharField(label='URL', max_length=128, help_text='Enter a url (starting with http/https) to start a job that will download it and count its words' )
        schedule_times = forms.IntegerField(required=False, help_text='How many times to run this job. Leave empty or 0 to run it only once.')
        schedule_interval = forms.IntegerField(required=False, help_text='How much time (in seconds) between runs of the job. Leave empty to run it only once.')

        def clean(self):
            data = super(TaskForm, self).clean()
            schedule_times = data.get('schedule_times')
            schedule_interval = data.get('schedule_interval')

            if schedule_times and not schedule_interval or not schedule_times and schedule_interval:
                msg = 'Please fill both schedule_times and schedule_interval to schedule a job or leave them both empty'
                self.add_error('schedule_times', msg)
                self.add_error('schedule_interval', msg)


views.py
--------

This is actually very simple if you're familiar with Class Based Views. Two CBVs
are defined, one for the Task form + Task display and another for the Job display.

.. code-block:: python

    from django.views.generic.edit import FormView
    from django.views.generic import TemplateView
    from forms import TaskForm
    from tasks import get_url_words, scheduled_get_url_words
    from models import Task,ScheduledTask
    from rq.job import Job
    import django_rq
    import datetime

    class TasksHomeFormView(FormView):
        """
        A class that displays a form to read a url to read its contents and if the job
        is to be scheduled or not and information about all the tasks and scheduled tasks.

        When the form is submitted, the task will be either scheduled based on the
        parameters of the form or will be just executed asynchronously immediately.
        """
        form_class = TaskForm
        template_name = 'tasks_home.html'
        success_url = '/'

        def form_valid(self, form):
            url = form.cleaned_data['url']
            schedule_times = form.cleaned_data.get('schedule_times')
            schedule_interval = form.cleaned_data.get('schedule_interval')

            if schedule_times and schedule_interval:
                # Schedule the job with the form parameters
                scheduler = django_rq.get_scheduler('default')
                job = scheduler.schedule(
                    scheduled_time=datetime.datetime.now(),
                    func=scheduled_get_url_words,
                    args=[url],
                    interval=schedule_interval,
                    repeat=schedule_times,
                )
            else:
                # Just execute the job asynchronously
                get_url_words.delay(url)
            return super(TasksHomeFormView, self).form_valid(form)

        def get_context_data(self, **kwargs):
            ctx = super(TasksHomeFormView, self).get_context_data(**kwargs)
            ctx['tasks'] = Task.objects.all().order_by('-created_on')
            ctx['scheduled_tasks'] = ScheduledTask.objects.all().order_by('-created_on')
            return ctx


    class JobTemplateView(TemplateView):
        """
        A simple template view that gets a job id as a kwarg parameter
        and tries to fetch that job from RQ. It will then print all attributes
        of that object using __dict__.
        """
        template_name = 'job.html'

        def get_context_data(self, **kwargs):
            ctx = super(JobTemplateView, self).get_context_data(**kwargs)
            redis_conn = django_rq.get_connection('default')
            try:
                job = Job.fetch(self.kwargs['job'], connection=redis_conn)
                job = job.__dict__
            except:
                job = None

            ctx['job'] = job
            return ctx

tasks.py
--------

Here two jobs are defined: One to be used for simple asynchronous tasks and the
other to be used for scheduled asynchronous tasks (since for asynchronous tasks
we wanted to group their runs per job id).

The ``@job`` decorator will add the ``delay()`` method (used in ``views.py``) to
the function. It's not really required for ``scheduled_get_url_words`` since
it's called through the ``scheduled.schedule``.

When a task is finished, it can return a value (like we do in ``return task.result``)
which will be saved for a limited amount of time (500 seconds by default - could be
even saved for ever) to redis.
This may be useful in some cases, however, I think that for normal web applications it's
not that useful, and since here we use normal django models
for each task, we can save it to that model's instance instead.

.. code-block:: python

    import requests
    from models import Task, ScheduledTask, ScheduledTaskInstance
    from rq import get_current_job
    from django_rq import job


    @job
    def get_url_words(url):
        # This creates a Task instance to save the job instance and job result
        job = get_current_job()

        task = Task.objects.create(
            job_id=job.get_id(),
            name=url
        )
        response = requests.get(url)
        task.result = len(response.text)
        task.save()
        return task.result


    @job
    def scheduled_get_url_words(url):
        """
        This creates a ScheduledTask instance for each group of
        scheduled task - each time this scheduled task is run
        a new instance of ScheduledTaskInstance will be created
        """
        job = get_current_job()

        task, created = ScheduledTask.objects.get_or_create(
            job_id=job.get_id(),
            name=url
        )
        response = requests.get(url)
        response_len = len(response.text)
        ScheduledTaskInstance.objects.create(
            scheduled_task=task,
            result = response_len,
        )
        return response_len


settings.py
-----------

.. code-block:: python

    import os
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = '123'
    DEBUG = True
    TEMPLATE_DEBUG = True
    ALLOWED_HOSTS = []

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'django_extensions',
        'django_rq',

        'tasks',
    )

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

    ROOT_URLCONF = 'django_test_rq.urls'
    WSGI_APPLICATION = 'django_test_rq.wsgi.application'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    STATIC_URL = '/static/'

    # Use redis for caches
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    # Use the same redis as with caches for RQ
    RQ_QUEUES = {
        'default': {
            'USE_REDIS_CACHE': 'default',
        },
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    RQ_SHOW_ADMIN_LINK = True

    # Add a logger for rq_scheduler in order to display when jobs are queueud
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },

        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'rq_scheduler': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

By default, rq_scheduler won't log anything so we won't be able to see
any output when new instances of each scheduled task are queued for execution.
That's why we've overriden the LOGGING setting in order to actually log
rq_scheduler output to the console.


Running the project
-------------------

I recommend using Vagrant_ to start a stock ubuntu/trusty32 box. After that, install redis, virtualenv and virtualenvwrapper
and create/activate a virtualenv named ``rq``. You can go to the home directory of ``django-test-rq``
and install requirements through ``pip install requirements.txt`` and create the database tables with
``python manage.py migrate``. Finally you may run the project with ``python manage.py runserver_plus``.


rqworker and rqscheduler
========================

Before scheduling any tasks we need to run two more processes:

- rqworker: This is a worker that dequeues jobs from the queue and executes them. We could run more than one onstance of this job if we need it.
- rqscheduler: This is a process that runs every one minute and checks if there are scheduled jobs that have to be executed. If yes, it will add them to the queue in order to be executed by a worker.

For development
---------------

If you want to run rqworker and rqscheduler for your development environment you can just do it with
running ``python manage.py rqworker`` and ``python mange.py rqscheduler`` through screen/tmux. If everything
is allright you should see tasks being added to the queue and scheduled (you may need to refresh the
homepage before seeing everything since a task may be executed after the response is created).

Also, keep in mind that rqscheduler runs once every minute by default so you may need to wait up to 
minute to see a ``ScheduledTask`` instance. Also, this means that you can't run more than one scheduled
task instance per minute.

For production
--------------

Trying to create daemons through screen is not
sufficient for a production envornment since we'd like to actually have logging, monitoring and of course
automatically start rqworker and rqscheduler when the server boots. 

For this, I recommend using the supervisord_ tool which
can be used to monitor and control a number of processes. There are other similar tools, however I've
found supervisord the easier to use.

In order to monitor/control a process through supervisord you need to add a ``[program:progrname]`` section in
supervisord's configuration and pass a number of parameters. The ``progname`` is the name of the monitoring
process. Here's how rqworker can be configured using supervisord:

.. code::

    [program:rqworker]
    command=python manage.py rqworker
    directory=/vagrant/progr/py/rq/django-test-rq
    environment=PATH="/home/vagrant/.virtualenvs/rq/bin"
    user=vagrant
    

The options used will chdir to ``directory`` and execute ``command`` as ``user``. The ``environment``
option can be used to set envirotnment variables - here we set ``PATH`` in order to use a specific
virtual environment. This will allow you to monitor rqworker through supervisord and log its 
output to a file in ``/var/log/supervisor`` (by default). A similar entry needs to be added for
rqscheduler of course. If everything has been configured correctly, when you reload the supervisord
settings you can run ``sudo /usr/bin/supervisorctl`` and should see something like

.. code::

    rqscheduler                      RUNNING    pid 1561, uptime 0:00:03
    rqworker                         RUNNING    pid 1562, uptime 0:00:03
    
Also, tho log files should contain some debug info.    


Conclusion
==========

Although using job queues makes it more difficult for the developer and adds at least one
(and probably more) points of failure to a project (the workers, the broker etc) their
usage, even for very simple projects is unavoidable.

Unless a complex, enterprise solution like celery is really required for a project
I recommend using the much simpler and easier to configure RQ for all your
asynchronous and scheduled task needs. Using RQ (and the relative projects django-rq
and rq-scheduler) we can easily add production ready queueued and scheduled jobs to
any django project.

In this article we presented a small introduction to RQ and its friends and saw how
to configure django to use it in a production ready environment using a small
django project (https://github.com/spapas/django-test-rq) which was implemented as a companion
to help readers quickly test the concepts presented here.


.. _celery: http://www.celeryproject.org/
.. _RQ: http://python-rq.org/
.. _`many dependencies`: http://celery.readthedocs.org/en/latest/faq.html#does-celery-have-many-dependencies
.. _django-rq: https://github.com/ui/django-rq
.. _rq-scheduler: https://github.com/ui/rq-scheduler
.. _Vagrant: https://www.vagrantup.com/
.. _supervisord: http://supervisord.org/