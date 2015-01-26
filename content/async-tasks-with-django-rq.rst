Asynchronous tasks in django with django-rq
###########################################

:date: 2015-01-26 14:20
:tags: django, python, tasks, jobs, rq, django-rq, asynchronous, scheduling, redis
:category: django
:slug: async-tasks-with-django-rq
:author: Serafeim Papastefanos
:summary: Using django-rq to add queuing jobs (asynchronous tasks) and scheduling (cron-like) capabilities to a django project.

.. contents::

Introduction
============

Job queuing (asynchronous tasks) is a common requirement for non-trivial projects. Whenever an operation
can take more than half a second it should be put to a job queue in order to be run asynchronously by a 
seperate worker. This adds much complexity to the project since beyond the basic application (web) process
at least one more (worker) process needs to be run (and monitored etc) -- however, in most cases it can't be avoided.

Even for fairly quick tasks (like sending email through an SMTP server) you need to use an asynchronous task since
the time required for such a task is not really limited. So

Beyond job queuing, another relative requirement for many projects is to schedule a task to be run in the future
(similar to the ``at`` unix command) or at specific time intervals (similar to the ``cron`` unix command). For
instance, if a user is registered today we may need to check after one or two days if he's logged in and used our application - 
if he hasn't then probably he's having problems and we can call him to help him. Also, we could check every night
to see if any users that have registered to our application don't have activated their account through email activation
and delete these accounts.

Some terminology
----------------

- Job/Task: A piece of code that needs to be executed asynchronously by a worker
- Synchronous execution: A task is executed synchronously when the caller will wait (blocks) until the task has finished executing
- Asynchronous execution: A task is executed asynchronously when the caller just signals the callee to start executing and resumes execution immediately without waiting for the callee to finish
- Broker: Jobs/tasks to be executed are stored in the broker in a first in a first out queue which could be a normal database but most of the times is a specialized system called message broker
- Worker: A worker is a process/thread that runs independently and checks the broker for new tasks to be executed. When there are queued tasks, the worker dequeues them and executes them

Job queues in python
====================

The most known application for using job queues in python is celery_ which is a really great project that supports
many brokers,  integrates nicely
with python/django (but can be used even with other languages) and has
many more features (most of them are only useful on really big, enterprise projects). I've already used 
it in a previous application, however, because celery is really complex it needed a lot of time to configure it
successfully and I never was perfectly sure that my asynchronous task would work 100% :( 

Celery also has `many dependencies`_ in order to be able to talk with the different broker backends it supports,
improve multithreading support etc. They may be required in enterprise apps but not for most Django web based projects.

So, for small-to-average projects I recommend using a different asynchronous task solution instead of celery, particularly
(as you've already guessed from the title of this post) RQ_. RQ is simpler than celery, it integrates great with django
using the excellent django-rq_ package and doesn't actually have any more dependencies beyond redis support which is
needed as a broker. It even supports supports job scheduling through the rq-scheduler_ package (celery also supports
job scheduling through celery beat).

Although RQ and frieds are really easy to use (and have a nice documentation) I wasn't able to find
a complete example of using it with django, so I'll present one rather complete
exampe here (also found at https://github.com/spapas/django-test-rq), along with some comments on
how to use it in your production environment.

django-rq example
=================

This is a simple django project that can be used to asynchronously 
run and schedule jobs and examine their behavior:

The job that is run
-------------------

The asychronous task will run the following
function (defined in tasks.py - some code ommited):

.. code-block:: python

import requests

def get_url_words(url):
    r = requests.get(url)
    t.result = len(r.text)
    return t.result


So, it just retrieves the content of a url and counts its length. This is actually the
example that RQ also uses in its documentation.

Models
------

Beyond this, there are two models: ``Task`` that saves info
about an asynchronous task and ``ScheduledTask`` that saves info about a 
scheduled task. For each scheduled run of a scheduled task a new ``ScheduledTaskInstance``
will be created. These models contain info about when each job was started,
what was its result and what is the job id.

Views and forms
---------------

The homepage will show all ``Task`` and ``ScheduledTask`` instances. For each
``ScheduledTask`` all the corresponding ``ScheduledTaskInstance`` instances will
also be presented.

The form just retrieves a url to counts its content length. It also retrieves
two extra parameters if we want to create a scheduled task: 
scheduled times (how many times this task should run) and schedule interval
(how much time between each run).

Depending on if the task is scheduled or not, a different version of 
``get_url_words`` will be run: For the simple version, a new ``Task``
will be created which will contain the result of the ``get_url_words``,
the id of the job, the created time and the url. For the scheduled
version, a ``ScheduledTask`` containing the url and the job id will
be created only once, while for each scheduled run, a new 
``ScheduledTaskInstance`` will be created with the
result and start time (and a ForeignKey to then single ``ScheduledTask``
instance). 

It is important to notice here that *for scheduled tasks there would
be only one job id* for each run of that task!

settings.py
-----------
In order to use django_rq in your project you need to add it to your ``INSTALLED_APPS`` list. Beyond that, I've added the following
to my ``settings.py``

.. code-block:: python

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
    
    RQ_QUEUES = {
        'default': {
            'USE_REDIS_CACHE': 'default',
        },
    }
    
    RQ_SHOW_ADMIN_LINK = True
    
The CACHES configures the default django cache to a localhost installed Redis 
while RQ_QUEUES creates a default job queue for RQ that will use the same Redis
connection. RQ_SHOW_ADMIN_LINK just adds a link to django-admin of this project
that shows the status of the queues.

Configuring logging
-------------------

.. code-block:: python

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


Running the project
-------------------

I recommend using Vagrant_ to start a stock ubuntu/trusty32 box. After that, instal redis, virtualenv and virtualenvwrapper
and create/activate a virtualenv named ``rq``. You can go to the home directory of ``django-test-rq``
and install requirements through ``pip install requirements.txt`` and create the database tables with
``python manage.py migrate``. Finally you may run the project with ``python manage.py runserver_plus``.

Before scheduling any tasks we need to configure TODO

Configuring rqworker and rqscheduler
====================================



.. code::

    [program:rqworker]
    command=python manage.py rqworker
    directory=/vagrant/progr/py/rq/django-test-rq
    environment=PATH="/home/vagrant/.virtualenvs/rq/bin"
    user=vagrant
    redirect_stderr=true


Conclusion
==========

Although using job queues makes it more difficult for the developer and adds at least one
(and probably more) points of failure to a project (the workers, the broker etc) their
usage, even for very simple projects is unavoidable. 

Unless a complex, enterprise solution like celery is really required for a project
I recommend using the much simpler and easier to configure RQ project for all your
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
