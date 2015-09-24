Django model auditing
#####################

:date: 2015-01-21 14:20
:tags: django, python, auditing
:category: django
:slug: django-model-auditing
:author: Serafeim Papastefanos
:summary: Model auditing (who-did-what) with Django

.. contents::

Introduction
============

An auditing trail is a common requirement in most non-trivial applications. Organizations
need to know *who* did the change, *when* it was done and *what* was actually changed.
In this post we will see three
different solution in order to add this functionality in Django: doing it ourselves,
using django-simple-history and using django-reversion. 

*Update 24/09/2015:* Added a paragraph describing the django-reversion-compare which is
a great addon for django-reversion that makes finding differences between versions a breeze!

Adding simple auditing functionality ourselves
==============================================

A simple way to actually do auditing is to keep four extra fields in our models:
``created_by``, ``created_on``, ``modified_by`` and ``modified_on``. The first two
will be filled when the model instance is created while the latter two will be
changed whenever the model instance is saved. So we only have *who* and *whe*.
Sometimes, these are enough so let's see how easy it is to implement it in django.

We'll need an abstract model that could be used as a base class for models that need auditing:

.. code-block:: python

    from django.conf import settings
    from django.db import models

    class Auditable(models.Model):
        created_on = models.DateTimeField(auto_now_add = True)
        created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_by')

        modified_on = models.DateTimeField(auto_now = True)
        modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='modified_by')

        class Meta:
            abstract = True


Models inheriting from ``Auditable`` will contain their datetime of creation and modification
which will be automatically filled using the very usefull ``auto_now_add_`` (which will
set the current datetime when the model instance is created) and ``auto_now_`` (which will
set the current datetime when the model instance is modified).

Such models will also have two foreign keys to ``User``, one for the user
that created the and one of the user that modified them. The problem with these two fields
is that they cannot be filled automatically (like the datetimes) because the user that
actually did create/change the objects must be provided!

Since I am really fond of CBVs I will present a simple mixin that can be used with CreateView
and UpdateView and does exactly that:

.. code-block:: python

    class AuditableMixin(object,):
        def form_valid(self, form, ):
            if not form.instance.created_by:
                form.instance.created_by = self.request.user
            form.instance.modified_by = self.request.user
            return super(AuditableMixin, self).form_valid(form)


The above mixin overrides the ``form_valid`` method of ``CreateView`` and ``UpdateView``:
First it checks if the object is created (if it is created it won't be saved in the
database yet thus it won't have an id) in order to set the ``created_by`` attribute to
the current user. After that it will set the ``modified_by`` attribute of the object to
the current user. Finally, it will call the next ``form_valid`` method to do whatever
is required (save the model instance and redirect to ``success_url`` by default).

The views using ``AuditableMixin`` should allow only logged in users (or else an
exception will be thrown). Also, don't forget to exclude the ``created_by`` and ``modified_by``
fields from your model form (``created_on`` and ``modified_on`` will automatically be
excluded).


Example
=======

Let's see a simple example of creating a small django application using the previously defined abstract model and mixin:

models.py
---------

.. code-block:: python

    from django.conf import settings
    from django.core.urlresolvers import reverse
    from django.db import models

    from auditable.models import Auditable


    class Book(Auditable):
        name = models.CharField(max_length=128)
        author = models.CharField(max_length=128)

        def get_absolute_url(self):
            return reverse("book_list")

In the above we suppose that the ``Auditable`` abstract model is imported from the
``auditable.models`` module and that a view named ``book_list`` that shows all books exists.

forms.py
---------

.. code-block:: python

    from django.forms import ModelForm


    class BookForm(ModelForm):
        class Meta:
            model = Book
            fields = ['name', 'author']

Show only ``name`` and ``author`` fields (and not the auditable fields) in the ``Book ModelForm``.

views.py
--------

.. code-block:: python

    from django.views.generic.edit import CreateView, UpdateView
    from django.views.generic import ListView

    from auditable.views import AuditableMixin

    from models import Book
    from forms import BookForm


    class BookCreateView(AuditableMixin, CreateView):
        model = Book
        form_class = BookForm


    class BookUpdateView(AuditableMixin, UpdateView):
        model = Book
        form_class = BookForm


    class BookListView(ListView):
        model = Book

We import the ``AuditableMixin`` from ``auditable.views`` and make our Create and Update views
inherit from this mixin also in addition to ``CreateView`` and ``UpdateView``. Pay attention that our
mixin is placed *before* CreateView in order to call ``form_valid`` in the proper order: When multiple
inheritance is used like this python will check each class from left to right to find the proper method
and call it. For example, in our ``BookCreateView``, when the ``form_valid`` method is called, python
will first check if ``BookCreateView`` has a ``form_valid`` method. Since it does not, it will check
if ``AuditableMixin`` has a ``form_valid`` method and call it. Now, we are calling the ``super(...).form_valid()`` in the
``AuditableMixin`` ``form_valid``, so the ``form_valid`` of ``CreateView`` will *also* be called.

A simple ``ListView`` is also added to just show the info on all books.


urls.py
-------

.. code-block:: python

    from django.conf.urls import patterns, include, url

    from views import BookCreateView, BookUpdateView, BookListView

    urlpatterns = patterns('',
        url(r'^accounts/login/$', 'django.contrib.auth.views.login', ),
        url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', ),

        url(r'^create/$', BookCreateView.as_view(), name='create_book'),
        url(r'^update/(?P<pk>\d+)/$', BookUpdateView.as_view(), name='update_book'),
        url(r'^$', BookListView.as_view(), name='book_list'),
    )

Just add the previously defined Create/Update/List views along with a login/logout views.

templates
---------

You'll need four templates:

* books/book_list.html: Show the list of books
* books/book_form.html: Show the book editing form
* registration/login.html: Login form
* registration/logout.html: Logout message


Using django-simple-history
===========================
django-simple-history_  can be used to not only store the user and date of each modification
but a different version for each modification. To do that, for every model that is registered
to be used with django-simple-history, it wil create a second table in
the database hosting all versions (historical records) of that model. As we can understand this is really powerfull
since we can see exactly what was changed and also do normal SQL queries on that!

Installation
------------

To use django-simple-history in a project, after we do a ``pip install django-simple-history``,
we just need to add it to ``INSTALLED_APPS`` and
add the ``simple_history.middleware.HistoryRequestMiddleware`` to the ``MIDDLEWARE_CLASSES`` list.

Finally, to keep the historical records for a model, just add an instace of ``HistoricalRecords`` to this model.

Example
-------

For example, our previously defined ``Book`` model will be modified like this:

.. code-block:: python
    import reversion


    class SHBook(models.Model):
        name = models.CharField(max_length=128)
        author = models.CharField(max_length=128)

        def get_absolute_url(self):
            return reverse("shbook_list")

        history = HistoricalRecords()

When we run ``python manage.py makemigrations`` and ``migrate`` this, we'll see that beyond the table for SHBook, a table for HistoricalSHBook will be created:

.. code::

    Migrations for 'sample':
      0002_historicalshbook_shbook.py:
        - Create model HistoricalSHBook
        - Create model SHBook

Let's see the schema of historicalshbook:

.. code::

    CREATE TABLE "sample_historicalshbook" (
        "id" integer NOT NULL,
        "name" varchar(128) NOT NULL,
        "author" varchar(128) NOT NULL,
        "history_id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        "history_date" datetime NOT NULL,
        "history_type" varchar(1) NOT NULL,
        "history_user_id" integer NULL REFERENCES "auth_user" ("id")
    );


So we see that it has the *same* fields as with ``SHBook`` (``id, name, author``) with the addition of
the primary key (``history_id``) of this historical record, the date and user that did the change
(``history_date``, ``history_user_id``) and the type of the record (created / update / delete).

So, just by adding a ``HistoricalRecords()`` attribute to our model definition we'll get complete auditing
for the instance of that model

Usage
-----

To find out information about the historical records we'll just use the ``HistoricalRecords()`` attribute
of that model:

For example, running ``SHBook.history.filter(id=1)`` will return all historical records of the book with
``id = 1``. For each one of them we have can use the following:

* get the user that made the change through the ``history_user`` attribute
* get the date of the change through the ``history_date`` attribute
* get the type of the change through the ``history_type`` attribute (and the corresponding ``get_history_type_dispaly``)
* get a model instance as it was then through the ``history_object`` attribute (in order to ``save()`` it and revert to this version)

Using django-reversion
======================

django-reversion_  offers more or less the same functionality of django-simple-history by following a different philosophy:
Instead of creating an extra table holding the history records for each model, it insteads converts all the fields of each model
to json and stores that JSON in the database in a text field.

This has the advantage that no extra tables are created to the database but the disadvantage that you can't easily query
your historical records. So you may choose one or the other depending on your actual requirements.

Installation
------------

To use django-reversion in a project, after we do a ``pip install django-reversion``,
we just need to add it to ``INSTALLED_APPS`` and
add the ``reversion.middleware.RevisionMiddleware`` to the ``MIDDLEWARE_CLASSES`` list.

In order to save the revisions of a model, you need to register this model to django-reversion. This can be
done either through the django-admin, by inheriting the admin class of that model from ``reversion.VersionAdmin``
or, if you don't want to use the admin by ``reversion.register`` decorator.

Example
-------

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
* revert to that previous version of that object using the ``revert()`` method

Comparing versions with django-reversion-compare
------------------------------------------------

A great addon for django-version is django-reversion-compare_ which helps you find out differences
between versions of your objects. When you use django-reversion-compare, you'll be able to select
two (different) versions of your object and you'll be presented with a list of all the differences
found in the fields of that object between the two versions. The diff algorithm is smart, so you'll
be able to easily recognise the changes. 

To use django-reversion-compare, after installing it you should just inherit your admin views from 
``reversion_compare.admin.CompareVersionAdmin`` (instead of ``reversion.VersionAdmin``) and you'll
get the reversion-compare views instead of reversion views in the admin for the history of the object.

Also, in case you need to give access to normal, non-admin users to the history of an object (this is
useful for auditing reasons), you can use the ``reversion_compare.views.HistoryCompareDetailView``
as a normal ``DetailView`` to create a non-admin history and compare diff view.


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


.. _auto_now: https://docs.djangoproject.com/en/1.7/ref/models/fields/#django.db.models.DateField.auto_now
.. _auto_now_add: https://docs.djangoproject.com/en/1.7/ref/models/fields/#django.db.models.DateField.auto_now_add
.. _django-simple-history: https://github.com/treyhunner/django-simple-history
.. _django-reversion: https://github.com/etianen/django-reversion
.. _django-reversion-compare: github.com/jedie/django-reversion-compare
