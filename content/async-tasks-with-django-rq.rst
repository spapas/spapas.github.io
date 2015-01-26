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

The most known application for using job queues in python is celery_ which is a really great project and integrates nicely
with django. I've already used it with great success in a previous application. However, unfortuanately celery


To use django-reversion to keep track of changes to ``Book`` we can modify it like this:

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

As we can understand, the ``revision`` table holds information like who created this
revison (``user_id``) and when (``date_created``) while the ``version`` stores
a reference to the object that was modified (through a GenericForeignKey) and
the actual data (in the ``serialized_data`` field). By default it uses JSON
to serialize the data (the serialization format is in the ``format`` field). There's
an one-to-one relation between ``revision`` and ``version``.

If we create an instance of ``RBook`` we'll see the following in the database:

.. code::

    sqlite> select * from reversion_revision;
    1|default|2015-01-21 10:31:25.233000||1

    sqlite> select * from reversion_version;
    1|1|1|json|[{"fields": {"name": "asdasdasd", "author": "asdasd"}, "model": "sample.rbook", "pk": 1}]|RBook object|12|1

``date_created`` and ``user_id`` are stored on ``revision`` while ``format``, ``serialized_data``, ``content_type_id`` and
``object_id_int`` (the ``GenericForeignKey``) are stored in ``version``.

Usage
-----

To find out information about an object you have to use the ``reversion.get_for_object(object)`` method. In order to be
easily used in templates I recommend creating the following ``get_versions()`` method in each model that is registered with django-reversion

.. code::

    def get_versions(self):
        return reversion.get_for_object(self)

Now, each version has a ``revision`` attribute for the corresponding revision and can be used to do the following:

* get the user that made the change through the ``revision.user`` attribute
* get the date of the change through the ``revision.date_created`` attribute
* get the values of the object fields as they were in this revision using the ``field_dict`` attribute
* get a model instance as it was on that revision using the ``object_version.object`` attribute
* revert to that previous version of that object using the ``rever()`` method

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

