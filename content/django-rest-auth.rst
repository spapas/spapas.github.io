Authenticating with django-rest-auth
####################################

:date: 2018-02-27 14:20
:tags: django, django-rest-auth, rest, django-rest-framework, authentication, python
:category: django
:slug: django-rest-auth
:author: Serafeim Papastefanos
:summary: How to authenticate with django-rest-auth
:status: draft

Introduction
------------

Most of the times I need authentication with `django-rest-framework` I will use 
`SessionAuthentication`_. This method uses the normal django login and logout views
to check out if there's an authenticated user and get his username. As can be
understood this method works only in the same session (browser window) as the one that
actually did the login but this should be enough for most cases.

However, sometimes instead of using the normal django login/logout views, you'll want 
to authentication through REST end-points, for example for using them with SPAs (where
you don't want to use normal views for authentication) or with mobile applications.

There are various ways this could be done but one of the simplest is using `django-rest-auth`.
This project adds a number of REST end-points to your project that can be used for user login
and registration. In the following I am going to write a simple tutorial on how to use `django-rest-auth` to 
authenticate with `django-rest-framework` using the provided REST end points.

Before continuing with the tutorial, let's take a look at what we'll build:

.. image:: /images/rest-auth.gif
  :alt: Our project
  :width: 640 px

This is a single html page (styled with spectre.css_) that checks if the user is logged in 
and either displays the login or logout button. When you click the login you'll get a modal in which you
can enter your credentials which will be submitted through REST to the django-rest-auth endpoint and
depending on the response will set a javascript variable (and a corresponding session/local storage key).
Then you can use the "Test auth" button that works only on authenticated users and returns their username.
Finally, notice that after you log out the "test auth" button returns a 403 access denied. 

If you want to play with this project yourself, you can clone it here https://github.com/spapas/rest_authenticate.
Just create a venv, install requirements, create a superuser and you should be good to go!

Installation & configuration
----------------------------

To install django-rest-auth just follow `the instructions here` i.e just add 
``'rest_framework', 'rest_framework.authtoken'`` and ``'rest_auth'`` to your `INSTALLED_APPS` in
``settings.py`` and run migrate. 

Since I won't be adding any other apps to this project (no models are actually needed), I've added
two directories ``static`` and ``templates`` to put static files and templates there. This is configured
by adding the ``'DIRS'`` attribte to ``TEMPLATES``, like this:

.. code:: 

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
            ],
            // ...
            
and adding the `STATICFILES_DIRS` setting:

.. code:: 

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]
            

The remaining setting are the default as were created by ``django-admin startproject``. 

I have included the the following urls to ``urls.py``:

.. code::

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('test_auth/', TestAuthView.as_view(), name='test_auth', ),
        path('rest-auth/', include('rest_auth.urls')),
        path('', HomeTemplateView.as_view(), name='home', ),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

These are: The django-admin, a test_auth view (that works only for authenticated users and returns their username),
the rest-auth REST end-points, the 

.. _`SessionAuthentication`: http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication
.. _`django-rest-auth`: https://github.com/Tivix/django-rest-auth
.. _`django-rest-framework`: http://www.django-rest-framework.org
.. _`the instructions here`: http://django-rest-auth.readthedocs.io/en/latest/installation.html#installation
.. _spectre.css: https://picturepan2.github.io/spectre/