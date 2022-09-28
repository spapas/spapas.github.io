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
------------

In this article I'd like to present a list of guidelines I follow when I develop
Django projects, especially projects that are destined to be used in a production
environment for many years. I am using django for more than 10 years as my day to
day work tool to develop applications for the public sector organization I work for.

My organization has got a number of different Django projects that cover its needs, with
some of them running successfully for more than 10 years, since Django 1.4. 

Guidelines for learning Django
------------------------------

Model design guidelines
-----------------------

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

.. _`official website`: https://www.postgresql.org/download/windows/
.. _`zip archives`: https://www.enterprisedb.com/download-postgresql-binaries
.. _`postgres trust authentication page`: https://www.postgresql.org/docs/current/auth-trust.html
.. _`psql reference page`: https://www.postgresql.org/docs/14/app-psql.html`
.. _`this SO issue`: https://stackoverflow.com/questions/20794035/postgresql-warning-console-code-page-437-differs-from-windows-code-page-125
.. _dbeaver: https://dbeaver.io/
.. _`template database`: https://www.postgresql.org/docs/current/manage-ag-templatedbs.html