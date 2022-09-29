My essential guidelines for better Django development
#####################################################

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
        ('CHOICE1', 'Choice 1 description'),
        ('CHOICE2', 'Choice 2 description'),
        ('CHOICE3', 'Choice 3 description'),
    )

and your database will contain ``CHOICE1``, ``CHOICE2`` or ``CHOICE3`` as values for the field while your users will see 
the corresponding description.

This is a great feature for prototyping however I
suggest to use it only on toy-prototyping-MVP projects and use normal relations in production projects instead. So the choice field
would be a Foreign Key and the choices would be tuples on the referenced table. The reasons for this are:

* The integrity of the choices is only on the application level. So people can go to the database and change a choice field with a random value.
* More general, the database design is not normalized; saving ``CHOICE1`` for every row is not ideal.
* Your users may want to edit the choices (add new ones) or change their descriptions. This is easy with a foreign key through the django-admin but needs a code change with choices.
* It is almost sure that you will need to add "properties" to your choices. No matter what your current requirements are, they are going to change. For example, you may want to make a choice "obsolete" so it can't be picked by users. This is trivial when you use a foreign key but not very easy when you use choices.
* The values of the choices is saved only inside your app. The database has only the ``'CHOICE1', 'CHOICE2'`` etc values, so you'll need to re-use the descriptions when your app is not used. For example, you may have reports that are generated directly from database queries so you'll need to add the description of each key to your query using something like ``CASE``.
* It easier to use the ORM to annotate your queries when you use relations instead of the choices.

The disadvantage of relations is of course that you'll need to follow the relation to display the values. So you must be
careful to use ``select_related`` to avoid the n+1 queries problem.

So, in short, I suggest to use choices only for quick prototyping and covert them to normal relations in production projects. 
If you already are using choices in your project but want to convert them to normal relations, you can use take a look 
at my `Django choices to ForeignKey article <{filename}django-rq-redux.rst>`_.


Always use surrogate keys
-------------------------

A `surrogate key`_ is a unique identifier for a database tuple which is used as the primary key. By default Django always adds a
surrogate key to your models. However, some people may be tempted to use a natural key as the primary key. Although this is possible
and supported in Django, I'd recommend to stick to integer surrogate keys. Why ?

* Django is more or less build upon having integer primary keys. Although non-integer primary keys are supported in core Django, you can't be assured that this will be supported by the various addons/packages that you'll want to use.
* I understand that your requirements say that "the field X will be unique and should be used to identify the row". This is never true; this can easily be changed in the future and your primary key may stop being unique! It has happened to me and the solution was *not* something I'd like to discuss here. If there's a field in the row that is guaranteed to be unique you can make it unique in the database level by adding ``unique==True``; there's no reason to also make it a primary key.
* Relying on all your models having an ``id`` integer primary key makes it easier to write your code and other people reading it.
* Using an auto-increment primary key is the fastest way to insert a new row in the database (when compared to, for example using a random uuid)

An even worse idea is to use composite keys (i.e define a primary key using two fields of your tuple). There's actually 
a `17-year an open issue`_ about that in Django! This should be enough for you to understand that you shouldn't touch that
with a 10-foot pole. Even if it is implemented somehow in core django, you'll have something that can't be used with all 
other packages that rely on primary key being a single field.

Now, I understand that some public facing projects may not want to expose the auto-increment primary key since that discloses information
about the number of rows in the database, the number of rows that are added between a user's tuples etc. In this case, you may want to
either add a unique uuid field, or a slug field, or even better use a library like hashid to convert your integer ids to hashes. I haven't
used uuids myself, but for a slug field I had used the `django-autoslug`_ library and was very happy with it.

Concerning hashids, I'd recommend reading my `Django hashids article <{filename}django-hashid.rst>`_.

Always use a through model on your m2m relations
------------------------------------------------

To add a many-to-many relation in Django, you'll usually do something like ``toppings = models.ManyToManyField(Topping)``
(for a pizza). This is a very convenient but, similar to the choices I mentioned above, it is not a good practice for 
production projects.
This is because your requirements *will* change and you'll need to add properties to your m2m relation. Although this *is possible*,
it definitely is not pretty so it's better to be safe than sorry.

When you use the ``ManyToManyField`` field, django will generate an intermediate table with a name similar to app_model1_model2, i.e 
for pizza and topping it will be `pizzas_pizza_topping`. This table will have 3 fields - the primary key, a foreign key to the pizza
table and a foreign key to the topping table. This is the default behavior of Django and it is not configurable.

What happens if you want to add a relation to the pizzas_pizza_topping table? For example, the amount of each topping on a pizza. Or
the fact that some pizzas used to have that topping but it has been replaced now by another one? This is not possible unless you use 
a through table. As I said it is possible to fix that but it's not something that you'll want to do.

So, my recommendation is to *always* add a through table when you use a m2m relation. Create a model that will represent the relation
and has foreign keys to both tables along with any extra attributes the relation may have. 

.. code-block:: python

    class PizzaTopping(models.Model):
        pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
        topping = models.ForeignKey(Topping, on_delete=models.CASCADE)
        amount = models.IntegerField()

and define your pizza toppings relation like ``toppings = models.ManyToManyField(Topping, through=PizzaTopping)``. 

If the relation doesn't have no extra attributes don't worry: You'll be prepared when these are requested!

A bonus to that is that now you can query directly the PizzaTopping model and you can also add an admin interface for it.

There are *no* disadvantages to adding the through model (except the 1 minute needed to add the through model minor) since 
Django will anyway create the intermediate table to represent the relation so you'll still need to use ``prefetch_related``
to get the toppings of a pizza and avoid the n+1 query problem.

Use a custom user model
-----------------------

Using a custom user model when starting a new project is already `advised in the Django documentation`_. This will make it 
easier to add custom fields to your user model and have better control over it. Also, although you may be able to add
a ``Profile`` model with an one to one relation with the default ``django.auth.User`` model you'll still need to use
a join to retrieve the profile for each user (something that won't be necessary when the extra fields are on your custom user model).
 

There's no real disadvantage to using a custom user model except the 5 minute it is needed to set it up. I actually recommend
create a ``users`` app that you're going to use to keep user related information (see 
the `users app on my cookiecutter project`_).





Views guidelines
================

Template guidelines
===================

Settings guidelines
===================

Debugging guidelines
====================

Be careful when using django-debug-toolbar
------------------------------------------

The `django-debug-toolbar`_ is a great and very popular library that can help you debug your Django application
and identify slow views and n+1 query problems. However I have observed that it makes your development app *much slower*.
For some views I am seeing like 10x decrease in speed i.e instead of 500 ms we'll get more than 5 seconds slower to display
that view! Since Django development (at least for me) is based on a very quick feedback loop, this is a huge problem.

Thus, I recommend to keep it disabled when you are doing normal development and only enable it when you need it, 
for example to identify problematic views.

Use the Werkzeug debugger
-------------------------

Instead of using the traditional runserver to run your app in development 
I recommend installing the django-extensions_ package so as to be able to 
use the Werkzeug debugger. This will enable you to get a python prompt
whenever your code throws an exception or even to add your own breakpoints by throwing exceptions.

More info on my `Django Werkzeug debugger article <{filename}django-debug-developing.rst>`_.


Querying guidelines
===================

The n+1 problem

General guidelines
==================

Consider using a cookiecutter project template
----------------------------------------------

Consider creating (or use an existing) cookiecutter project template. 

Be careful on your selecton of packages/addons
----------------------------------------------


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
.. _`17-year an open issue`: https://code.djangoproject.com/ticket/373
.. _`django-autoslug`: https://github.com/justinmayer/django-autoslug
.. _`django-debug-toolbar`: https://github.com/jazzband/django-debug-toolbar
.. _`django-extensions`: https://github.com/django-extensions/django-extensions
.. _`advised in the Django documentation`: https://docs.djangoproject.com/en/stable/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
.. _`users app on my cookiecutter project`: https://github.com/spapas/cookiecutter-django-starter/tree/master/%7B%7Bcookiecutter.project_name%7D%7D/%7B%7Bcookiecutter.project_name%7D%7D/users

.. _`official website`: https://www.postgresql.org/download/windows/
.. _`zip archives`: https://www.enterprisedb.com/download-postgresql-binaries
.. _`postgres trust authentication page`: https://www.postgresql.org/docs/current/auth-trust.html
.. _`psql reference page`: https://www.postgresql.org/docs/14/app-psql.html`
.. _`this SO issue`: https://stackoverflow.com/questions/20794035/postgresql-warning-console-code-page-437-differs-from-windows-code-page-125
.. _dbeaver: https://dbeaver.io/
.. _`template database`: https://www.postgresql.org/docs/current/manage-ag-templatedbs.html