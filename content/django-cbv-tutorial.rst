A comprehensive Django CBV guide
################################

:date: 2017-11-29 11:20
:tags: python, cbv, class-based-views, django
:category: django
:slug: comprehensive-django-cbv-guide
:author: Serafeim Papastefanos
:summary: A comprehensive guide to django CBVs - from neophyte to more advanced

Class Based Views (CBV) is one of my favourite things about Django. I've heard
various rants about them (mainly that they are too complex and difficult to use)
but I believe that if they are used properly they grealy improve your Django
experience. Also, they are the only way to properly override django views; if
of course the views have been properly written (i.e they allow overriding) -
more on this later.

This guide has three parts:

- A gentle introduction to how CBVs are working and to the the problems that do solve. For this we'll implement
  our own simple Custom Class Based View variant.
- A high level overview of the real Django CBVs using `CBV inspector`_ as our guide.
- A number of use cases where CBVs can be used to elegantly solve real world problems

A gentle introduction to CBVs
=============================

In this part of the guide we'll do a gentle introduction to (our own) class based views -
along with it we'll introduce some basic concepts of python (multiple) inheritance and how
it applies to CBVs.

Before continuing, let's talk about the concept of the "view" in Django:
Traditionally, a view in Django is a normal python function that takes a single parameter,
the request_ object and must return a response_ object (notice that if the
view takes request parameters for example the id of an object to be retrieved
they will also be passed to the function). The responsibility of the
view function is to properly parse the request parameters and construct the
response object - as can be understood there is a lot of work that need to be
done for each view (for example check if the method is GET or POST, if the user
has access to that page, retrieve objects from the database, render a template etc).

Now, since functional views are simple python functions it is *not* easy to override
or extend their behavior. There are more or less two methods for this: Use function
wrappers or pass extra parameters when adding the view to your urls. The first one
creates an extra function that extends the initial one by adding some functionality
(for example check if the current user has access) and then simply calls the initial one
and returns the result (which could also be changed). For the second one you must
write your function view in a way which allows it to be extended, for example instead
of hard-coding the template name allow it to be passed by a parameter or instead
of using a specific form class for a form make it configurable through a parameter.

Both these methods have severe limitations and do not allow you to be as DRY as
you should be. It is obvious that using the wrapped views you can't actually
change the functionality of the original view (since that original function needs
to be called) by only do things before and after calling it. Also, using the
parameters will lead to spaghetti code with multiple if / else conditions in order
to take into account the various cases that may arise. All the above lead to
very reduced re-usability and DRYness of functional views - usually the best thing
you can do is to gather the common things in external functions that could be
re-used from other functional views (actually gathering common code to re-usable
functions is a practice that you should be doing anyway).

Class based views solve the above problem of non-DRY-ness by using the well know
concept of OO inheritance: The view is defined from a class which has methods
for implementing the view functionality - you inherit from that class and override
the parts you want so the inherited class based view will use the overriden methods instead
of the original ones. You can also create re-usable classes (mixins) that offer a specific
functionality to your class based view by implementing some of the methods of the
original class. Each one of your class based views can inherit its functionality from
multiple mixins thus allowing you to define a single class for each thing you need
and re-using it everywhere.

To make things more clear we'll try to implement our own class based views hierarchy. Here's
a first try:

.. code-block:: python

    class CustomClassView:
        context = []
        header = ''

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            for (k,v) in kwargs.items():
                setattr(self, k, v)

        def render(self):
            return """
                <html>
                    <body>
                        <h1>{header}</h1>
                        {body}
                    </body>
                </html>
            """.format(
                    header=self.header, body='<br />'.join(self.context),
                )

        @classmethod
        def as_view(cls, *args, **kwargs):
            def view(request, ):
                instance = cls(**kwargs)
                return HttpResponse(instance.render())

            return view

This class can be used to render a simple HTML template with a custom header and
a list in the body (named ``context``). There are two things to notice here: The ``__init__`` method (which
will be called as the object's constructor) will assign all the kwargs it receives
as instance attributes (for example ``CustomClassView(header='hello')`` will create
an instance with ``'hello'`` as its header attribute). The ``as_view`` is a classmethod
(i.e it can be called on the *class* without the need to instantiate an object) that
defined and returns the functional view that will be used in your urls. The returned
view is very simple - it just instantiates a new instance of CustomClassView passing
the kwargs it got in the constructor and then returns a normal ``HttpResponse`` with
the instance's ``render()`` result. The ``render`` method will just output some html
using the instance's header and context to fill it.

Notice that the instance above is not created using
``CustomClassView(**kwargs)`` but using ``cls(**kwargs)`` - cls is the name of the
class that ``as_view`` was called on and actually passed as a parameter for
class methods (in a similar manner to how self is passed to instance methods).
This is important to instantiate the correct
object instance. For example, if you created a class that inherits from ``CustomClassView``
and called its ``as_view`` method then when you use the ``cls`` parameter to instantiate
the object it will correctly
create an object of the *inherited* class and not the *base* class.

To add the above class method in your urls, just use its ``as_view()`` as you'd
normally use a functional view:

.. code-block:: python

    from django.conf.urls import include, url
    from . import views

    urlpatterns = [
        url(r'^ccv-empty/$', views.CustomClassView.as_view(), name='ccv-empty'),
        # ... other urls
    ]

This doesn't actually render anything since both header and context are empty on
the created instance -- remember that ``as_view`` returns a functional view that
instantiates a ``CustomClassView`` objet and returns an ``HttpResponse`` filling it
with the object's ``render()`` reuslts. To add some functionality we can either
create another class that inherits from ``CustomClassView`` or
initialize the attributes from the constructor of the class (using the kwargs functionality described above).

The inherited class can just override the values of the attributes:

.. code-block:: python

    class InheritsCustomClassView(CustomClassView, ):
        header = "Hi"
        context = ['test', 'test2' ]

And then just add the inherited class to your urls as before:

.. code-block:: python

    url(r'^ccv-inherits/$', views.InheritsCustomClassView.as_view(), name='ccv-inherits'),

The ``as_view()`` method will create an instance of ``InheritsCustomClassView`` that has
the values configured in the class as attributes and return
its ``render()`` output as response.

The other way to configure the attributes of the class is to
pass them to the ``as_view`` class method (which in turn will pass them to the instances
constructor which will set the attributes in the instance). Here's an example:

.. code-block:: python

    url(r'^ccv-with-values/$', views.CustomClassView.as_view(header='Hello', context=['hello', 'world', ], footer='Bye', ), name='ccv-with-values'),

The above will create a ``CustomClassView`` instance with the provided values as its attributes. This is more or less
similar to how functional views are configured and is limited for the same reasons explained above.

I don't use this method of configuring class based views anymore but I want to discuss it a bit because
it is supported (and used) in normal django CBVs (for example
set the ``template_name`` in a ``TemplateView``). I recommend you also avoid using it  because passing parameters
to the ``as_view`` method pollutes the urls.py with configuration
that (at least in my opinion) should *not* be there and also, even for very simple views I know that after some time I'll need
to add some functionality that cannot be implemented by passing the parameters so I prefer to bite the
bullet and define all my views as inherited classes so it will be easy for me to further customize them later (we'll
see how this is done in a second). In any case, I won't discuss passing parameters to the ``as_view`` method any more
so from now on any class based views I define will be added to urls py using ``ClassName.as_view()``.

Let's now suppose that we wanted to allow our class based view to print something on the header even if no header is provided
when you configure it. The naive way to do it would be to re-define the ``render`` method and do something like

.. code-block:: python

    header=self.header if self.header else "DEFAULT HEADER"

in the ``render()`` method's format.
This is definitely not the way to do it because you more or less need to re-define the whole ``render`` method and think
what would happen if
you wanted to print ``"ANOTHER DEFAULT HEADER"`` as a default header for some other view... In fact, the above
``CustomClassView`` is naively implemented because it does not allow proper customization through inheritance. For
example, if you wanted to add an index number after all the numbers then you'll need to again re-implement the
whole ``render`` method.

This is definitely not DRY. If that was our only option then we could just stick to functional views. We can do
much better if we define the class based view in such a way that allows inherited classes to override methods that
define specific parts of the functionality. Here's how we could improve the ``CustomClassView``:

.. code-block:: python

    class BetterCustomClassView(CustomClassView, ):
        def get_header(self, ):
            print ("Better Custom Class View")
            return self.header if self.header else ""

        def get_context(self , ):
            return self.context if self.context else []

        def render_context(self):
            context = self.get_context()
            if context:
                return '<br />'.join(context)
            return ""

        def render(self):
            return """
                <html>
                    <body>
                        <h1>{header}</h1>
                        {body}
                    </body>
                </html>
            """.format(
                    header=self.get_header(), body=self.render_context(),
                )

So what happens here? First of all we inherit from ``ClassClassView`` to keep the
``as_view`` method which doesn't need changing (for now). Beyond this, the render
uses methods (``get_header`` and ``render_context``) to retrieve the values from the header and the body - this means
that we could re-define these methods to an inherited class in order to override
what these methods will return. Beyond ``get_header`` and ``render_contex`` I've added
a ``get_context`` method that is used by ``render_context`` because, for example I may
need to configure the context (add/remove items from the context). Of course this could
be done from ``render_context`` *but* this means that I would need to define my new functionality
(modifying the context items) *and* re-defining the context list formatting. It is much
better (in my opinion always) to keep properly seperate these things.

Now, the above is a first try that I created to mainly fulfill my requirement of
having a default header and some more examples I will discuss later. You could
extract more functionality as methods-for-overriding, for example the render
method could be written like this:

.. code-block:: python

    def render(self):
        return self.get_template().format(
                header=self.get_header(), body=self.render_context(),
            )

and add a ``get_template`` method that will return the actual html template. There's no
hard rules here on what functionality should be extracted to a method (so it could
be overriden) however I recommend to follow the YAGNI rule (so implement everything
as normally and when you see that some functionality needs to be overriden then refactor
your code to extract it to a separate method).

Let's see an example of adding the default header functionality by overriding ``get_header``:

.. code-block:: python

    class DefaultHeaderBetterCustomClassView(BetterCustomClassView, ):
        def get_header(self, ):
            return self.header if self.header else "DEFAULT HEADER"

Now, classes inheriting from ``DefaultHeaderBetterCustomClassView`` can choose to not
actually define a header attribute so ``"DEFAULT HEADER"`` will be printed instead. Keep in
mind that for ``DefaultHeaderBetterCustomClassView`` to be actually useful you'll need to
have more than one classes that need this default-header functionality (or else you could
just set the header attribute of your class to ``"DEFAULT HEADER"`` - this is not
user generated input, this is your source code!).

We have come now to a crucial point in this introduction, so please stick with me. Let's say that you have
*more than one* class based views that contain a header attribute. You want to include
the default header functionality on all of them so, if they don't define a header
the default string will be output (I know that this may be a rather trivial example but I want
to keep everything simple to make following easy - instead of the default header the functionality
you want to override may be adding stuff to the context or filtering the objects you'll retrieve
from the database).

Now, to re-use this default header funtionality from multiple classes you have *two* options:
Either inherit all classes that need this functionality from ``DefaultHeaderBetterCustomClassView`` or 
extract the custom ``get_header`` method to a mixin and inherit from the mixin. A mixin is a class not
related to the class based view hierarchy we are using - the mixin inherits from object (or from another
mixin) and just defines the methods and attributes that need to be overriden.

To not feel anxious about it I'm telling you right now that using mixins is the best solution for this. But why? 
Let's suppose that you have a base class that renders the header and context as JSON instead of the HTML
template, something like this:

.. code-block:: python

    class JsonCustomClassView:
        def get_header(self, ):
            return self.header if self.header else ""

        def get_context(self, ):
            return self.context if self.context else []

        @classmethod
        def as_view(cls, *args, **kwargs):
            def view(request, ):
                instance = cls(**kwargs)
                return HttpResponse(json.dumps({
                    'header': instance.get_header(),
                    'context': instance.get_context(),
                }))

            return view

Notice that this class does not inherit from our previous hierarchy but from object since it provides
its own ``as_view`` method. Suppose we also wanted to use the default header functionality for this (since it
has a ``get_header`` we could override it if we wanted (duck typing)? Creating a class that
inherits from both ``JsonCustomClassView`` and ``DefaultHeaderBetterCustomClassView`` using something
like 

.. code-block:: python

    # OPTION 1
    class JsonDefaultHeaderCustomClassView(JsonCustomClassView, DefaultHeaderBetterCustomClassView):
        pass

    # OR 
    # OPTION 2
    class DefaultHeaderJsonCustomClassView(DefaultHeaderBetterCustomClassView, JsonCustomClassView):
        pass

is not the
correct solution since the methods ``get_header`` and ``as_view`` exist in *both* ancestor classes so
in the first option the ``get_header`` and ``as_view`` from ``JsonCustomClassView`` will be used while
in the second option the ``get_header`` and ``as_view`` from ``DefaultHeaderBetterCustomClassView`` will
be used. Notice that if these classes had a common ancestor (for example they both used
``CustomClassView``) you may actually get the correct behavior depending on the rather complex rules
of python MRO (metod resolution order). The MRO is also what I used to know which ``get_header``
and ``as_view`` will be used in each ccase in the previous sample.

What is MRO? For every class python tries to create a *list* of classes containing that class as 
the first element and its ancestors in a specific order I'll discuss right next after that. When a method
of an object of a specific class needs to be
called, then the method will be seached in the list (from the first element ie starting that class) - when a class is found
in the list that defines the method then that method (ie the method defined in this class) will be called and the search will stop (careful readers: I haven't
yet talked about *super* please be patient). 

Now, how is the MRO list created? As I explained, the first element
is the class of the object. The second element is the MRO of the *leftmost* ancestor of that object (so MRO will 
run recursively on each ancenstor), the third element will be the MRO of the ancestor right next to the leftomost
ancestor etc. There is one extra and important rule: When class is found multiple times in the MRO list (for example
if some elements have a common ancestor) then *only the last occurence in the list will be kept* - so each class
will be found only one time in the MRO list.

Let's see a quick example for ``DefaultHeaderJsonCustomClassView``:
``DefaultHeaderJsonCustomClassView, DefaultHeaderBetterCustomClassView, BetterCustomClassView, CustomClassView, JsonCustomClassView, object``
and for ``JsonDefaultHeaderCustomClassView``:
``JsonDefaultHeaderCustomClassView, JsonCustomClassView, DefaultHeaderBetterCustomClassView, BetterCustomClassView, CustomClassView, object``

Let's try an example that has the same base class twice in the hierarchy. For this, we'll create a 
``DefaultContextBetterCustomClassView`` that returns a default context if the context is empty. 

.. code-block:: python

    class DefaultContextBetterCustomClassView(BetterCustomClassView, ):
        def get_context(self, ):
            return self.context if self.context else ["DEFAULT CONTEXT"]

Now we'll create a class that inherits from both of them: 

.. code-block:: python

    class DefaultHeaderContextCustomClassView(DefaultHeaderBetterCustomClassView, DefaultContextBetterCustomClassView):
        pass

Let's do the MRO for the ``DefaultHeaderContextCustomClassView`` class:

Initially, the MRO will be the following:

.. code::

    Starting with the initial class 
    1. DefaultHeaderContextCustomClassView
    Follows the leftmost class MRO
    2. DefaultHeaderContextCustomClassView, 3. BetterCustomClassView, 4. CustomClassView, 5. object
    And finally the next class MRO
    6. DefaultContextBetterCustomClassView, 7. BetterCustomClassView, 8. CustomClassView, 9. object

Notice that classes ``BetterCustomClassView``, ``CustomClassView`` and ``object`` are repeated two times
(on place 3,4,5 and 7,8,9) thus *only* their last occurence will be kept in the list. So the
resulting MRO is the following:

``DefaultHeaderContextCustomClassView, DefaultHeaderBetterCustomClassView, DefaultContextBetterCustomClassView, BetterCustomClassView, CustomClassView, object``

So the ``DefaultHeaderContextCustomClassView`` *will* actually work properly because the 
``get_header`` will be found in ``DefaultHeaderBetterCustomClassView`` and the
``get_context`` will be found in ``DefaultContextBetterCustomClassView``. 

Yes it does work but at what cost? Do you really want to do the mental exercise
of finding out the MRO for each class you define? Also, what would happen if the 
``DefaultHeaderContextCustomClassView`` class also had a ``get_context`` method defined
(hint: that ``get_context`` would be used and the ``get_context`` of ``DefaultContextBetterCustomClassView``
would be ignored). 

That's why I
propose implementing common functionality that needs to be re-used between
classes only with mixins (hint: that's also what Django does). Each re-usable functionality
will be implemented in its own mixin - class views that need to implement that
functionality will just inherit from the mixin along with the class view. So each
one of the view classes you define should inherit from *one and only one* other class
view and any number of mixins you want. Make sure that the view class is righmost in
the ancestors list and the mixins are to the left so that they will properly override
its behavior). Keep in mind that the methods of the classes to the left override the methods of the
classes on the right -- and the methods of the defined class have of course the highest priority.

Let's try implementing the proposed mixins for a default header and context:

.. code-block:: python

    class DefaultHeaderMixin:
        def get_header(self, ):
            return self.header if self.header else "DEFAULT HEADER"

    class DefaultContextMixin:
        def get_context(self, ):
            return self.context if self.context else ["DEFAULT CONTEXT"]

and all the proposed use cases using the base class view and the mixins:

.. code-block:: python

    class DefaultHeaderMixinBetterCustomClassView(mixins.DefaultHeaderMixin, BetterCustomClassView):
        pass

    class DefaultContextMixinBetterCustomClassView(mixins.DefaultContextMixin, BetterCustomClassView):
        pass

    class DefaultHeaderContextMixinBetterCustomClassView(mixins.DefaultHeaderMixin, mixins.DefaultContextMixin, BetterCustomClassView):
        pass

    class JsonDefaultHeaderMixinCustomClassView(mixins.DefaultHeaderMixin, JsonCustomClassView):
        pass

I believe that the above definitions are self-documented and it is very easy to know which
method of the resulting class will be called each time: Start from the main class and if 
the method is not found there continue from left to right to the ancestor list.

The final thing and extension I'd like to discuss for our custom class based views is the case
where you want to use the functionality of more than one mixins. For example, let's suppose
that we had a mixin that added some data to the context and a different mixing that added
some different data to the context. Both would use the ``get_context`` method. 
How could we add implement these mixins and stay DRY? This is the same problem as 
if we wanted to inherit from a mixin (or a class view) and override one of its methods
but *also* call its parent (overriden) method for example to get its output and use it as the base
of the output for the overriden method.

Both of the above are more or less the same requirement because what stays in the end is
the MRO list. So, say we we had the following base clase

.. code::

    class V:pass

and we wanted to override it either using mixins or by using normal inheritance. 

Using mixins we'll have the following MRO:

.. code::

    class M1:pass
    class M2:pass
    class MIXIN(M2, M1, V):pass
    
    # MIXIN.mro()
    # [MIXIN, M2, M1, V, ]

and using inheritance we'll have the following MRO:

.. code::

    class M1V(V):pass
    class M2M1V(M1V):pass
    class INHERITANCE(M2M1V):pass
    
    # INHERITANCE.mro()
    # [INHERITANCE, M2M1V, M1V, V, ]

As we can see in both cases the base class V is the last one and between there are
the classes that define the extra (mixin) functionality: ``M2`` and ``M1`` (start from
left to right) in the first case and ``M2M1V`` and ``M1V`` (follow the inheritance hierarchy)
in the second case. So in both cases when calling a method they will be searched using
the MRO list and when the method is found it will be exetuted and the search will stop.

But what if we needed to re-use the functionality from ``V``? The answer to both cases is ``super``.

The ``super`` method can be used by a class to call a method of *its ancestors* respecting
the MRO. Thus, running ``super().x()`` from a method instance will try to find method ``x()``
on the MRO ancestors of this instance *even if the instance defines the ``x()`` method*. Notice
that if the ``x()`` method does not exist in the MRO chain you'll get an attribute error.

Let's take a look at how ``super()`` works by defining a method calld ``x()`` on all classes
of the previous example:

.. code-python::

    class V:
        def x(self):
            print ("From V")

    class M1:
        def x(self):
            super().x()
            print ("From M1")

    class M2:
        def x(self):
            super().x()
            print ("From M2")

    class MIXIN(M2, M1, V):
        def x(self):
            super().x()
            print ("From MIXIN")


    class M1V(V):
        def x(self):
            super().x()
            print ("From M1V")

    class M2M1V(M1V):
        def x(self):
            super().x()
            print ("From M2M1V")

    class INHERITANCE(M2M1V):
        def x(self):
            super().x()
            print ("From INHERITANCE")

    print ("MIXIN OUTPUT")
    MIXIN().x()

    print ("INHERITANCE OUTPUT")
    INHERITANCE().x()

Here's the output:

.. code:: 

    MIXIN OUTPUT
    From V
    From M1
    From M2
    From MIXIN
    INHERITANCE OUTPUT
    From V
    From M1V
    From M2M1V
    From INHERITANCE

A high level overview of CBVs
=============================

Real world use cases
====================




.. _`CBV inspector`: http://ccbv.co.uk`
.. _`request`: https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpRequest
.. _`response`: https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponse
