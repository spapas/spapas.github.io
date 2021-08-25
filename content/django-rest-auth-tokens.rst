Token Authentication for django-rest-framework
##############################################

:date: 2021-08-25 12:40
:tags: django, dj-rest-auth, rest, django-rest-framework, authentication, python, tokens
:category: django
:slug: django-token-rest-auth
:author: Serafeim Papastefanos
:summary: How to authenticate django-rest-framework with tokens

Introduction
------------

In a `a previous article <{filename}django-rest-auth.rst>`_ 
I explained how to authenticate for your django-rest-framework API 
using the django-rest-auth package.
Since then I have observed that various things have changed and most importantly that 
the library I used there (django-rest-auth) is not updated anymore and has been 
superseded by another one. Also, some of my information there is contradictory, 
especially the parts that deal with the session authentication and csrf protection. 

Thus I've written this new article that betters describes a recommended
authentication workflow using tokens. This workflow does not rely on sessions at all.
Beyond that, is more or less the same as the previous one with some updates 
and clarifications where needed. 

I have also updated the accompanying project of the previous article which
can be found on https://github.com/spapas/rest_authenticate.

Before continuing with the tutorial, let's take a look at what we'll build here:

.. image:: /images/rest-auth.gif
  :alt: Our project
  :width: 640 px

This is a single html page (styled with spectre.css_) that checks if the user is logged in 
and either displays the login or logout button (using javascript). When you click the login you'll get a modal in which you
can enter your credentials which will be submitted through REST to the authentication endpoint and
depending on the response will set a javascript variable (and a corresponding session/local storage key).
Then you can use the "Test auth" button that works only on authenticated users and returns their username.
Finally, notice that after you log out the "test auth" button returns a 403 access denied. 

The javascript client uses token authentication so you can run the client in the same server as the server or 
in a completely different server (if you are using the proper CORS headers of course). 


Some theory
-----------

Here I will try to explain a bunch of important concepts:

Sessions
========

After you log in with Django normally, your authentication information is saved to the session_. 
The session is a bucket of information
that the Django application saves about your visit -- to distinguish between different visitors a cookie with a unique
value named ``sessionid`` will be used. So, your web browser will send this cookie with each page request thus allowing Django
to know which bucket of information is yours (and if you've authenticated know who are you). This is not a Django
related concept but a general one (supported by most if not all HTTP frameworks) and is used to add state to an otherwise
stateless medium (HTTP).

Since the ``sessionid`` cookie is sent not only with traditional but also with Ajax request it can be used to authenticate
REST requests after you've logged in. This is what is used by default in django-rest-framework is a very good solution for 
most use cases: You login to django and you can go ahead and call the REST
API through Ajax; the ``sessionid`` cookie will be sent along with the request and you'll be authenticated automatically.

Now, although the session authentication is nice for using in browsers, you may need to access your API through a desktop
or a mobile application where, setting the cookies yourself is not the optimal solution. Also, you may have an SPA that needs
to access an API in a different domain; using `using cookies for this is not easy`_ - if possible at all.


CSRF protection 
===============

One important thing that you should be aware if you are going to use session authentication for your API is the 
`CSRF protection`_. This is a mechanism that helps prevent cross-site request forgery (CSRF) attacks. 
A CSRF attack works like this: Let's suppose that site A is a bank, and has a form with an email and a money amount. 
When the user submits the form via POST it will send this much money to the entered email using Paypal. Now, site B is 
a malicious site. When the user visits site B, it will automatically generate a POST request containing the malicious 
user's email and the money he wants and submit it to site A. Now, if the user is authenticated with sessions on site A
then site A will think that this is a valid form submission and will actually process the form as normally and send the 
money to the malicious user!

As you can understand this is a very serious and easy to exploit attack. To prevent this attack, the CSRF protection is 
used: In order to submit the form on site A, the request must contain a unique string (the CSRF token) that is generated 
automatically by site A. Thankfully, site B cannot access this token and thus cannot submit the form.

The CSRF situation is only related to sessions. If you are not using sessions then CSRF protection is not needed because 
there's no way for site B to submit the form on site A (for example, with TokenAuthentication, site B cannot access the 
token that site A has). 

However if you *are* using sessions then you must be extra careful
to protect your POST views against CSRF attacks. Django does this by default so you don't need to do anything 
fancy. However, when you actually want to submit a form using an API with sessions you must be careful to also 
include the CSRF token as explained in the Django docs about the topic (`CSRF protection`_). 

Tokens
======

For cases where you can't use the session to authenticate, django-rest-framework
offers a different authentication method called ``TokenAuthentication_``. Using this method, each user of the Django application
is correlated with a random string (Token) which is passed along with each request at its header thus the Django app can authenticate
the user using this token. The token is retrieved when the user logs using his credentials and is saved in the browser.

One thing that may seem strange is that since both the session cookie and a token are 
set through HTTP Headers why all the fuss about tokens? Why not just use the session cookie and be done with it?
Well, there are
various reasons - here's a `rather extensive article`_ explaining some of them. Some of the reasons are that a token can be valid forever 
while the session is something ephemeral - beyond authorization information, sessions may keep various other data for a web
application and are expired after some time to save space. Also, since tokens are used for exactly this (authentication) they
are much easier to use and reason about. Finally, as I've already explained, sharing cookies by multiple sites is not something
you'd like to do. Actually, to make things easier for you just follow this rule: 
**If your API will be run on a different domain  than your client (i.e api.example.com and www.example.com)
or your client not run on the web (i.e. is a desktop/mobile app) then you must not use session authentication**. Use token 
authentication as proposed here or whatever else you may want that doesn't rely on sessions.


CORS
====

Another thing that must concern the people that will want to use an API is the CORS_ situation.
By default cross-origin requests are not allowed, i.e site B cannot issue Ajax requests to site A.
Each server can be configured to allow cross-origin requests from other servers. This means that 
if you have a server api.example.com that is used as a backend and a server www.example.com that will 
serve your front-end, you can configure api.example.com to allow requests only from www.example.com.

By default Django does not allow any cross origin requests and you need to use the django-cors-headers_
package to properly configure it. 

Notice that CORS protection is enforced by the Browser. For example if you have build a mobile app
and are consuming an API in api.example.com then CORS protection does not apply to your http client.


Installation & configuration
----------------------------

The project will use django-rest-framework_, dj-rest-auth_ and django-cors-headers_.

To install django-rest-framework and dj-rest-auth just follow `the instructions here`_ i.e just add 
``'rest_framework', 'rest_framework.authtoken'`` and ``'dj_rest_auth'`` to your `INSTALLED_APPS` in
``settings.py`` and run migrate. 

To install django-cors-headers follow the `the setup instructions`_: Add ``"corsheaders"`` to your ``INSTALLED_APPS`` and 
``"django.middleware.common.CommonMiddleware"`` to your ``MIDDLEWARE`` in ``settings.py``. Then you can use the 
``CORS_ALLOWED_ORIGINS`` setting to configure which origins are allowed to make requests to your project. Let's 
suppose that you are running your project at 127.0.0.1:8000 and you want to allow requests from a client 
running at 127.0.0.1:8001. You can do this by adding the following to your settings.py: 
``CORS_ALLOWED_ORIGINS = ['http://127.0.0.1:8001', 'http://localhost:8001']``. Actually, try running the project 
with and without that setting and see how the javascript client behaves.

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

Urls
----

I have included the the following urls to ``urls.py``:

.. code-block:: python

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('test_auth/', TestAuthView.as_view(), name='test_auth', ),
        path('rest-auth/logout/', LogoutViewEx.as_view(), name='rest_logout', ),
        path('rest-auth/login/', LoginView.as_view(), name='rest_login', ),
        path('', HomeTemplateView.as_view(), name='home', ),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

These are: The django-admin, a ``test_auth`` view (that works only for authenticated users and returns their username),
a view (``LogoutViewEx``) that overrides the rest-auth REST logout-view (I'll explain why this is needed in a minute),
the rest-auth REST login-view, the home template view (which is the only view implemented) and finally a mapping
of your static files to the ``STATIC_URL``. 

The ``LoginView`` is the default provided by the dj-rest-auth project. One thing to consider is that 
this view will check if the credentials you pass are valid and return a valid token for your user. However, 
it will also optionally login the user using sessions (i.e create a new session and return a sessionid cookie). This 
is configured by the ``REST_SESSION_LOGIN`` option which by default is ``True``. 

To test this functionality, try logging in using this login view with a superuser and then visit the django-admin. You 
will see that you are already logged in. Now, logout and add (or change) ``REST_SESSION_LOGIN=False`` to your settings.py.
Login again from the rest view and now if you visit the django-admin you should see that you need to login again.

Another way to test this is by checking out the response headers of the ``POST`` to ``rest-auth/login/`` from your 
browser's development tools. When you are using ``REST_SESSION_LOGIN=True`` (or you haven't defined it since by 
default it is true) you'll see the following ``Set-Cookie`` line:

.. code::

    sessionid=pw8rp7l7yy33lk7geuxbczaleh35w9je; expires=Wed, 08 Sep 2021 08:29:40 GMT; HttpOnly; Max-Age=1209600; Path=/; SameSite=Lax

This cookie won't be set if you login again with ``REST_SESSION_LOGIN=False``.


The views
---------

I've defined three views in this application - the ``HomeTemplateView``, the ``TestAuthView``
and the ``LogoutViewEx`` view that overrides the normal ``LogoutView`` of ``django-rest-auth``. 

HomeTemplateView
================

The ``HomeTemplateView`` is
a simple ``TemplateView`` that just
displays an html page and loads the client side code - we'll talk about it later in the front-side section. 
This is more or less similar (without the django-stuff) with the standalone client  page that can be found on 
``client/index.html``.

TestAuthView
============

The ``TestAuthView`` is implemented like this:

.. code-block:: python

    class TestAuthView(APIView):
        authentication_classes = (authentication.TokenAuthentication,)
        permission_classes = (permissions.IsAuthenticated,)

        def get(self, request, format=None):
            return Response("Hello {0}!".format(request.user))
        
        def post(self, request, format=None):
            return Response("Hello {0}! Posted!".format(request.user))
            
This is very simple however I'd like to make a few comments about the above. First of all you see that
I've defined both a ``get`` and a ``post`` method. When you use the token authentication you'll see that the 
``post`` method will work without the need to provide a csrf token as already discussed before.

Authentication and permission
=============================

Notice that both ``authentication_classes`` and ``permission_classes`` are included in the ``TestAuthView``. These options define:

* which method will be used for authenticating access to the REST view i.e finding out if the user 
  requesting access has logged in and if yes what's his username (in our case only ``TokenAuthentication`` will be used)
* if the user is authorized (has permission) to call this REST view (in our case only authenticated users will be allowed)

The authentication and permission classes can be set globally 
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
            'rest_framework.permissions.IsAuthenticated',
        ),
    }

Please keep in mind that you haven't defined these in your views or your settings, they will have the 
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

The above mean that if you don't define authentication and permission classes anywhere then the REST 
views will use either session authentication (i.e the user has logged in normally using
the Django login views as explained before) or HTTP basic authentication 
(the request provides the credentials in the header using traditional HTTP Basic authentication)
and also that all users (logged in or not) will be allowed to call all APIs (this is
probably not something you want).

Tokens
======

The ``TokenAuthentication`` that we are using for the ``TestAuthView``
means that for every request a valid token must be passed (there's no concept of state 
in HTTP so you need to pass it whenever you communicate with the server). 

The tokens are normal object instances of ``rest_framework.authtoken.models.Token``
and you can take a look at them (or even add one) through the Django admin (auth token - tokens). You can also
even do whatever you normally would do to an object instance, for example:

.. code-block:: python

    >>> [ (x.user, x.key) for x in Token.objects.all()]
    [(<User: root>, 'db4dcc1b9d00d1af74fb3cb41e1f9e673208485b')]

To authenticate with a token (using TokenAuthentication_), you must add an extra header to your request with the format
``Authorization: Token token`` for example in the previous case ``root`` would add 
``Authorization: Token db4dcc1b9d00d1af74fb3cb41e1f9e673208485b``. To do this you'll need something
client-side code which we'll see in the next section. 

To debug your authentication with curl_ you can just do something like this:

.. code-block:: bash

    curl http://127.0.0.1:8000/test_auth/ -H "Authorization:Token db4dcc1b9d00d1af74fb3cb41e1f9e673208485b"
    
Try it with a valid and invalid token and without providing a token at all and see the response each time.    

dj-rest-auth
============

So, django-rest-framework provides the model (Token) and the mechanism (add the extra Authentication header) for
authentication with Tokens. What it does not provide is a simple way to create/remove tokens for users: This
is where the dj-rest-auth project comes to the rescue! Its login and logout REST views will automatically
create (and delete) tokens for the users that are logging in. 

As already described above, the login view will also authenticate the user
using the session when the REST_SESSION_LOGIN is set to True (default) - this means that if a user 
logs in using the login REST endpoint he'll then
be logged in normally to the site and be able to access non-REST parts of the site (for example the django-admin).

Also, if the user logs in through the dj-rest-auth REST end point and if you have are using ``SessionAuthentication``
to one of your views then he'll be able to authenticate to these views *without* the need to pass the token (make sure 
you understand why).

LogoutViewEx
============

Finally, let's take a look at the ``LogoutViewEx``:

.. code-block:: python

    class LogoutViewEx(LogoutView):
        authentication_classes = (authentication.TokenAuthentication,)
        
This class only defines the authentication_classes attribute. Is this really needed? Well, it depends on 
you project. If you take a look at the source code of 
``LogoutView`` (https://github.com/iMerica/dj-rest-auth/blob/master/dj_rest_auth/views.py#L131)
you'll see that it does not define ``authentication_classes``. This, as we've already discussed, means that it will
fall-back to whatever you have defined in the settings (or the defaults of django-rest-framework). 

So, if you haven't
defined anything in the settings then you'll get the by default the 
``SessionAuthentication`` and ``BasicAuthentication`` methods (hint: *not* the ``TokenAuthentication``). 
This means that you won't be able to
logout when you pass the token (but *will* be able to logout from the web-app after you login - why?). So to make everything 
crystal and be able to reason better about the behavior I specifically define the ``LogoutViewEx`` to use 
the ``TokenAuthentication`` to properly log out your user. This of course means that you need to pass 
the token to your logout view also or else there won't be any way to associate the request with a user to log out.
        

The client side scripts
-----------------------

I've included all client-side code to a ``home.html`` template that is loaded
from the ``HomeTemplateView``. Also, the same code has been included in ``client/index.html``. This is 
a completely standalone javascript client that you can run in a different http server than your Django server, 
for example by running ``py -3 -m  http.server 8001`` from the client folder and visiting http://127.0.0.1:8001.


The client-side code has been implemented only with jQuery because I think
this is the library that most people are familiar with - and is really easy to be understood even if you
are not familiar with it. It more or less consists of five sections in html:

* A user-is-logged-in section that displays the username and the logout button
* A user-is-not-logged-in section that displays a message and the login button
* A test-auth section that displays a button for calling the ``TestAuthView`` with GET defined previously and outputs its response
* A test-auth POST section that displays a button for calling the ``TestAuthView`` with POST defined previously and outputs its response
* The login modal

Here's the html (using spectre.css for styling):

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
    <hr />
    <div class="columns" id="test">
        <div class='column col-3'>
            <button class="btn btn-primary"  id='testAuthPostButton'>Test auth (POST)</button>
        </div>
        <div class='column col-9'>
            <div id='test-auth-post-response' ></div>
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
    
The html is very simple and I don't think I need to explain much  - notice that the ``#logged-in`` and ``#non-logged-in`` 
sections are mutually exclusive (I use ``$.show()`` and ``$.hide()`` to show and hide them) but the ``#test`` section is always displayed
so you'll be able to call the test REST API when you are and are not authenticated. For the modal
to be displayed you need to add an ``active`` class to its ``#modal`` container.

For the javascript, let's take a look at some initialization stuff:

.. code-block:: js

    var g_urls = {
        'login': '{% url "rest_login" %}',
        'logout': '{% url "rest_logout" %}',
        'test_auth': '{% url "test_auth" %}',
    };
    var g_auth = localStorage.getItem("auth");
    if(g_auth == null) {
        g_auth = sessionStorage.getItem("auth");
    }
    
    if(g_auth) {
        try {
            g_auth = JSON.parse(g_auth);
        } catch(error) {
            g_auth = null; 
        }
    }

    var initLogin = function() {
        if(g_auth) {
            $('#non-logged-in').hide();
            $('#logged-in').show();
            $('#span-username').html(g_auth.username);
            if(g_auth.remember_me) {
                localStorage.setItem("auth", JSON.stringify(g_auth));
            } else {
                sessionStorage.setItem("auth", JSON.stringify(g_auth));
            }
        } else {
            $('#non-logged-in').show();
            $('#logged-in').hide();
            $('#span-username').html('');
            localStorage.removeItem("auth");
            sessionStorage.removeItem("auth");
        }
        $('#test-auth-response').html("");
        $('#test-auth-post-response').html("");
    };

First of all, I define a ``g_urls`` window/global object that will keep the required REST URLS (login/logout and test auth). These
are retrieved from Django using the ``{% url %}`` template tag and are not hard-coded (in the js only client they are hard-coded of course).
After that, I check to see if the user has authenticated before. Notice that because
this is client-side code, I need to do that every time the page loads or else the JS won't be initialized properly! The user login
information is stored to an object named ``g_auth`` and contains three attributes: ``username``, ``key`` (token) and ``remember_me``.

To keep the login information I use either a key named ``auth`` to either the ``localStorage`` or the ``sessionStorage``. The ``sessionStorage`` is used to save 
info for the current browser tab (*not* window) while the ``localStorage`` saves info for ever (until somebody deletes it). Thus,
``localStorage`` can be used for implementing a "remember me" functionality.


The final function we define here, ``initLogin`` (which is called a little later) checks to see if there is login information 
and hides/displays the correct things in html. It will also set the local or session storage (depending on remember me value).

After that, we have some client side code that is inside the ``$()`` function which will be called after the page has completely loaded:

.. code-block:: js

    $(function () {
        initLogin(); 

        $('#loginButton').click(function() {
            $('#login-modal').addClass('active');
        });
        
        $('.close-modal').click(function() {
            $('#login-modal').removeClass('active');
        });
        
        $('#testAuthButton').click(function() {
            $.ajax({
                url: g_urls.test_auth, 
                method: "GET", 
                beforeSend: function(request) {
                    if(g_auth) {
                        request.setRequestHeader("Authorization", "Token " + g_auth.key);
                    }
                }
            }).done(function(data) {
                $('#test-auth-response').html("<span class='label label-success'>Ok! Response: " + data);
            }).fail(function(data) {
                $('#test-auth-response').html("<span class='label label-error'>Fail! Response: " + data.responseText + " (status: " + data.status+")</span>");
            });
        });
        
        $('#testAuthPostButton').click(function() {
            // Same as with the GET 
        });
        
        // continuing below ...

The first thing happening here is to call the ``initLogin`` function to properly initialize the page and then we add a couple of
handlers to the click buttons of the ``#loginButton`` (which just displays the modal by adding the ``active`` class ), 
``.close-modal`` class (there are multiple
ways to close the modal thus I use a class which just removes that ``active`` class) and finally to the ``#testAuthButton``
and ``#testAuthPostButton#``. 
These
button will do a ``GET`` and ``POST`` request to the ``g_urls.test_auth`` we defined before. The important thing to notice 
here is that we add
a ``beforeSend`` attribute to the ``$.ajax`` request which, if ``g_auth`` is defined, adds an ``Authorization`` header with the token
in the form that django-rest-framework ``TokenAuthentication`` expects and as we've already discussed above:

.. code-block:: js

    beforeSend: function(request) {
        if(g_auth) {
            request.setRequestHeader("Authorization", "Token " + g_auth.key);
        }
    }

If this ajax call returns without errors (the ``done`` part of the ajax call) 
we just add the ``data`` to a green label else if there's an error (``fail`` part)
we add the response text and status to a red label. You can try clicking the buttons and you see that only if you've logged in
you will succeed in this call. Also, notice that both GET and POST requests work normally without the need to also include 
a csrf token (I hope you understand why by now).

Let's now take a look at the ``#loginOkbutton`` click handler (inside the modal):

.. code-block:: js

        $('#loginOkButton').click(function() {
            var username = $('#input-username').val();
            var password = $('#input-password').val();
            var remember_me = $('#input-local-storage').prop('checked');
            if(username && password) {
                console.log("Will try to login with ", username, password);
                $('#modal-error').addClass('d-invisible');
                $.ajax({
                    url: g_urls.login, 
                    method: "POST", 
                    data: {
                        username: username,
                        password: password
                    }
                }).done(function(data) {
                    console.log("DONE: ", username, data.key);
                    g_auth = {
                        username: username,
                        key: data.key,
                        remember_me: remember_me
                    };
                    $('#login-modal').removeClass('active');
                    initLogin();
                }).fail(function(data) {
                    console.log("FAIL", data);
                    $('#modal-error').removeClass('d-invisible');
                });
            } else {
                $('#modal-error').removeClass('d-invisible');
            }
        });

All three user inputs (``username, password, remember_me``) are read from the form and if both username and
password have been defined an Ajax request will be done to the ``g_urls.login`` url. We pass
``username`` and ``password`` as the request data. Now, if there's an
error (``fail``) I just display a generic message (by removing it's `d-invisible` class) while, if the
request was Ok I retrieve the ``key`` (token) from the response, initialize the ``g_auth`` object with the
``username``, ``key`` and ``remember_me`` values and call ``initLogin`` to show the correct divs and save
to the session/local storage. 

Finally, here's the code for logout (still inside the ``$(function () {``):

.. code-block:: js

        $('#logoutButton').click(function() {
            console.log("Trying to logout");
            $.ajax({
                url: g_urls.logout, 
                method: "POST", 
                beforeSend: function(request) {
                    request.setRequestHeader("Authorization", "Token " + g_auth.key);
                }
            }).done(function(data) {
                console.log("DONE: ", data);
                g_auth = null;
                initLogin();
            }).fail(function(data) {
                console.log("FAIL: ", data);
            });
        });
    
    }); // End of $(function () {

The code here is very simple - just do a ``POST`` to the ``g_urls.logout``  and if everything is ok delete the ``g_auth`` values
and call ``initLogin()`` to show the correct divs and remove the ``auth`` key from local/session storage. Notice that when
you ``POST`` to the ``logout`` REST end-point, you need to also add the ``Authorization`` header with the token or else
(since we've defined only ``TokenAuthentication`` for the ``authentication_classes`` for the ``LogoutViewEx`` class)
there won't be any way to correlate the request with the user and log him out!


Conclusion
----------

Using the info presented on this article you should be able to properly login and logout to Django using REST and
also call REST end-points using the ``TokenAuthentication``. 

I recommend using the ``curl`` utility to try to call the rest
end point with various parameters to see the response. Also, you change the ``LogoutViewEx`` with the 
default django-rest-auth ``LogoutView`` and then try logging out through the web-app *and* through curl and see 
what happens when you try to access the test-auth end-point.

As a final remark, a couple of thing to note:

* You can use the django-rest-knox_ package to improve the functionality and security of your REST tokens (by allowing multiple tokens per user, storing them hashed in the database and configuring expiration times for the tokens)
* If you are using Apache and mod_wsgi to run you Django project you need to set the WSGIPassAuthorization_ option to ``on`` in order to pass the Authorization header to your Django app.


.. _`SessionAuthentication`: http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication
.. _`dj-rest-auth`: https://github.com/iMerica/dj-rest-auth
.. _`django-rest-framework`: http://www.django-rest-framework.org
.. _`the instructions here`: https://dj-rest-auth.readthedocs.io/en/latest/installation.html
.. _`the setup instructions`: https://github.com/adamchainz/django-cors-headers#setup
.. _spectre.css: https://picturepan2.github.io/spectre/
.. _default: http://www.django-rest-framework.org/api-guide/settings/#default_authentication_classes
.. _values: http://www.django-rest-framework.org/api-guide/settings/#default_permission_classes
.. _TokenAuthentication: http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
.. _`CSRF protection`: https://docs.djangoproject.com/en/stable/ref/csrf/
.. _`django-allauth`: https://github.com/pennersr/django-allauth
.. _session: https://docs.djangoproject.com/en/stable/topics/http/sessions/
.. _`rather extensive article`: https://auth0.com/blog/angularjs-authentication-with-cookies-vs-token/
.. _`using cookies for this is not easy`: https://stackoverflow.com/questions/3342140/cross-domain-cookies
.. _curl: https://curl.haxx.se
.. _CORS: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
.. _django-cors-headers: https://github.com/adamchainz/django-cors-headers
.. _django-rest-knox: https://github.com/James1345/django-rest-knox
.. _WSGIPassAuthorization: https://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIPassAuthorization.html