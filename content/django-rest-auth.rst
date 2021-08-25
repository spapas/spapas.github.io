Authentication for django-rest-framework with django-rest-auth
##############################################################

:date: 2018-03-01 22:40
:tags: django, django-rest-auth, rest, django-rest-framework, authentication, python
:category: django
:slug: django-rest-auth
:author: Serafeim Papastefanos
:summary: How to authenticate with django-rest-auth


**Update: 25/08/2021** Please notice that I've written 
a `a new article  <{filename}django-rest-auth-tokens.rst>`_ 
concerning Token authentication in django rest framework which 
I recommend to read instead of this one since most info here is 
deprecated.

Introduction
------------

Most of the times I need authentication with any REST APIs defined through `django-rest-framework`_ 
I will use  `SessionAuthentication`_ method. This method uses the session cookie (which is set through the 
normal Django login and logout views)
to check out if there's an authenticated user and get his username. This method works only in the 
same session (browser window) as the one that actually did the login but this should be enough for most cases.

However, sometimes instead of using the normal Django login/logout views, you'll want 
to authentication through REST end-points, for example for using them with SPAs (where
you don't want to use the traditional views for authentication but through REST end-points) or 
because you have implemented a mobile (or desktop) application that needs to authenticate with
your script.

There are various ways this could be done but one of the simplest is using `django-rest-auth`_.
This project adds a number of REST end-points to your project that can be used for user login
and registration (and even social login when combined with `django-allauth`_). 
In the following I am going to write a simple tutorial on how to actually use django-rest-auth to 
authenticate with django-rest-framework using the provided REST end points and how to call a
REST API as an authenticated user.

Before continuing with the tutorial, let's take a look at what we'll build here:

.. image:: /images/rest-auth.gif
  :alt: Our project
  :width: 640 px

This is a single html page (styled with spectre.css_) that checks if the user is logged in 
and either displays the login or logout button (using javascript). When you click the login you'll get a modal in which you
can enter your credentials which will be submitted through REST to the django-rest-auth endpoint and
depending on the response will set a javascript variable (and a corresponding session/local storage key).
Then you can use the "Test auth" button that works only on authenticated users and returns their username.
Finally, notice that after you log out the "test auth" button returns a 403 access denied. 

If you want to play with this project yourself, you can clone it here https://github.com/spapas/rest_authenticate.
Just create a venv, install requirements, create a superuser and you should be good to go!

Some theory
-----------

After you log in with Django, your authentication information is saved to the "session"_. The session is a bucket of information
that the Django application saves about your visit -- to distinguish between different visitors a cookie with a unique
value named ``sessionid`` will be used. So, your web browser will send this cookie with each page request thus allowing Django
to know which bucket of information is yours (and if you've authenticated know who are you). This is not a Django
related concept but a general one (supported by most if not all HTTP frameworks) and is used to add state to an otherwise
stateless medium (HTTP).

Since the ``sessionid`` cookie is sent not only with traditional but also with Ajax request it can be used to authenticate
REST requests after you've logged in. This is what is used by default in django-rest-framework and as I said in the
introduction it is a very good solution for most use cases: You login to django and you can go ahead and call the REST
API through Ajax; the ``sessionid`` cookie will be sent along with the request and you'll be authenticated.

Now, although the session authentication is nice for using in browsers, you may need to access your API through a desktop
or a mobile application where, setting the cookies yourself is not the optimal solution. Also, you may have an SPA that needs
to access an API in a different domain; using `using cookies for this is not easy`_ - if possible at all.

For such cases, django-rest-framework
offers a different authentication method called ``TokenAuthentication_``. Using this method, each user of the Django application
is correlated with a random string (Token) which is passed along with the request at its header thus the Django app can authenticate
the user using this token! One thing that may seem strange is that since both the session cookie and a token are 
set through HTTP Headers why all the fuss about tokens? Why not just use the session cookie and be done with it. Well, there are
various reasons - here's a `rather extensive article` explaining some. Some of the reasons are that a token can be valid forever 
while the session is something ephemeral - beyond authorization information, sessions may keep various other data for a web
application and are expired after some time to save space. Also, since tokens are used for exactly this (authentication) they
are much easier to use and reason about. Finally, as I've already explained, sharing cookies by multiple sites is not something
you'd like to do.

Installation & configuration
----------------------------

To install django-rest-auth just follow `the instructions here`_ i.e just add 
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
        path('rest-auth/logout/', LogoutViewEx.as_view(), name='rest_logout', ),
        path('rest-auth/login/', LoginView.as_view(), name='rest_login', ),
        path('', HomeTemplateView.as_view(), name='home', ),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

These are: The django-admin, a test_auth view (that works only for authenticated users and returns their username),
*a view (LogoutViewEx) that overrides the rest-auth REST logout-view* (I'll explain why this is needed in a minute),
the rest-auth REST login-view, the home template view (which is the only view implemented) and finally a mapping
of your static files to the ``STATIC_URL``. 

The views
---------

There are three views in this application - the ``HomeTemplateView``, the ``TestAuthView``
and the ``LogoutViewEx`` view that overrides the normal ``LogoutView`` of ``django-rest-auth``. 
The first one is
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
            'rest_framework.permissions.IsAuthenticated',
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

The above mean that if you don't define authentication and permission classes anywhere then the REST 
views will use either session authentication (i.e the user has logged in normally using
the Django login views as explained before) or basic authentication 
(the request provides the credentials in the header using traditional HTTP Basic authentication)
and also that all users (logged in or not) will be allowed to call all APIs (this is
probably not something you want).

The ``TokenAuthentication`` that we are using instead means that for every user there must be a valid token which will be provided
for each request he does. The tokens are normal object instances of ``rest_framework.authtoken.models.Token``
and you can take a look at them (or even add one) through the Django admin (auth token - tokens). You can also
even do whatever you normally would do to an object instance, for example:

.. code-block:: python

    >>> [ (x.user, x.key) for x in Token.objects.all()]
    [(<User: root>, 'db4dcc1b9d00d1af74fb3cb41e1f9e673208485b')]

To authenticate with a token (using TokenAuthentication_), you must add an extra header to your request with the format
``Authorization: Token token`` for example in the previous case ``root`` would add 
``Authorization: Token db4dcc1b9d00d1af74fb3cb41e1f9e673208485b``. To do this you'll need something
client-side code which we'll see in the next section. 

To do it with curl_ you can just do something like this:

.. code-block:: bash

    curl http://127.0.0.1:8000/test_auth/ -H "Authorization:Token db4dcc1b9d00d1af74fb3cb41e1f9e673208485b"
    
Try it with a valid and invalid token and without providing a token at all and see the response each time.    

So, django-rest-framework provides the model (Token) and the mechanism (add the extra Authentication header) for
authentication with Tokens. What it does not provide is a simple way to create/remove tokens for users: This
is where ``django-rest-auth`` comes to the rescue! Its login and logout REST views will automatically
create (and delete) tokens for the users that are logging in. They will also authenticate the user
normally (using sessions) - this means that if a user logs in using the login REST endpoint he'll then
be logged in normally to the site and be able to access non-REST parts of the site (for example the django-admin).
Also, if the user logs in through the django-rest-auth REST end point and if you have are using ``SessionAuthentication``
to one of your views then he'll be able to authenticate to these views *without* the need to pass the token (can
you understand why?).

Finally, let's take a look at the ``LogoutViewEx``:

.. code-block:: python

    class LogoutViewEx(LogoutView):
        authentication_classes = (authentication.TokenAuthentication,)
        
This class only defines the authentication_classes attribute. Is this really needed? Well, it depends on 
you project. If you take a look at the source code of ``LogoutView`` (https://github.com/Tivix/django-rest-auth/blob/master/rest_auth/views.py#L99)
you'll see that it does not define ``authentication_classes``. This, as we've already discussed, means that it will
fall-back to whatever you have defined in the settings (or the defaults of django-rest-framework). So, if you haven't
defined anything in the settings then you'll get the by default the 
SessionAuthentication and BasicAuthentication methods (hint: *not* the ``TokenAuthentication``). This means that you won't be able to
logout when you pass the token (but *will* be able to logout from the web-app after you login - why?). So to make everything 
crystal and be able to reason better about the behavior I specifically define the ``LogoutViewEx`` to use the ``TokenAuthentication`` - that's
what you'd use if you developed a mobile or desktop app anyway.
        

The client side scripts
-----------------------

I've included all client-side code to a ``home.html`` template that is loaded
from the ``HomeTemplateView``. The client-side code has been implemented only with jQuery because I think
this is the library that most people are familiar with - and is really easy to be understood even if you
are not familiar with it. It more or less consists of four sections in html:

* A user-is-logged-in section that displays the username and the logout button
* A user-is-not-logged-in section that displays a message and the login button
* A test-auth section that displays a button for calling the ``TestAuthView`` defined previously and outputs its response
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
    
The html is very simple and I don't think I need to explain much  - notice that the `#logged-in` and 
`#non-logged-in` sections are mutually exclusive (I use ``$.show()`` and ``$.hide()`` to show and hide them) but the `#test` section is always displayed
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

    var getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };
    var g_csrftoken = getCookie('csrftoken');

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
    };

First of all, I define a ``g_urls`` window/global object that will keep the required REST URLS (login/logout and test auth). These
are retrieved from Django using the ``{% url %}`` template tag and are not hard-coded.
After that, I check to see if the user has authenticated before. Notice that because
this is client-side code, I need to do that every time the page loads or else the JS won't be initialized properly! The user login
information is stored to an object named ``g_auth`` and contains two attributes: ``username``, ``key`` (token) and ``remember_me``.

To keep the login information I use either a key named ``auth`` to either the ``localStorage`` or the ``sessionStorage``. The ``sessionStorage`` is used to save 
info for the current browser tab (*not* window) while the ``localStorage`` saves info for ever (until somebody deletes it). Thus,
``localStorage`` can be used for implementing a "remember me" functionality. Notice that instead of using the session/local storage
I could instead integrate the user login information with the Django back-end. To do this I'd need to see if the current user has
a session login and if yes pass his username and token to  Javascript. These values would then be read by the login initialization
code. I'm leaving this as an exercise for attentive readers. 

Getting the login information from the session probably is a better solution for web-apps however I think that using the local or session storage emulate better a more
general (and completely stateless) behaviour especially considering that the API may be used for mobible/desktop apps. 

In any case, after you've initialized the ``g_auth`` object you'll need to read the CSRF cookie. By default Django requires
`CSRF protection`_ for all ``POST`` requests (we do a POST request for login and logout). What happens here is that for pages that may
need to do a ``POST`` request, Django will set a cookie (CSRF cookie) in its initial response. You'll need to read that cookie and submit its
value along with the rest of your form fields when you do the POST. So the ``getCookie`` function is just used to set the ``g_csrftoken`` with the value
of the CSRF cookie.

The final function we define here (which is called a little later) checks to see if there is login information and hides/displays the correct
things in html. It will also set the local or session storage (depending on remember me value).

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
        
        
        // continuing below ...

The first thing happening here is to call the ``initLogin`` function to properly intiialize the page and then we add a couple of
handlers to the click buttons of the ``#loginButton`` (which just displays the modal by adding the ``active`` class ), 
``.close-modal`` class (there are multiple
ways to close the modal thus I use a class which just removes that ``active`` class) and finally to the ``#testAuthButton``. This
button will do a ``GET`` request to the ``g_urls.test_auth`` we defined before. The important thing to notice here is that we add
a ``beforeSend`` attribute to the ``$.ajax`` request which, if ``g_auth`` is defined adds an ``Authorization`` header with the token
in the form that django-rest-framework ``TokenAuthentication`` expects and as we've already discussed above:

.. code-block:: js

    beforeSend: function(request) {
        if(g_auth) {
            request.setRequestHeader("Authorization", "Token " + g_auth.key);
        }
    }

If this ajax call returns ok (``done`` part) we just add the ``Ok`` to a green label else if there's an error (``fail`` part)
we add the response text and status to a red label. You can try clicking the button and you see that only if you've logged in
you will succeed in this call.

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
                        password: password,
                        csrfmiddlewaretoken: g_csrftoken
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
                    // CAREFUL! csrf token is rotated after login: https://docs.djangoproject.com/en/1.7/releases/1.5.2/#bugfixes
                    g_csrftoken = getCookie('csrftoken');
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
``username, password`` *and* ``g_csrftoken`` (as discussed before) as the request data. Now, if there's an
error (``fail``) I just display a generic message (by removing it's `d-invisible` class) while, if the
request was Ok I retrieve the ``key`` (token) from the response, initialize the ``g_auth`` object with the
``username``, ``key`` and ``remember_me`` values and call ``initLogin`` to show the correct divs and save
to the session/local storage. 

It is important to keep in mind that with the line ``g_csrftoken = getCookie('csrftoken')``
we re-read the CSRF cookie. This is needed because, as you can see in the mentioned link in the comment,
after Django logs in, the csrf cookie value is rotated for security reasons so it must be re-read here (or else
the ``logout`` that is also a POST request will not work).

Finally, here's the code for logout (still inside the ``$(function () {``):

.. code-block:: js

        $('#logoutButton').click(function() {
            console.log("Trying to logout");
            $.ajax({
                url: g_urls.logout, 
                method: "POST", 
                beforeSend: function(request) {
                    request.setRequestHeader("Authorization", "Token " + g_auth.key);
                }, 
                data: {
                    csrfmiddlewaretoken: g_csrftoken
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
also call REST end-points as an authenticated used. I recommend using the ``curl`` utility to try to call the rest
end point with various parameters to see the response. Also, you change the ``LogoutViewEx`` with the 
default django-rest-auth ``LogoutView`` and then try logging out through the web-app *and* through curl and see 
what happens when you try to access the test-auth end-point.

Finally, the above project can be easily modified to use
``SessionAuthentication`` instead of ``TokenAuthentication`` (so you won't need ``django-rest-auth`` at all) - I'm
leaving it as an exercise to the reader.


.. _`SessionAuthentication`: http://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication
.. _`django-rest-auth`: https://github.com/Tivix/django-rest-auth
.. _`django-rest-framework`: http://www.django-rest-framework.org
.. _`the instructions here`: http://django-rest-auth.readthedocs.io/en/latest/installation.html#installation
.. _spectre.css: https://picturepan2.github.io/spectre/
.. _default: http://www.django-rest-framework.org/api-guide/settings/#default_authentication_classes
.. _values: http://www.django-rest-framework.org/api-guide/settings/#default_permission_classes
.. _TokenAuthentication: http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
.. _`CSRF protection`: https://docs.djangoproject.com/en/2.0/ref/csrf/
.. _`django-allauth`: https://github.com/pennersr/django-allauth
.. _`"session"`: https://docs.djangoproject.com/en/2.0/topics/http/sessions/
.. _`rather extensive article`: https://auth0.com/blog/angularjs-authentication-with-cookies-vs-token/
.. _`using cookies for this is not easy`: https://stackoverflow.com/questions/3342140/cross-domain-cookies
.. _curl: https://curl.haxx.se