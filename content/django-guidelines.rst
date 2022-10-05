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
some of them running successfully for more than 10 years, since Django 1.4. I have
been involved in the development of all of them, and I have learned a lot from them.

I am not saying that these are the only guidelines that you should follow, but they
are the ones that I follow and I believe that they are good enough to be shared.
	

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


Think of your models as database tables
---------------------------------------

Your models should be designed as database tables. They should have proper data types,
relations, indeces and constraints. Your mindset must be of designing a database not only writing 
Python code.

Don't de-normalize your data (i.e by using JSONField or ArrayField) unless you *know* that you
need to do that. 


Views guidelines
================

Use class based views
---------------------

I recommend always using class-based views instead of function-based views. This is because class-based views are easier to
reuse and extend. I've written an extensive `comprehensive Django CBV guide <{filename}django-cbv-tutorial.rst>`_ that you can read to 
learn everything about class based views!

View method overriding guidelines
---------------------------------

It is important to know which method you need to override to add functionality to your class based views. You can
use the excellent `CBV Inspector`_ app to understand how each CBV is working. Also, I've got
many examples in my `comprehensive Django CBV guide <{filename}django-cbv-tutorial.rst>`_.

Some quick guidelines follow:

* For *all* methods do not forget to call the parent's method by ``super()``. 
* Override ``dispatch(self, request, *args, **kwargs)`` if you want to add functionality that is executed before any other method. For example to add permission checks or add some attribute (``self.foo``) to your view instance. This method will *always* run on both HTTP GET/POST or whatever. Must return a Response object (i.e ``HttpResponse``, ``HttpResponseRedirect``, ``HttpResponseForbidden`` etc)
* You should rarely need to override the ``get`` or ``post`` methods of your CBVs since they are called directly after ``dispatch`` so any code should be there.
* To add extra data in your context (template) override ``get_context_data(self, **kwargs)``. This should return a dictionary with the context data.
* To pass extra data to your form (i.e the current request) override ``get_form_kwargs(self)``. This data will be passed on the ``__init__`` of your form, you need to *remove it* by using something like ``self.request = kwargs.pop('request')`` before calling ``super().__init(*args, **kwargs)``
* To override the initial data of your form override ``get_form_initial(self)``. This should return a dictionary with the initial data.
* You can override ``get_form(self, form_class=None)`` to use a configurable form instance or ``get_form_class(self)`` to use a configurable form class. The form instance will be generated by ``self.get_form_class()(**self.get_form_kwargs())`` (notice that the kwargs will contain an ``initial=self.get_form_initial()`` value)
* To do stuff after a valid form is submitted you'll override ``form_valid(self, form)``. This should return an ``HttpResponse`` object and more specifically an ``HttpResponseRedirect`` to avoid double form submission. This is the place where you can also add flash messages to your responses.
* You can also override ``form_invalid(self, form)`` but this is rarely useful. This should return a normal response (not a redirect)
* Override ``get_success_url(self)`` if you only want to set where you'll be redirected after a valid form submission (notice this is used by ``form_valid``)
* You can use a different template based on some condition by overriding ``get_template_names(self)``. This is useful to return a partial response on an ajax request (for example the same detail view will return a full html view of an object when visited normally but will return a small partial html with the object's info when called through an ajax call)
* For views that return 1 or multiple objects (``DetailView, ListView, UpdateView`` etc) you almost always need to override the ``get_queryset(self)`` method, *not* the ``get_object``. I'll talk about that a little more later.
* The ``get_object(self, queryset=None)`` method will use the queryset returned by ``get_queryset`` to get the object based on its pk, slug etc. I've observed that this rarely needs to be overridden since most of the time overriding ``get_queryset`` will suffice. One possible use case for overriding ``get_object`` is for views that don't care at all about the queryset; for example you may implement a ``/profile`` detail view that will pick the current user and display some stuff. This can be implemented by a ``get_object`` similar to ``return self.request.user``. 

Use slim views
--------------

Try to avoid putting business logic in your views. This is because views are hard to test and hard to reuse. There are two places
you can put your business logic instead. Either in your models (fat models) or in some other service-module (this will be simple
functions or classes).



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

Cache your templates in production
----------------------------------

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

You should never put secrets (i.e your database password or API KEYS) on your version control. There are two
ways that can be used to handle secrets in Django: 

* Use a ``settings/local.py`` file that contains all your secrets for the current environment and is not under version control.
* Use environment variables.

For the ``settings/local.py`` solution, you'll add the following code at the end of each one of your settings environment
modules (i.e you should put it at the end of ``dev.py``, ``uat.py``, ``prod.py`` etc):

.. code-block:: python

    try:
        from .local import *
    except ImportError:
        pass


The above will try to read a module named ``local.py`` and if it exists it will import it. If it doesn't exist it will
just ignore it. Because this file is at the end of the corresponding settings module, it will override any settings that are already
defined. The above file should be excluded from version control so you'll add the line ``local.py`` to your ``.gitignore``.

Notice that the same solution to store secrets can be used if you don'tt use the settings package approach but you have a ``settings.py``
module. Create a ``settings_local.py`` module and import from that at the end of your settings module instead. However I strongly
recommend to use the settings package approach.

To catalogue my secrets, I will usually add a ``local.py.template`` file that has all the settings that I need to override in my
local.py with empty values. I.e it will may be similar to:

.. code-block:: python

    API_TOKEN=''
    ANOTHER_API_TOKEN=''
    DATABASES_U = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

Then I'll copy over ``local.py.template`` to ``local.py`` when I initialize my project and fill in the values.

Before continuing, it is important to understand the priority of the settings modules. So let's suppose we are on
production. We should have a ``DJANGO_SETTINGS_MODULE=project.settings.prod``. The players will be ``base.py``, 
``prod.py`` and ``local.py``. The priority will be 

1. ``local.py``
2. ``prod.py``
3. ``base.py``

So any settings defined in ``prod.py`` will override the settings of ``base.py``. And any settings defined in ``local.py``
will override any settings defined either in ``prod.py`` or ``base.py``. Please notice that I mention *any* setting, not 
just secrets.

To use the environment variables approach, you'll have to read the values of the secrets from your environment. 
A simple way to do that is to use ths os.getenv function, for example in your ``prod.py`` you may have something like:

.. code-block:: python

    import os 

    API_TOKEN = os.getenv('API_TOKEN')

This will set ``API_TOKEN`` setting to ``None`` if the ``API_TOKEN`` env var is not found. You can do something like
``os.environ["API_TOKEN"]`` instead to throw an exception. Also, there are libraries that will help you with this 
like python-dotenv_, However I can't really recommend them because I haven't used them. 

Now, which one to use? My recommendation (and what I always do) is to use the first approach (``local.py``) *unless* you need to use 
environment variables to configure your project. For example, if you are using a PaaS like Heroku, you'll have to use
environment variables because of the way you deploy so you can't really choose. However using the ``local.py`` is much
simpler, does not have any dependencies and you can quickly understand which settings are overriden. Also you can 
use it to override *any* setting by putting it in your local.py, not just secrets. 

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

Avoid the n+1 problem
---------------------

The most common Django newbie mistake is not considering the n+1 problem when writing your queries.

Because Django automatically follows relations it is very easy to write code that will result in the n+1 queries
problem. A simple example is having something like 

.. code-block:: python

    class Category(models.Model):
        name = models.CharField(max_length=255)

    class Product(models.Model):
        name = models.CharField(max_length=255)
        category = models.ForeignKey(Category, on_delete=models.CASCADE)

        def __str__(self):
            return "{0} ({1})".format(self.name, self.category.name)

and doing something like:

.. code-block:: python

    for product in Product.objects.all():
        print(product)

or even having ``products = Product.objects.all()`` as a context variabile in your template:

.. code-block:: html

    {% for product in products %}
        {{ product }}
    {% endfor %}

If you've got 100 products, the above will run 101 queries to the database: The first one
will get all the products and the other 100 will return each product's category one by one!
Consider what may happen if you had thousands of products...

To avoid this problem you should add the ``select_related``, so ``products = Product.objects.all().select_related('category')``.
This will do an SQL JOIN between the products and categories table so each product will include its category instance. Now, when
you've got a many to many relation the situation is a little different. Let's suppose you've got a ``tags = models.ManyToManyField(Tag)`` 
field in your ``Product`` model. If you wanted to do something like ``{{ product.tags.all|join:", " }}`` to display the product tags you'd
also get a n+1 situation because Django will do a query for each product to get its tags. To avoid this you cannot use 
``select_related`` but should use the ``prefetch_related``
method so ``products = Product.objects.all().prefetch_related('tags')``. This will result in 2 queries, one for 
products and one for their tags, the joining will be done in python. 

One final comment about the ``prefetch_related`` is that you must be very careful to use what you prefetch. Let's suppose that we
had prefeched the tags but we wanted to display them ordered by name: Doing this ``", ".join([tag for tag in product.tags.all().order_by('name')])``
will *not* use the prefetched tags but will do a new query for each product to get its tags resulting in the n+1 problem! Django has
``tag.objects.all()`` for each product, *not* ``tag.objects.all().order_by('name')``. To fix that you need to use `Prefetch` like this:

.. code-block:: html
    from django.db.models import Prefetch

    Product.objects.prefetch_related(Prefetch('tags', queryset=Tag.objects.order_by('name')))

The same is true if you wanted to filter your tags etc.

Now, one thing to understand is that this behavior of Django is intentional. Instead of automatically following the relationships,
Django could throw an exception when you tried to follow a relationship that wasn't in a ``select_related``
(this how it works in other frameworks). The disadvantage 
of this is that it would make Django *more difficult* to use for new users. Also, there are cases that the n+1 problem isn't 
really a big deal, for example you may have a DetailView fetching a single object so in this case the n+1 problem will be 1+1
and wouldn't really matter. So, at least for Django, it's a case of premature optimization: Write your queries as good as you
can (but keep in mind the n+1 problem), if you miss some cases that actually make your views slow, you can easily optimize them later.



Learn to use the Django ORM
---------------------------

The Django ORM is a very powerful tool that can help you write very complex queries. Before some years
I was sometimes need to use raw SQL queries in my Django projects, however nowadays I never need to 
since the Django ORM has all the SQL features I need. 

So, if you want to use a raw SQL query, please think twice and research the possibility that this is possible 
through the Django ORM instead.

Re-use your queries
-------------------

You should re-use your queries to avoid re-writing them. You can either put them inside your models
(as instance methods) or in a mixin for the queries of your views or even add a new manager for
your model. Let's see some examples:

Let's suppose I wanted to get the tags of my product: I'd add this method to my ``Product`` model:

.. code-block:: python

    class Product(models.Model):
        # ...

        def get_tags(self):
            return self.tags.all().order_by('name')

Please notice that if you haven't used a proper prefetch this will result in the n+1 queries problem. See the discussion above
for more info. To get the products with their tags I could add a new manager like:

.. code-block:: python

    class ProductWithTagManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().prefetch_related(Prefetch('tags', queryset=Tag.objects.order_by('name')))

    class Product(models.Model):
        # ...

        products_with_tags = ProductWithTagManager()

Now I could do ``[p.get_tags() for p in Product.products_with_tags.all()]`` and not have a n+1 problem.

Actually, if I knew that I would *always* wanted to display the product's tags I could override the default manager like

.. code-block:: python

    class Product(models.Model):
        # ...

        objects = ProductWithTagManager()

However I would not recommend that since having a consistent behavior when you run Model.objects is very important. If you
are to modify the default manager then you'll need to always remember what your default manager does. This is very problematic
in old projects and when you want to quickly query your database from a shell. Also, even more problematic is if you 
override your default manager to *filter* (hide) objects. Don't do that or you'll definitely regret it.


The other query re-use option is through a mixin that would override the ``get_queryset`` of your models. This is mainly for 
permission purpopses. Let's suppose that each user can only see his products: I could add a mixin like:

.. code-block:: python

    class ProductPermissionMixin:
        def get_queryset(self):
            return super().get_queryset().filter(created_by=self.request.user)


Then I could inherit my ``ListView, DetailView, UpdateView`` and ``DeleteView`` i.e ``ProductListView(ProductPermissionMixin, ListView)`` from that mixin and I'd have a consistent behavior on
which products each user can view. More on this can be found on my 
`comprehensive Django CBV guide <{filename}django-cbv-tutorial.rst>`_.

Forms guidelines
================

Always use django-forms
-----------------------

This is a no-brainer: The django-forms offers some great class-based functionality for your forms. I've
seen people creating html forms "by hand" and missing all this. Don't be that guy; use django-forms!

I understand that sometimes the requirements of your forms may be difficult to be implemented with 
a django form and you prefer to use a custom form. This may seem fine at first but in the long run
you're gonna need (and probably re-implement) most of the django-forms capabilities. So, do it from the
start.

Overriding Form methods guidelines
----------------------------------

Your ``CustomForm`` inherits from a Django ``Form`` so you can override some of its methods. Which ones
should you override? 

* The most usual method for overriding is ``clean(self)``. This is used to add your own server-side checks to the form. I'll talk a bit more about overriding clean later.
* The second most usual to override is ``__init__(self, *args, **kwargs)``. You should override it to "pop"
  any extra kwargs from the ``kwargs`` dict *before* calling ``super().__init__(*args, **kwargs)``. See the view method overriding guidelines for more info. Also you'll use it to
  change.
* I usually *avoid* overriding the form's ``save()`` method. The ``save()`` is almost always called from the view's ``form_valid`` method so I prefer to do any extra stuff from the view. This is mainly a personal preference in order to avoid having to hop between the form and view modules; by knowing that the form's save is always the default the behavior will be consistent. This is personal preference though.

There shouldn't be a need to override any other method of a ``Form`` or ``ModelForm``. However please notice that you can easily
use mixins to add extra functionality to your forms. For example, if you had a particular check that would be called from *many* forms,
you could add a 

.. code-block:: python

    class CustomFormMixin:
        def clean(self):
            super().clean() # Not really needed here but I recommend to add it to keep the inheritance chain
            # The common checks that does the mixin

    class CustomForm(CustomFormMixin, Form):
        # Other stuff

        def clean(self):
            super().clean() # This will run the mixin's clean
            # Any checks that only this form needs to do 


Proper cleaning
---------------

When you override the ``clean(self)`` method of a ``Form`` you should always use the ``self.cleaned_data`` to check the
data of the form. The common way to mark errors is to use the ``self.add_error`` method, for example, if you have a 
``date_from`` and ``date_to`` and date_from is after the ``date_to`` you can do your clean something like this:

.. code-block:: python

    def clean(self):

        date_from = self.cleaned_data.get("date_from")
        date_to = self.cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            error_str = "Date from cannot be after date to"
            self.add_error("date_from", error_str)
            self.add_error("date_from", error_str)

Please notice above that I am checking that both ``date_from`` and ``date_to`` are not null (or else it will try to compare
null dates and will throw). Then I am adding the same error message to both fields. Django will see that the form has errors
and run ``form_invalid`` on the view and re-display the form with the errors.

Beyond the ``self.add_error`` method that adds the error to the field there's a possibility to add an error to the "whole"
form using:

.. code-block:: python

    from django.core.exceptions import ValidationError

    def clean(self):
        if form_has_error:
            raise ValidationError(u"The form has an error!")

This kind of error won't be correlated with a field. You can use this approach when an error is correlated to multiple fields
instead of adding the same error to multiple fields. 

You must be very careful because if you are using a non-standard
form layout method (i.e you enumerate the fields) you also need to display the ``{{ form.errors }}`` in your template or else
you'll get a rejected form without any errors! This is a very common mistake.

Another thing to notice is that when your clean method raises it will display only the first such error. So if you've got multiple
checks like:

.. code-block:: python

    def clean(self):
        if form_has_error:
            raise ValidationError(u"The form has an error!")
        if form_has_another_error:
            raise ValidationError(u"The form has another error!")

and your form has *both* errors only the 1st one will be displayed to the user. Then after he fixes it he'll also see the 2nd one. When
you use ``self.add_error`` the user will get both at the same time.

Overriding the __init__
-----------------------

You can override the ``__init__`` method of your forms for three main reasons:

Retrieve the request or user from the view:

.. code-block:: python

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

Please notice that we must pop the ``request`` from the ``kwargs`` dict before calling ``super().__init__``. 

Override some field attributes on a ModelForm. A Django ModelForm will automatically create a field for each model field. 
Some times you may want to override some of the attributes of the field. For example, you may want to change the label of the field
or make a field required. To do that, you can do something like:

.. code-block:: python

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["my_field"].label = "My custom label" # Change the label
        self.fields["my_field"].help_text = "My custom label" # Change the help text
        self.fields["my_field"].required = True # change the required attribute
        self.fields["my_field"].queryset = Model.objects.filter(is_active=True) # Only allow specific objects for the forein key

Please notice that we need to use ``self.fields["my_field"]`` *after* we call ``super().__init__(*args, **kwargs)``.

Add functionality related to the current user/request. For example, you may want to add a field that is only editable if
the user is superuser:

    .. code-block:: python

        def __init__(self, *args, **kwargs):
            self.request = kwargs.pop("request", None)
            super().__init__(*args, **kwargs)
            if not self.request.user.is_superuser:
                self.fields["my_field"].widget.attrs['readonly'] = True


Laying out forms
----------------

To lay out the forms I recommend using a library like django-crispy-forms_. This integrates your forms properly with your 
front-end engine and helps you have proper styling. I've got some more info on 
`form layout post <{filename}django-crispy-form-easy-layout.rst>`_

Improve the formset functionality
---------------------------------

Beyond simple forms, Django allows you to use a functionality it calls formsets_. A formset is a collection of forms that
can be used to edit multiple objects at the same time. This is usually used in combination with inlines which are a 
way to edit models on the same page as a parent model. 
For example you may have something like this:

.. code-block:: python

    class Pizza(models.Model):
        name = models.CharField(max_length=128)
        toppings = models.ManyToManyField('Topping', through='PizzaTopping')

    class Topping(models.Model):
        name = models.CharField(max_length=128)
    
    class PizzaTopping(models.Model):
        amount = models.PositiveIntegerField()
        pizza = models.ForeignKey('Pizza')
        topping = models.ForeignKey('Topping')

Now we'd like to have a form that allows us to edit a pizza by both changing the pizza name *and* the toppings of the pizza 
along with their amounts. The pizza form will be the main form and the topping/amount will be the inline form. Notice that we
won't also create/edit the topping name, we'll just select it from the existing toppings (we're gonna have a completely different
view for adding/editing individual toppings).

First of all, to create a class based view that includes a formset we can use the django-extra-views_
package (this isn't supported by built-in django CBVs unless we implement the functionality ourselves). Then we'd do something
like:

.. code-block:: python

    from extra_views import CreateWithInlinesView, InlineFormSetFactory


    class ToppingInline(InlineFormSetFactory):
        model = Topping
        fields = ['topping', 'amount']


    class CreatePizzaView(CreateWithInlinesView):
        model = Pizza
        inlines = [ToppingInline]
        fields = ['name']

This will create a form that will allow us to create a pizza and add toppings to it. Now, to display the formset we'd 
modify our template to be similar to:

.. code-block:: html 

    <form method="post">
    ...
    {{ form }}

    {% for formset in inlines %}
        {{ formset }}
    {% endfor %}
    ...
    <input type="submit" value="Submit" />
    </form>

This works however it will be very ugly. The default behavior is to display the ``Pizza`` form and three empty ``Topping`` forms.
If we want to add more toppings we'll have to submit that form so it will be saved and then edit it. But once again we'll get our
existing toppings and three more. I am not fond of this behavior.

That's why my recommendation is to follow the instructions on my 
`better django inlines <{filename}better-django-inlines.rst>`_ article that allows you to sprinkle some javascript on your
template and get a much better, dynamic behavior. I.e you'll get an "add more" button to add extra toppings without the need t
submit the form every time.


General guidelines
==================

Consider using a cookiecutter project template
----------------------------------------------

If you are working on a Django shop so you need to create frequenctly new Django apps I'd recommend to 
consider creating (or use an existing) cookiecutter_ project template. You can use `my own cookiecutter`_
to create your projects or as an inspiration to create your own. It follows all the conventions I mention in
this post and it is very simple to use.

Be careful on your selection of packages/addons
-----------------------------------------------

Django, because of its popularity, has an `abudance of packages/addons`_ that can help you do almost anything. 
However, my experience has taught me that you should be very careful and do your research before adding a new 
package to your project. I've been left many times with projects that I was not able to upgrade because they 
heavily relied on functionality from an external package that was abandoned by its creator. I also have lost 
many hours trying to debug a problem that was caused by a package that was not compatible with the latest version
of Django.

So my guidelines before using an external Django addon are:

* Make sure that it has been upgraded recently. There are *no* finished Django addons. Django is constantly evolving by releasing new versions and that must be true for the addons. Even if the addons are compatible with the new Django version they need to denote that in their README so as to know that their maintainers care.
* Avoid using very new packages. I've seen many packages that are not yet mature and they are not yet ready for production. If you really need to use such a package make sure that you understand what it does and you can fix problems with the package if needed.
* Avoid using packages that rely heavily on Javascript; this is usually better to do on your own.
* Try to understand, at least at a high level, what the package does. If you don't understand it, you will not be able to debug if it breaks.
* Make sure that the package is well documented and that it has a good test coverage.
* Don't use very simple packages that you can easily implement yourself. Don't be a left-pad developer.

I already propose some packages in this article but I also like to point you out to my 
`Django essential package list <{filename}django-essential-packages.rst>`_. This list was compiled 5 years ago and 
I'm happy to still recommend *all* of these packages with the following minor changes:

* Nowadays I recommend using wkhtmltopdf for creating PDFs from Django instead of xhtml2pdf. Please see my `PDFs in Django like it's 2022 <{filename}pdfs-in-django-2022.rst>`_ article for more info. Notice that there's nothing wrong with the xhtml2pdf package, it still works great and is supported but my personal preference is to use the wwhtmltopdf.
* The django-sendfile is no longer supported so you need to use django-sendfile2_ instead. This is a drop-in replacement from django-sendfile2. See the point about media securing for more info.
* django-auth-ldap_ uses github now (nothing changed, it just uses github instead of bitbucket).

The fact that from a list of ~30 packages only one (django-sendfile) is no longer supported 
(and the fact that even for that there's a drop-in replacement) is 
a testament to the quality of the Django ecosystem (and to my choosing capabilities).

In addition to the packages of my list, this article already contains a bunch of packages 
that I've used in my projects and I am happy with them so I'd also recommend them to you.


Don't be afraid to use threadlocals
-----------------------------------

One controversial aspect if Django is that it avoids using the threadlocals functionality. The `thread-local data`_ is a
way to store data that is specific to the current running thread. This, combined with the fact that each one of the
requests to your Django app *will be served by the same thread* (worker) gives you a super powerful way to store and then
access data that is specific to the current request and would be very difficult (if at all possible) to do it otherwise.

The usual way to work with thread locals in Django is to add a middleware that sets the current request in the thread local
data. Then you can access this data from wherever you want in your code, like a global. You can either create that middleware
yourself but I'd recommend using the django-tools_ library for adding this functionality. You'll add the 
``'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware'`` to your list of middleware (at the end of the listt 
unless you want to use the current user from another middleware) and then you'll use it like this:

.. code-block:: python

    from django_tools.middlewares import ThreadLocal

    # Get the current request object:
    request = ThreadLocal.get_current_request()
    # You can get the current user directly with:
    user = ThreadLocal.get_current_user()

Please notice that Django recommends avoiding this technique because it hides the request/user dependency and makes
testing more difficult. However I'd like to respectfully disagree with their rationale.

* First of all, please notice that this is exactly how `Flask works`_ when you access the current request. It stores the request in the thread locals and then you can access it from anywhere in your code.
* Second, there are things that are very difficult (or even not possible) without using the threadlocals. I'll give you an example in a little.
* Third, you can be careful to use the thread locals functionality properly. After all it is a very simple concept. The fact that you are using thread locals can be integrated to your tests.

One example of why thread locals are so useful is this abstract class that I use in almost all my projects and models:

.. code-block:: python

    class UserDateAbstractModel(models.Model):
        created_on = models.DateTimeField(auto_now_add=True, )
        modified_on = models.DateTimeField(auto_now=True)

        created_by = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.PROTECT,
            related_name="%(class)s_created",
        )
        modified_by = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.PROTECT,
            related_name="%(class)s_modified",
        )

        class Meta:
            abstract = True

        def save(self, *args, **kwargs):
            user = ThreadLocal.get_current_user()
            if user:
                if not self.pk:
                    self.created_by = user

                self.modified_by = user
            super(UserDateAbstractModel, self).save(*args, **kwargs)

Models that override this abstract model will automatically set the ``created_by`` and ``modified_by`` fields to the current user. This works
the same no matter if I edit the object from the admin, or from a view. To use that functionality all I need to do is to inherit from that model i.e
``class MyModel(UserDateAbstractModel)`` and that's it.

What would I need to do if I didn't use the thread locals? I'd need to create a mixin from which *all my views* (that modify an object) 
would inherit! This mixin would pick the current user from the request and set it up. Please consider the difference between these two approaches;
using the model based approach with the thread locals I can be assured that no matter where I modify an object, the ``created_by`` and ``modified_by``
will be set properly (unless of course I modify it through the database or django shell -- actually, I could make ``save`` throw if 
the current use hasn't been setup so it wouldn't be possible to modify from the shell). If I use the mixin approach, I need to make sure that
all my views inherit from that mixin and that I don't forget to do it. Also other people that add code to my project will also need to 
remember that. This is a lot more error prone and difficult to maintain.

The above is a *simple* example. I have seen many more cases where without the use of thread locals I'd need to replicate 3-4 classes 
from an external library (this library was django-allauth for anybody interested) in order to be able to pass through the current user
to where I needed to use this. This is a lot of code duplication and a maintenance hell.

One final comment: I'm not recommending to do it like Flask, i.e use thread locals anywhere. For example, in your views and forms it is
easy to get the current request, there's no need to use thread locals there. However, in places where there's no simple path for
accessing the current user then definitely use thread locals and don't feel bad about it!




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
.. _`thread-local data`: https://docs.python.org/3/library/threading.html#thread-local-data
.. _`Flask works`: https://flask.palletsprojects.com/en/2.2.x/reqcontext/
.. _django-tools: https://github.com/jedie/django-tools/
.. _`CBV Inspector`: https://ccbv.co.uk/
.. _python-dotenv: https://github.com/theskumar/python-dotenv
.. _cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`my own cookiecutter`: https://github.com/spapas/cookiecutter-django-starter
.. _`abudance of packages/addons`: https://djangopackages.org/
.. _django-auth-ldap: https://github.com/django-auth-ldap/django-auth-ldap
.. _django-crispy-forms: https://github.com/django-crispy-forms/django-crispy-forms
.. _formsets: https://docs.djangoproject.com/en/4.1/topics/forms/formsets/
.. _django-extra-views: https://github.com/AndrewIngram/django-extra-views

.. _`official website`: https://www.postgresql.org/download/windows/
.. _`zip archives`: https://www.enterprisedb.com/download-postgresql-binaries
.. _`postgres trust authentication page`: https://www.postgresql.org/docs/current/auth-trust.html
.. _`psql reference page`: https://www.postgresql.org/docs/14/app-psql.html`
.. _`this SO issue`: https://stackoverflow.com/questions/20794035/postgresql-warning-console-code-page-437-differs-from-windows-code-page-125
.. _dbeaver: https://dbeaver.io/
.. _`template database`: https://www.postgresql.org/docs/current/manage-ag-templatedbs.html