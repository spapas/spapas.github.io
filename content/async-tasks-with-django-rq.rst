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
the time required for such a task is not really limited.

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
with django and has many more features (most of them are only useful on really big, enterprise projects). I've already used 
it in a previous application, however, because celery is really complex it needed a lot of time to configure it
successfully and I never was perfectly sure that my asynchronous task would work 100% :( 

Celery also has `many dependencies`_ in order to be able to talk with the different broker backends it supports,
improve multithreading support etc. They may be required in enterprise apps but not for most Django web based projects.

So, for small-to-average projects I recommend using a different asynchronous task solution instead of celery, particularly
(as you've already guessed from the title of this post) RQ_. RQ is simpler than celery, it integrates better with django
using the excellent django-rq_ package and doesn't actually have any more dependencies beyond redis support which is
needed as a broker. It even supports supports job scheduling through the rq-scheduler_ package (celery also supports
job scheduling through celery beat).


.. code-block:: python
    import reversion


    @reversion.register
    class RBook(models.Model):
        name = models.CharField(max_length=128)
        author = models.CharField(max_length=128)

        def get_absolute_url(self):
            return reverse("rbook_list")


django-reversion uses two tables in the database to keep track of revisions: ``revision`` and ``version``. Let's
take a look at their schemata:

.. code::

    .schema reversion_revision
    CREATE TABLE "reversion_revision" (
        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        "manager_slug" varchar(200) NOT NULL,
        "date_created" datetime NOT NULL,
        "comment" text NOT NULL,
        "user_id" integer NULL REFERENCES "auth_user" ("id")
    );

    .schema reversion_version
    CREATE TABLE "reversion_version" (
        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        "object_id" text NOT NULL,
        "object_id_int" integer NULL,
        "format" varchar(255) NOT NULL,
        "serialized_data" text NOT NULL,
        "object_repr" text NOT NULL,
        "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
        "revision_id" integer NOT NULL REFERENCES "reversion_revision" ("id")
    );

Conclusion
==========

In the above we say that it is really easy to add basic (*who* and *when*) auditing capabilities to your models: You just need to
inherit your models from the ``Auditable`` abstract class and inherit your Create and Update CBVs from ``AuditableMixin``.
If you want to know exactly *what* was changed then you have two solutions: django-simple-history to create an extra table for
each of your models so you'll be able to query your historical records (and easily extra aggregates, statistics etc) and 
django-reversion to save each version as a json object, so no extra tables will be created.

All three solutions for auditing have been implemented in a sample project at https://github.com/spapas/auditing-sample.

You can clone the project and, preferrably in a virtual environment, install requirements (``pip install -r requirements.txt``), 
do a migrate (``python manage.py migrate`` -- uses sqlite3 by default) and run the local development 
server (``python manage.py ruinserver``).


.. _celery: http://www.celeryproject.org/
.. _RQ: http://python-rq.org/
.. _`many dependencies`: http://celery.readthedocs.org/en/latest/faq.html#does-celery-have-many-dependencies
.. _django-rq: https://github.com/ui/django-rq
.. _rq-scheduler: https://github.com/ui/rq-scheduler
