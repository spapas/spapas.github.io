Authenticating with django-rest-auth
####################################

:date: 2018-02-28 14:20
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

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
            ],
            // ...
            
and adding the `STATICFILES_DIRS` setting:

.. code-block:: python

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]
            

The remaining setting are the default as were created by ``django-admin startproject``. 

I have included the the following urls to ``urls.py``:

.. code-block:: python

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('test_auth/', TestAuthView.as_view(), name='test_auth', ),
        path('rest-auth/', include('rest_auth.urls')),
        path('', HomeTemplateView.as_view(), name='home', ),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

These are: The django-admin, a test_auth view (that works only for authenticated users and returns their username),
the rest-auth REST end-points, the home template view (which is the only view implemented) and finally a mapping
of your static files to the ``STATIC_URL``.

The views
---------

There are two views in this application - the ``HomeTemplateView`` and the ``TestAuthView``. The first one is
a simple ``TemplateView`` that just
displays an html page and loads the client side code - we'll talk about it later in the front-side section. 

The ``TestAuthView`` is implemented like this:

.. code-block:: python

    class TestAuthView(APIView):
        authentication_classes = (authentication.TokenAuthentication,)
        permission_classes = (permissions.IsAuthenticated,)

        def get(self, request, format=None):
            return Response("Hello {0}!".format(request.user))
            
This is very simple however I'd like to make a few comments about the above. First of all you see that
I've defined ``authentication_classes`` and ``permission_classes``. These options define 

* which method will be used for authenticating access to the REST view i.e finding out if the user 
  requesting access has logged in and if yes what's his username (in our case the ``TokenAuthentication`` will be used)
* if the user is authorized (has permission) to call this REST view (in our case only authenticated users will be allowed)

The authentication and permission clases can be set globally 
in your ``settings.py`` using ``REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`` and 
``REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']``
or defined per-class like this. If I wanted to have the same authentication and permission classes defined
in my ``settings.py`` so I wouldn't need to set these options per-class I'd add the following to my ``settings.py``:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.authentication.IsAuthenticated',
        ),
    }

Finally, keep in mind that you haven't defined these in your views or your settings, they will have the 
following default_ values_: 

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.BasicAuthentication'
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.AllowAny',
        ),
    }

The above mean that the REST views will use either session (i.e the user has logged in normally using
the django login views) or basic (the request provides the credentials using HTTP Basic authentication)
authentication and also that all users (logged in or not) will be allowed to call all APIs (this is
probably not something you want).

The ``TokenAuthentication`` means that for every user there must be a valid token which will be provided
for each request he does. The tokens are normal object instances of ``rest_framework.authtoken.models.Token``
and you can take a look at them (or even add one) through the django admin (auth token - tokens). You can also
even do whatever you normall would do to an instance, for example:

.. code-block:: python

    >>> [ (x.user, x.key) for x in Token.objects.all()]
    [(<User: root>, 'db4dcc1b9d00d1af74fb3cb41e1f9e673208485b')]

To `authenticate with a token`_, you must add an extra header to your request with the format
``Authorization: Token token`` for example in the previous case ``root`` would add 
``Authorization: Token db4dcc1b9d00d1af74fb3cb41e1f9e673208485b``. To do this you'll need something
client-side code which we'll see in the next section.

So, django-rest-framework provides the model (Token) and the mechanism (add the extra header) for
authentication with Tokens. What it does not provide is a simple way to create/remove tokens for users: This
is where ``django-rest-auth`` comes to the rescue! Its login and logout REST views will automatically
create (and delete) tokens for the users that are logging in. They will also authenticate the user
normally (using sessions) - this means that if a user logs in using the login REST endpoint he'll then
be logged in normally to the site and be able to access non-REST parts of the site (for example the django-admin).


The client side scripts
-----------------------

As we've discussed previously, I've included all client-side code to a ``home.html`` template that is loaded
from the ``HomeTemplateView``. The client-side code has been implemented only with jQuery because I think
this is the library that most people are familiar with - and is really easy to be understood even if you
are not familiar with it. It more or less consists of four sections in html:

* A user-is-logged-in section that displays the username and the logout button
* A user-is-not-logged-in section that displays a message and the login button
* A test-auth section that displays a button for calling the ``TestAuthView`` defined previously and outputs its response
* The login modal

Here's the html (as I've already explained, I used spectre.css for styling):

.. code-block:: html

    <div class="container grid-lg">
        <h2>Test</h2>
        <div class="columns" id="non-logged-in">
            <div class='column col-3'>
                You have to log-in!
            </div>
            <div class='column col-3'>
                <button class="btn btn-primary"  id='loginButton'>Login</button>
            </div>
        </div>
        <div class="columns" id="logged-in">
            <div class='column col-3'>
                Welcome <span id='span-username'></span>!
            </div>
            <div class='column col-3'>
                <button class="btn btn-primary"  id='logoutButton'>Logout</button>
            </div>
        </div>
        <hr />
        <div class="columns" id="test">
            <div class='column col-3'>
                <button class="btn btn-primary"  id='testAuthButton'>Test auth</button>
            </div>
            <div class='column col-9'>
                <div id='test-auth-response' ></div>
            </div>
        </div>
    </div>
    
    <div class="modal" id="login-modal">
        <a href="#close" class="modal-overlay close-modal" aria-label="Close"></a>
        <div class="modal-container">
            <div class="modal-header">
                <a href="#close" class="btn btn-clear float-right close-modal" aria-label="Close"></a>
                <div class="modal-title h5">Please login</div>
            </div>
            <div class="modal-body">
                <div class="content">
                    <form>
                        {% csrf_token %}
                        <div class="form-group">
                            <label class="form-label" for="input-username">Username</label>
                            <input class="form-input" type="text" id="input-username" placeholder="Name">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="input-password">Password</label>
                            <input class="form-input" type="password" id="input-password" placeholder="Password">
                        </div>
                        <div class="form-group">
                            <label class="form-checkbox" for="input-local-storage">
                                <input type="checkbox" id="input-local-storage" /> <i class="form-icon"></i>  Use local storage (remember me)
                            </label>
                        </div>
                    </form>
                    <div class='label label-error mt-1 d-invisible' id='modal-error'>
                        Unable to login!
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                
                <button class="btn btn-primary" id='loginOkButton' >Ok</button>
                <a href="#close" class="btn close-modal" >Close</a>
            </div>
        </div>
    </div> 


.. _`SessionAuthentication`: http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication
.. _`django-rest-auth`: https://github.com/Tivix/django-rest-auth
.. _`django-rest-framework`: http://www.django-rest-framework.org
.. _`the instructions here`: http://django-rest-auth.readthedocs.io/en/latest/installation.html#installation
.. _spectre.css: https://picturepan2.github.io/spectre/
.. _default: http://www.django-rest-framework.org/api-guide/settings/#default_authentication_classes
.. _values: http://www.django-rest-framework.org/api-guide/settings/#default_permission_classes
.. _`authenticate with a token`: http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication