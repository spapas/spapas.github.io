My essential guidelines for better Django development
#####################################################

:date: 2022-09-28 11:10
:tags: python, django
:category: django
:slug: django-guidelines
:author: Serafeim Papastefanos
:summary: A list of guidelines that I follow in every non-toy Django project I develop


.. contents::


Introduction
============

In this article I'd like to present a list of guidelines I follow when I develop
Django projects, especially projects that are destined to be used in a production
environment for many years. I am using django for more than 10 years as my day to
day work tool to develop applications for the public sector organization I work for.

My organization has got a number of different Django projects that cover its needs, with
some of them running successfully for more than 10 years, since Django 1.4. 


4. trees

	

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

Another very important reason to use a custom user model is that you'll be able to easily add custom methods to your user model. 
For example, there's the ``get_full_name`` method in builtin-Django that returns the first_name plus the last_name, with a space in between
so you're able to call it like ``{{ user.get_full_name }}`` in your templates. If you don't have a custom user model, you'll need to
add template tags for similar functionality; see the discussion about not adding template tags when you can use a method.

There's no real disadvantage to using a custom user model except the 5 minute it is needed to set it up. I actually recommend
create a ``users`` app that you're going to use to keep user related information (see 
the `users app on my cookiecutter project`_).


Views guidelines
================

Use class based views
---------------------

I recommend always using class-based views instead of function-based views. This is because class-based views are easier to
reuse and extend. I've written an extensive `comprehensive Django CBV guide <{filename}django-cbv-tutorial.rst>`_ that you can read to 
learn everything about class based views!

Use slim views
--------------


Template guidelines
===================

Stick to the built-in Django template backend
---------------------------------------------

Django has its own built-in template engine but it also allows you to use the Jinja template engine or even 
use a completely different one! The django template backend is considered "too restrictive" by some people mainly
because you can only call functions without parameters from it.

My opinion is to just stick to the builtin Django template. Its restriction is actually a strength, enabling you
to create re-usable custom template tags (or object methods) instead of calling business logic from the template.
Also, using a completely custom backend means that you'll add dependencies to your project; please see my the guideline 
about the selection of using external packages. Finally, don't forget that any packages you'll use that provide 
templates would be for the Django template backend, so you'll need to convert/re-write these templates to be used with 
a different engine.

I would consider the Jinja engine only if you already have a bunch of Jinja templates from a different project and 
you want to quickly use them.

Don't add template tags when you can use a method
-------------------------------------------------

Continuing from the discussion on the previous guideline, I recommend you to add methods to your models instead of 
adding template tags. For example, let's suppose that we want to get our pizza toppings order by their name. We could
add a template tag that would do that like:

.. code-block:: python 

    def get_pizza_toppings(context, pizza):
        return pizza.toppings.all().order_by('name')

and use it like ``{% get_pizza_toppings pizza as pizza_toppings %}`` in our template. Notice that if you don't care about 
the ordering you could instead do ``{{ pizza.toppings.all }}`` but you need to use the order_by and pass a parameter so you
can't call the method.

Instead of adding the template tag that I recommend  adding a method to your ``pizza`` model like:

.. code-block:: python 

    def get_toppings(self):
        return self.toppings.all().order_by('name')

and then call it like ``{{ pizza.get_toppings }}`` in your template. This is much cleaner and easier to understand.

Please notice that this guideline is not a proposal towards the "fat models" approach. You can add 1 line methods to 
your models that would only call the corresponding service methods if needed. 



Re-use templates with partials
------------------------------

When you have a part of a template that will be used in multiple places you can use partials to avoid repeating yourself.
For example, let's suppose you like to display your pizza details. These details would be displayed in the list of 
pizzas, in the cart page, in the receipt page etc. So can create an html page named ``_pizza_details.html`` under a 
``partial`` folder (or whatever name you want but I recommend having a way to quickly check your partials) with contents
similar to:

.. code-block:: html
    
    <div class='pizza-details'>
        <h3>{{ pizza.name }}</h3>
        {% if show_photo %}
            <img src='{{ pizza.photo.url }}'>
        {% endif %}
        <p>Toppings: {{ pizza.get_toppings|join:", " }}</p>
    </div>

and then include it in your templates like ``{% inlude "pizzas/partials/_pizza_details.html" %}`` to display the info without photo or 
``{% inlude "pizzas/partials/_pizza_details.html" with show_photo=True %}`` to display the photo. Also notice that you can override the 
{{ pizza }} context variable so, if you want to display two pizzas in a template you'll write something like


.. code-block:: html
    
    {% inlude "partials/_pizza_details.html" with show_photo=True pizza=pizza1 %}
    {% inlude "partials/_pizza_details.html" with show_photo=True pizza=pizza2 %}


Settings guidelines
===================

Use a package instead of module
-------------------------------

This is a well known guideline but I'd like to mention it here. When you create a new project, Django will
create a ``settings.py`` file. This file is a python module. I recommend to create a settings folder next to the
``settings.py`` and put
in it the ``settings.py`` renamed as ``base.py`` and an ``__init__.py`` file so the ``settings`` folder will be a 
python package. So instead of ``project\settings.py`` you'll have ``project\settings\base.py`` and ``project\settings\__init__.py``.

Now, you'll add an extra module inside settings for each kind of environment you are gonna use your app on. For example, you'll
have something like 
* ``project\settings\dev.py`` for your development environment
* ``project\settings\uat.py`` for the UAT environment
* ``project\settings\prod.py`` for the production environment

Each of these files will import the ``base.py`` file and override the settings that are different from the base settings, i.e
these files will start like: 

.. code-block:: python

    from .base import *

    # And now all options that are different from the base settings

All these files will be put in your version control. You won't put any secrets in these files. We'll see how to handle
secrets later.

When Django starts, it will by default look for the ``project/settings.py`` module. So, if you try to run ``python manage.py``
now it will complain. To fix that, you have to set the ``DJANGO_SETTINGS_MODULE`` environment variable to point to
the correct settings module you wanna use. For example, in the dev env you'll do ``DJANGO_SETTINGS_MODULE=project.settings.dev``.

To avoid doing that every time I recommend creating a script that will initiate the project's virtual environment and set the 
settings module. For example, in my projects I have a file named dovenv.bat (I use windows) with the following contents:

.. code-block

    call ..\venv\scripts\activate
    set DJANGO_SETTINGS_MODULE=project.settings.dev


Handle secrets properly
-----------------------

Static and media guidelines
===========================

Use ManifestStaticFilesStorage
------------------------------

Django has a ``STATICFILES_STORAGE`` setting that can be used to specify the storage engine that will be used to store
the static files. By default, Django uses the ``StaticFilesStorage`` engine which stores the files in the file system
under the ``STATIC_ROOT`` folder and with a ``STATIC_URL`` url. 

For example  if you've got a ``STATIC_ROOT=/static_root`` and a ``STATIC_URL=/static_url/`` and you've got a file named ``styles.css``
which you include with ``{% static "styles.css" %}``. When you run ``python manage.py collectstatic`` the ``styles.css`` will be copied
to ``/static_root/styles.css`` and you'll be able to access it with ``/static_url/styles.css``.

Please notice that the above should be configured in your web server (i.e nginx). Thus, you need to configure your 
web server so as to publish the files under ``/static_root`` on the ``/static_url`` url. This should work without Django,
i.e if you have configured the web server properly you'll be able to visit ``example.com/static_url/styles.css`` even if
your Django app isn't running. For more info see `how to deploy static files`_.

Now, the problem with the ``StaticFilesStorage`` is that if you change the ``styles.css`` there won't be any 
way for the user's browser to understand that the file has been changed so it will keep using the cached version.

This is why I recommend using the ManifestStaticFilesStorage_ instead. This storage will append the md5 has of each static
file when copying it so the ``styles.css`` will be copied to ``/static_root/styles.fb2be32168f5.css`` and the url will be 
``/static_url/styles.fb2be32168f5.css``. When the ``styles.css`` is changed, its hash will also be changed so the users 
are guaranteed to pick the correct file each time.

Organize your media files
-------------------------

When you upload a file to your app, Django will store it in the ``MEDIA_ROOT`` folder and serve it through ``MEDIA_URL``
similar to the static files as I explained before. The problem with this approach is that you'll end up with a lot of files
in the same folder. This is why I recommend creating a folder structure for your media files. To create this structure
you should set the upload_to_ attribute of ``FileField``. 

So instead of having ``file = models.FileField`` or ``image = models.ImageField`` you'd do something like
``file = models.FileField(upload_to='%Y/%m/files')`` or ``image = models.ImageField(upload_to='%Y/%m/images')`` to
upload these files to their corresponding folder organized by year/month.

Notice that instead of a string you can also pass a function to the ``upload_to`` attribute. This function will need to 
return a string that will contain the path of the uploaded file *including* the filename. For example, an upload_to
function can be similar to this:

.. code-block:: python
    import anyascii

    def custom_upload_path(instance, filename):
        dt_str = instance.created_on.strftime("%Y/%m/%d")
        fname, ext = os.path.splitext(filename)
        slug_fn = slugify(anyascii.anyascii(fname))
        if ext:
            slug_fn += "" + ext
        return "protected/{0}/{1}/{2}".format(dt_str, instance.id, slug_fn)

The above code will convert the filename to an ascii slug (i.e a file named ``δοκιμή.pdf`` will be 
converted to ``dokime.pdf``) and will store it in a folder after the created date year/month/day and id of the
object instance the file belongs to. So if for example the file ``δοκιμή.pdf`` belongs to the object with id 3242
and created date 2022-09-30 will be stored on the directory ``protected/2022/09/30/3242/dokime.pdf``.

The above code is just an example. You can use it as a starting point and modify it to fit your needs. Having the
media files in separate folders will enable you to easily navigate the folder structure and for example back up
only a portion of the files.


Do not serve media through your application server
--------------------------------------------------

This is important. The media files of your app have to be served through your web server (i.e nginx) and *not* your 
application server (i.e gunicorn). This is because the application server has a limited number of workers and if you
serve the media files through them, it will be a bottleneck for your app. Thus you need to configure your web server
to serve the media files by publishing the ``MEDIA_ROOT`` folder under the ``MEDIA_URL`` url similar to the static files
as described above.

Notice that by default Django will only serve your media files for development by using the following at the end of your
``urls.py`` file:

.. code-block:: python

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Under no circumstances you should use this when ``settings.DEBUG = False`` (i.e on production).

Secure your media properly
--------------------------

Continuing from the above, if you are not allowed to serve your media files through your application then how are 
you supposed to secure them? For example you may want to allow a user to upload files to your app but you want only 
that particular user to be able to download them and not anybody else. So you'll need to check somehow that the 
user that tries to download the file is the same user that uploaded it. How can you do that?

The answer is to use a functionality offered by most web servers called X SendFile. First of all I'd like to explain how this works:

1. A user wants to download a file with id ``1234`` so he clicks the "download" button for that file
2. The browser of the user will then visit a normal django view for example ``/download/1234``
3. This view will check if the user is allowed to download the file by doing any permissions checks it needs to do, all in Django code
4. If the user is not allowed to download, it will return a 403 (forbidden) or 404 (not-found) response
5. However if the user is *allowed* to download the Django view will return an http response that *will not* contain the file but will have a special header with the path of the file to download (which is the path that file 1234 is saved on)
6. When the web server (i.e nginx) receives the http response it will check if the response has the special header and if it does it will serve the response it got *along* with the file, directly from the file system without going through the application server (i.e gunicorn)

The above gives us the best of both worlds: We are allowed to do any checks we want in Django and the file is served through nginx.

A library that implements this functionality is django-sendfile2 which is a fork of the non-maintained anymore django-sendfile. 
To use it you'll need to follow the instructions provided and depend on your web server. However, let's see a quick example for
nginx from one production project:

.. code-block:: python

    # nginx conf 

    server {
        # other stuff 

        location /media_project/protected/ {
            internal;
            alias /home/files/project/media/protected/;
        }

        location /media_project/ {
            alias /home/files/project/media/;
        }


    }

For nginx we add a new location block that will serve the files under the ``/media_project/protected/`` url. The ``internal;``
directive will prevent the client from going directly to the URI, so visiting ``example.com/media_project/protected/file.pdf`` directly
will not work. We also have a ``/media_project/`` location that serves the files under /media that are not protected. Please notice that
nginx matches the most specific path first so all files under protected will be matched with the correct, internal location.

.. code-block:: python

    # django settings
    MEDIA_ROOT = "/home/files/project/media"
    SENDFILE_ROOT = "/home/files/project/media/protected"

    MEDIA_URL = "/media_project/"
    SENDFILE_URL = "/media_project/protected"
    SENDFILE_BACKEND = "sendfile.backends.nginx"

Notice the difference between the ``MEDIA_ROOT`` (that contains all our media files - some are not protected) and ``SENDFILE_ROOT``
and same for ``MEDIA_URL`` and ``SENDFILE_URL``

.. code-block:: python 

    # django view 

    def get_document(request, doc_id):
        from django_sendfile import sendfile

        doc = get_object_or_404(Document, pk=doc_id)
        rules_light.require(request.user, "apps.app.read_docs", doc.app)
        return sendfile(request, doc.file.path, attachment=True)

So this view first gets the ``Document`` instance from its id and checks to see if the current user
can read it. Finally, it returns the ``sendfile`` response that will serve the file directly from the file system passing
the ``path`` of that file. This function view will have a url like ``path("get_doc/<int:doc_id>/", login_required(views.get_document), name="get_document", ),``

A final comment is that for your ``dev`` environment you probably want to use the 
``SENDFILE_BACKEND = "django_sendfile.backends.development"`` (please see the settings package guideline on how to 
override settings per env).

Handle stale media
------------------

Django does never delete your media files. For example if you have an object that has a file field and the object is deleted,
the file that this file field refers to will not be deleted. The same is true if you upload a new file on that file field,
the old file will also be kept there! 

This is very problematic in some cases, resulting to GB of unused files in your disk. To handle that, there are two solutions:

* Add a signal in your models that checks if they are deleted or a file field is updated and delete the non-used file. This is implemented by the django-cleanup_ package.
* Use a management command that will periodically check for stale files and delete them. This is implemented by the django-unused-media_ package.

I've used both packages in various projects and they work great. I'd recommend the django-cleanup on greenfield projects so as to avoid stale files from the beginning.




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
.. _ManifestStaticFilesStorage: https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.ManifestStaticFilesStorage\
.. _upload_to: https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.FileField.upload_to
.. _`how to deploy static files`: https://docs.djangoproject.com/en/4.1/howto/static-files/deployment/
.. _django-sendfile2: https://github.com/moggers87/django-sendfile2
.. _django-cleanup: https://github.com/un1t/django-cleanup
.. _django-unused-media: https://github.com/akolpakov/django-unused-media

.. _`official website`: https://www.postgresql.org/download/windows/
.. _`zip archives`: https://www.enterprisedb.com/download-postgresql-binaries
.. _`postgres trust authentication page`: https://www.postgresql.org/docs/current/auth-trust.html
.. _`psql reference page`: https://www.postgresql.org/docs/14/app-psql.html`
.. _`this SO issue`: https://stackoverflow.com/questions/20794035/postgresql-warning-console-code-page-437-differs-from-windows-code-page-125
.. _dbeaver: https://dbeaver.io/
.. _`template database`: https://www.postgresql.org/docs/current/manage-ag-templatedbs.html