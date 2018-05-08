Adding a delay to Django HTTP responses
#######################################

:date: 2018-05-08 15:20
:tags: python, django, cbv, middleware, class-based-views
:category: django
:slug: django-reponse-add-delay
:author: Serafeim Papastefanos
:summary: How add a delay to your Django HTTP responses using a middleware or a CBV

Sometimes you'd like to make your Django views more slow by adding a fake delay. This may
sound controversial (why would somebody want to make some of his views slower) however it is a real requirement,
at least when developing an application.

For example, you may be using a REST API and you want to implement a spinner while your form is loading. However, usually when
developing your responses will load so soon that you won't be able to admire your spinner in all its glory! Also, when you
submit a POST form (i.e a form that changes your data), it is advisable to disable your submit button so that when your users
double click it the form won't be submitted two times (it may seem strange to some people but this is a very common error that
has bitten me many times; there are many users that think that they need to double click the buttons; thus I always disable
my submit buttons after somebody clicks them); in this case you also need to make your response a little slower to make sure
that the button is actually disabled!

I will propose two methods for adding this delay to your responses. One that will affect all (or most) your views using
a middleware_ and another that you can add to any CBV you want using a mixin; please see my previous `CBV guide`_ for more on
Django CBVs and mixins. For the middleware solution we'll also take a quick look at what is the Django middleware mechanism and
what it 

Using middleware
----------------

The Django middleware_ is a mechanism for adding your own code to the Django request / response cycle. I'll try to explain
this a bit; Django is waiting for an HTTP Request (i.e GET a url with these headers and these query parameters), it will
parse this HTTP Request and prepare an HTTP Response (i.e some headers and a Payload). Your view will be the main actor for
retrieving the HTTP response and returning the HTTP request. However, using this middleware mechanism Django allows you to
enable other actors (the middleware) that will universally modify the HTTP request before passing it to your view and will also
modify the view's HTTP respone before sending it back to the client.

Actually, a list of middleware called ... ``MIDDLEWARE`` is `defined by default`_ in the ``settings.py`` of all new Django
projects; these are used to add various capabilities
that are universally needed, for example session support, various security enablers, django message support and others. You
can easily attach your own middleware to that list to add extra functionality. Notice that the order of the middleware in the ``MIDDLEWARE``
list actually matters. Middleware later in the list will be executed after the ones previous in the list; we'll see some consequences of this
later.

Now the time has come to take a quick look at how to implement a middleware, `taken from the Django docs`_:

.. code-block:: python

    class SimpleMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response
            # One-time configuration and initialization.

        def __call__(self, request):
            # Code to be executed for each request before
            # the view (and later middleware) are called.

            response = self.get_response(request)

            # Code to be executed for each request/response after
            # the view is called.

            return response

Actually you can implement the middleware as a nested function however I prefer the classy version. The comments should be really enlightening:
When your project is started the constructor (``__init__``) will be called once, for example if you want to read a configuration setting from the database
then you should do it in the ``__init__`` to avoid calling the database everytime your middleware is executed (i.e for *every* request). The ``__call__`` is
a special method that gets translated to calling this class instance as a function, i.e if you do something like:

.. code-block:: python

    sm = SimpleMiddleware()
    sm()

Then ``sm()`` will execute the ``__call__``; there are various similar `python special methods`_, for example ``__len__``, ``__eq__`` etc

Now, as you can see the ``__call__`` special method has four parts:

* Code that is executed *before* the ``self.get_response()`` method is called; here you should modify the request object. Middleware will reach this point in the order they are listed.
* The actual call to ``self.get_response()``
* Code that is executed *after* the ``self.get_response()`` method is called; here you should modify the response object. Middleware will reach this point in the reverse order they are listed.
* Returning the response to be used by the next middleware

Notice that ``get_response`` will call the next middleware; while the ``get_response`` for the last middleware will actually call the view. Then
the view will return a response which could be modified (if needed) by the middlewares in the opposite order of their definition list.

As an example, let's define two simple middlewares:

.. code-block:: python

    class M1:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            print("M1 before response")
            response = self.get_response(request)
            print("M1 after response")
            return response

    class M2:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            print("M2 before response")
            response = self.get_response(request)
            print("M2 after response")
            return response

When you define ``MIDDLEWARE = ['M1', 'M2']`` you'll see the following:

.. code-block:: python

    # Got the request
    M1 before response
    M2 before response
    # The view is rendered to the response now
    M2 after response
    M1 after response
    # Return the response


Please notice
a middleware may not call ``self.get_response`` to continue the chain but return directly a response (for example a 403 Forbiden response).


After this quick introduction to how middleware works, let's take a look at a skeleton for the time-delay middleware:

.. code-block:: python

    import time

    class TimeDelayMiddleware(object):

        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            time.sleep(1)
            response = self.get_response(request)
            return response

This is really simple, I've just added an extra line to the previous middleware. This line adds a one-second delay to all responses. I've
added it before ``self.get_response`` - because this delay does not depend on anything, I could have added it after ``self.get_response``
without changes in the behavior. Also, the order of this middleware in the ``MIDDLEWARE`` list doesn't matter since it doesn't depend on
other middleware (it just needs to run to add the delay).

This middleware may have a little more functionality, for example to configure the delay from the settings or add the delay only for
specific urls (by checking the ``request.path``).
Here's how these extra features could be implemented:

.. code-block:: python

    import time
    from django.conf import settings

    class TimeDelayMiddleware(object):

        def __init__(self, get_response):
            self.get_response = get_response
            self.delay = settings.REQUEST_TIME_DELAY


        def __call__(self, request):
            if '/api/' in request.path:
                time.sleep(self.delay)
            response = self.get_response(request)
            return response

The above will add the delay only to requests whose path contains ``'/api'``. Another case is if you want to
only add the delay for ``POST`` requests by checking that ``request.method == 'POST'``.

Now, to install this middleware, you can configure your ``MIDDLEWARE`` like this in your ``settings.py``
(let's say that you have an application named ``core`` containing a module named ``middleware``):

.. code-block:: python

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        'core.middleware.TimeDelayMiddleware',
    ]

The other middleware are the default ones in Django. One more thing to consider is that if
you have a single settings.py this middleware will be called; one way to override the delay
is to check for settings.DEBUG and not call ``time.sleep`` for ``DEBUG == False``. However,
the proper way to do it is to have different settings for your development and production
environments and add the ``TimeDelayMiddleware`` only to your development ``MIDDLEWARE`` list.
Having different settings for each development is a `common practice in Django`_ and I totally
recommend to use it.

Using CBVs
----------

Another method to add a delay to the execution of a view is to implement a TimeDelayMixin and inherit
your Class Based View from it. As we've seen in the `CBV guide`_, the ``dispatch`` method is the one
that is always called when your CBV is rendered, thus your ``TimeDelayMixin`` must be implemented like this:

.. code-block:: python
    import time

    class TimeDelayMixin(object, ):

        def dispatch(self, request, *args, **kwargs):
            time.sleep(1)
            return super().dispatch(request, *args, **kwargs)

This is very simple (and you can use similar techniques as described for the middleware above to configure
the delay time, or delay only ``POST`` or add the delay only when settings.DEBUG == True etc) - to actually use it, just inherit your
view from this mixin, f.e:

.. code-block:: python

    class DelayedSampleListView(TimeDelayMixin, ListView):
        model = Sample

Now whenever you call your ``DelayedSampleListView`` you'll see it after the configured delay!

What is really interesting is that the ``dispatch`` method actually exists (and has the same functionality) also
in Django Rest Framework CBVs, thus using the same mixin you can delay not only your normal CBVs but also your DRF API views!



.. _middleware: https://docs.djangoproject.com/en/2.0/topics/http/middleware/
.. _`CBV guide`: https://spapas.github.io/2018/03/19/comprehensive-django-cbv-guide/
.. _`defined by default`: https://docs.djangoproject.com/en/2.0/topics/http/middleware/#activating-middleware
.. _`taken from the Django docs`: https://docs.djangoproject.com/en/2.0/topics/http/middleware/#writing-your-own-middleware
.. _`python special methods`: http://www.diveintopython3.net/special-method-names.html
.. _`common practice in Django`: https://medium.com/@ayarshabeer/django-best-practice-settings-file-for-multiple-environments-6d71c6966ee2