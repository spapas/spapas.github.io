My essential guidelines for better Django development
#####################################################
:status: draft
:date: 2022-09-28 11:10
:tags: python, django
:category: django
:slug: django-guidelines
:author: Serafeim Papastefanos
:summary: A list of guidelines that I follow in every non-toy Django project I develop

Introduction
============

In this article I'd like to present a list of guidelines I follow when I develop
Django projects, especially projects that are destined to be used in a production
environment for many years. I am using django for more than 10 years as my day to
day work tool to develop applications for the public sector organization I work for.

My organization has got a number of different Django projects that cover its needs, with
some of them running successfully for more than 10 years, since Django 1.4. 

1. surrogate keys
2. through moldel m2m
3. no choices
4. trees
5. custom user model
	

Model design guidelines
=======================

Avoid using choices
-------------------

Django has the convenient feature of allowing you to define `choices for a field`_ by defining 
a tuple of key-value pairs the field can take. So you'll define a field like 
``choice_field = models.CharField(choices=CHOICES)`` with ``CHOICES`` being a tuple like 

.. code-block:: python

    CHOICES = (
        ('C1', 'Choice 1 description'),
        ('C2', 'Choice 2 description'),
        ('C3', 'Choice 3 description'),
    )

and your database will contain ``C1``, ``C2`` or ``C3`` as values for the field while your users will see 
the corresponding description.

This is a great feature for prototyping however I
suggest to use it only on toy-prototyping-MVP projects and use normal relations in production projects instead. So the choice field
would be a Foreign Key and the choices would be tuples on the referenced table. The reasons for this are:

* The integrity of the choices is only on the application level. So people can go to the database and change a choice field with a random value
* Your users may want to edit the choices (add new ones) or change their descriptions. This is easy with a foreign key through the django-admin but needs a code change with choices.
* Change properties
* 

Always use surrogate keys
-------------------------

A `surrogate key`_ is a unique identifier for a database tuple which is used as the primary key. By default Django always adds a
surrogate key to your models. However, some people may be tempted to use a natural key as the primary key. This is a bad idea
and you should avoid it. 



Views guidelines
----------------

Template guidelines
-------------------

Settings guidelines
-------------------

Debugging guidelines
--------------------

Conclusion
----------

Using the above steps you can easily setup a postgres database server on windows for development. Some advantages of the method
proposed here are:

* Since you configure the data directory you can have as many clusters as you want (run initdb with different data directories and pass them to postgres)
* Since nothing is installed globally, you can have as many postgresql versions as you want, each one having its own data directory. Then you'll start the one you want each time! For example I've got Postgresql 12,13 and 14.5.
* Using the trust authentication makes it easy to connect with whatever user
* Running the database from postgresql.exe so it has a dedicated window makes it easy to know what the database is doing, peeking at the logs and stopping it (using ctrl+c)

.. _`surrogate key`: https://en.wikipedia.org/wiki/Surrogate_key
.. _`choices for a field`: https://docs.djangoproject.com/en/stable/ref/models/fields/#choices

.. _`official website`: https://www.postgresql.org/download/windows/
.. _`zip archives`: https://www.enterprisedb.com/download-postgresql-binaries
.. _`postgres trust authentication page`: https://www.postgresql.org/docs/current/auth-trust.html
.. _`psql reference page`: https://www.postgresql.org/docs/14/app-psql.html`
.. _`this SO issue`: https://stackoverflow.com/questions/20794035/postgresql-warning-console-code-page-437-differs-from-windows-code-page-125
.. _dbeaver: https://dbeaver.io/
.. _`template database`: https://www.postgresql.org/docs/current/manage-ag-templatedbs.html