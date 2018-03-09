A comprehensive Django CBV guide
################################

:status: draft
:date: 2017-11-29 11:20
:tags: python, cbv, class-based-views, django
:category: django
:slug: comprehensive-django-cbv-guide
:author: Serafeim Papastefanos
:summary: A comprehensive guide to django CBVs - from neophyte to more advanced

.. contents:: :backlinks: none


Class Based Views (CBV) is one of my favourite things about Django. During my
first Django projects (using Django 1.4 around 6 years ago) I was mainly using
functional views -- that's what the tutorial recommended then anyway. However,
slowly in my next projects I started reducing the amount of functional views
and embracing CBVs, slowly understanding their usage and usefulness. Right now,
I more or less use only use CBVs for my views; even if sometimes it seems more work
to use a CBV instead of a functional one I know that sometime in the future I'd
be glad that I did it since I'll want to re-use some view functionality and 
CBVs are more or less the only way to have DRY views in Django.

I've heard various rants about them, mainly that they are too complex and difficult to 
understand and use, however I believe that they are easy to be understood when
you start from the basics and 
when they are used properly they will greatly improve your Django experience. Notice
that to properly understand CBVs you must have a good comprehension of how 
python's (multiple) inheritance and MRO work. Yes, this is a rather complex and
confusing thing but I'll try to also explain this as good as I can to the first chapter of this article.

This guide has three parts:

- A gentle introduction to how CBVs are working and to the the problems that do solve. For this we'll implement
  our own simple Custom Class Based View variant and take a look at python's inheritance model.
- A high level overview of the real Django CBVs using `CBV inspector`_ as our guide.
- A number of use cases where CBVs can be used to elegantly solve real world problems

A gentle introduction to CBVs
=============================

In this part of the guide we'll do a gentle introduction to (our own) class based views -
along with it we'll introduce some basic concepts of python (multiple) inheritance and how it applies to CBVs.

Before continuing, let's talk about the concept of the "view" in Django:
Traditionally, a view in Django is a normal python function that takes a single parameter,
the request_ object and must return a response_ object (notice that if the
view takes request parameters for example the id of an object to be edited
they will also be passed to the function). The responsibility of the
view function is to properly parse the request parameters and construct the
response object - as can be understood there is a lot of work that need to be
done for each view (for example check if the method is GET or POST, if the user
has access to that page, retrieve objects from the database, crate a context dict
and pass it to the template to be rendered etc). 

Now, since functional views are simple python functions it is *not* easy to override,
reuse or extend their behavior. There are more or less two methods for this: Use function
decorators or pass extra parameters when adding the view to your urls. I'd like
to point out here that there's a third method for code-reuse: Extracting 
functionality to common and re-usable functions or classes that will be called from the
functional views but this is not something specific to Django views but a general
concept of good programming style which you should follow anyway.

The first one uses `python decorators`_ to create a functional view that wraps the
initial one. The new view is called before the initial one, adds some functionality
(for example check if the current user has access, modify request parameters etc), 
calls the initial one which will return a response object, modify the response if needed
and then return that. This is how login_required_ works. Notice that by using
decorators you can change things before and after the original view runs but
you can't do anything about the way the view works.

For the second one you must
write your function view in a way which allows it to be reused, for example instead
of hard-coding the template name allow it to be passed by a parameter or instead
of using a specific form class for a form make it configurable through a parameter. Then,
when you add this function to your urls you will pass different parameters
depending on how you want to configure your view. Using this method you can
override the original function behavior however there's a limit to the number of
parameters you can allow your function views to hava and notice that these
function views cannot be further overrided.

It should be obvious that both these methods have severe limitations and do not allow you to be as DRY as
you should be. Using the wrapped views you can't actually
change the functionality of the original view (since that original function needs
to be called) but only do things before and after calling it. Also, using the
parameters will lead to spaghetti code with multiple if / else conditions in order
to take into account the various cases that may arise. All the above lead to
very reduced re-usability and DRYness of functional views - usually the best thing
you can do is to gather the common things in external normal python functions (not view functions) that could be
re-used from other functional views as already discussed.

Class based views solve the above problem of non-DRY-ness by using the well know
concept of OO inheritance: The view is defined from a class which has methods
for implementing the view functionality - you inherit from that class and override
the parts you want so the inherited class based view will use the overriden methods instead
of the original ones. You can also create re-usable classes (mixins) that offer a specific
functionality to your class based view by implementing some of the methods of the
original class. Each one of your class based views can inherit its functionality from
multiple mixins thus allowing you to define a single class for each thing you need
and re-using it everywhere. Notice of course that this is possible only if the
CBVs are properly implemented to allow overriding their functionality.

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

**Warning: The code in this post is written in Python 3.6 - that's why
the class is defined like this. If you wanted to follow along with Python 2.7
then you'd need to use new-style classes i.e the previous class would need
to be defined like CustomClassView(object ,).**

This class can be used to render a simple HTML template with a custom header and
a list in the body (named ``context``). There are two things to notice here: The ``__init__`` method (which
will be called as the object's constructor) will assign all the kwargs it receives
as instance attributes (for example ``CustomClassView(header='hello')`` will create
an instance with ``'hello'`` as its header attribute). The ``as_view`` is a classmethod
(i.e it can be called on the *class* without the need to instantiate an object) that
defines and returns a functional view that will be used to serve the view. The returned
functional view is very simple - it just instantiates a new instance of CustomClassView passing
the kwargs it got in the constructor and then returns a normal ``HttpResponse`` with
the instance's ``render()`` result. The ``render`` method will just output some html
using the instance's header and context to fill it.

Notice that the instance of the ``CustomClassView`` inside the ``_as_view`` is not created using
``CustomClassView(**kwargs)`` but using ``cls(**kwargs)`` - cls is the name of the
class that ``as_view`` was called on and actually passed as a parameter for
class methods (in a similar manner to how self is passed to instance methods).
This is important to instantiate an object instace of the proper class. 
For example, if you created a class that inherits from ``CustomClassView``
and called its ``as_view`` method then when you use the ``cls`` parameter to instantiate
the object it will correctly
create an object of the *inherited* class and not the *base* one.

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
so from now on any class based views I define will be added to urls py using ``ClassName.as_view()`` without any
parameters to the ``as_view()`` class method.

Let's now suppose that we wanted to allow our class based view to print something on the header even if no header is provided
when you configure it. The naive way to do it would be to re-define the ``render`` method and do something like

.. code-block:: python

    header=self.header if self.header else "DEFAULT HEADER"

in the ``render()`` method's format.
This is definitely not the DRY way to do it because you would need to re-define the whole ``render`` method. Think
what would happen if
you wanted to print ``"ANOTHER DEFAULT HEADER"`` as a default header for some other view - once again re-defining
``render``... In fact, the above
``CustomClassView`` is naively implemented because it does not allow proper customization through inheritance. The
same problems for the header arise also when you need modify the body; for
example, if you wanted to add an index number before displaying the items of the list then you'd need to again re-implement the
whole ``render`` method.

This is definitely not DRY. If that was our only option then we could just stick to functional views. However, we can do
much better if we define the class based view in such a way that allows inherited classes to override methods that
define specific parts of the functionality. To do this the class-based-view must be properly implemented so each 
part of its functionality is implemented by a differnet method. Here's how we could improve the ``CustomClassView``:

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
a ``get_context`` method that is used by ``render_context`` to make this CBV even
more re-usable. For example I may
need to configure the context (add/remove items from the context i.e have a CBV
that adds a last item with the numer of list itens to the list to be displayed). Of course this could
be done from ``render_context`` *but* this means that I would need to define my new functionality
(modifying the context items) *and* re-defining the context list formatting. It is much
better (in my opinion always) to keep properly seperated these things.

Now, the above is a first try that I created to mainly fulfill my requirement of
having a default header and some more examples I will discuss later (and keep
everything simple enough). You could
extract more functionality as methods-for-overriding, for example the render
method could be written like this:

.. code-block:: python

    def render(self):
        return self.get_template().format(
                header=self.get_header(), body=self.render_context(),
            )

and add a ``get_template`` method that will return the actual html template. There's no
hard rules here on what functionality should be extracted to a method (so it could
be overriden) however I recommend to follow the YAGNI rule (i.e implement everything
as normnal and when you see that some functionality needs to be overriden then refactor
your code to extract it to a separate method).

Let's see an example of adding the default header functionality by overriding ``get_header``:

.. code-block:: python

    class DefaultHeaderBetterCustomClassView(BetterCustomClassView, ):
        def get_header(self, ):
            return self.header if self.header else "DEFAULT HEADER"

Classes inheriting from ``DefaultHeaderBetterCustomClassView`` can choose to not
actually define a header attribute so ``"DEFAULT HEADER"`` will be printed instead. Keep in
mind that for ``DefaultHeaderBetterCustomClassView`` to be actually useful you'll need to
have more than one classes that need this default-header functionality (or else you could
just set the header attribute of your class to ``"DEFAULT HEADER"`` - this is not
user generated input, this is your source code!). All this will show how useful
it is when you consider more complex use-cases.

We have come now to a crucial point in this introduction, so please stick with me. Let's say that you have
*more than one* class based views that contain a header attribute. You want to include
the default header functionality on all of them so that if any view instantiated from these
class based views doesn't define a header
the default string will be output (I know that this may be a rather trivial example but I want
to keep everything simple to make following easy - instead of the default header the functionality
you want to override may be adding stuff to the context or filtering the objects you'll retrieve
from the database).

To re-use this default header funtionality from multiple classes you have *two* options:
Either inherit all classes that need this functionality from ``DefaultHeaderBetterCustomClassView`` or 
extract the custom ``get_header`` method to a *mixin* and inherit from the mixin. A mixin is a class not
related to the class based view hierarchy we are using - the mixin inherits from object (or from another
mixin) and just defines the methods and attributes that need to be overriden. So
the mixin will only define ``get_header`` and not all other methods like
``render``, ``get_context`` etc. Using the
``DefaultHeaderBetterCustomClassView`` may be enough for some cases but for the general case
you'll need to create the mixin. Let's see why:

Suppose that you have a base class that renders the header and context as JSON instead of the HTML
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

Notice that this class does not inherit from our previous hierarchy (i.e does not
inherit from BetterCustomClassView) but from object since it provides
its own ``as_view`` method. How could we re-use default header functionality
in this class (without having to re-implement it)? One solution would be to create a class that
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
correct one since the methods ``get_header`` and ``as_view`` exist in *both* ancestor classes so
in the first option (``JsonDefaultHeaderCustomClassView``) the ``get_header`` and ``as_view`` from ``JsonCustomClassView`` will be used while
in the second option (``DefaultHeaderJsonCustomClassView``) the ``get_header`` and ``as_view`` from ``DefaultHeaderBetterCustomClassView`` will
be used. Notice that if these classes had a common ancestor (for example they both used
``CustomClassView``) you may actually get the correct behavior depending on the rather complex rules
of python MRO (method resolution order). The MRO is also what I used to know which ``get_header``
and ``as_view`` will be used in each case in the previous example.

What is MRO? For every class that python sees, it tries to create a *list* (MRO list) of ancestor classes containing that class as 
the first element and its ancestors in a specific order I'll discuss right next after that. When a method
of an object of a specific class needs to be
called, then the method will be seached in the list (from the first element of the MRO list i.e. starting that class) - when a class is found
in the list that defines the method then that specific method (ie the method defined in this class) will be called and the search will stop (careful readers: I haven't
yet talked about *super* so please be patient). 

Now, how is the MRO list created? As I explained, the first element
is the class of the object. The second element is the MRO of the *leftmost* ancestor of that object (so MRO will 
run recursively on each ancenstor), the third element will be the MRO of the ancestor right next to the leftomost
ancestor etc. There is one extra and important rule: When a class is found multiple times in the MRO list (for example
if some elements have a common ancestor) then *only the last occurence in the list will be kept* - so each class
will exist only once in the MRO list. The above rule implies that the
rightmost element in every MRO list will always be object - please make sure you
understand why before continuing.

Thus, thwe MRO list for ``DefaultHeaderJsonCustomClassView`` is (remember, start
with the class to the left and add the MRO of each of its ancestors starting
from the leftmost one):
``[DefaultHeaderJsonCustomClassView, DefaultHeaderBetterCustomClassView, BetterCustomClassView, CustomClassView, JsonCustomClassView, object]``, while
for ``JsonDefaultHeaderCustomClassView`` is 
``[JsonDefaultHeaderCustomClassView, JsonCustomClassView, DefaultHeaderBetterCustomClassView, BetterCustomClassView, CustomClassView, object``

Let's try an example that has the same base class twice in the hierarchy. For this, we'll create a 
``DefaultContextBetterCustomClassView`` that returns a default context if the context is empty 
(similar to the default header functionality). 

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
    Follows the leftmost class (DefaultHeaderBetterCustomClassView) MRO
    2. DefaultHeaderContextCustomClassView, 3. BetterCustomClassView, 4. CustomClassView, 5. object
    And finally the next class (DefaultContextBetterCustomClassView) MRO
    6. DefaultContextBetterCustomClassView, 7. BetterCustomClassView, 8. CustomClassView, 9. object

Notice that classes ``BetterCustomClassView``, ``CustomClassView`` and ``object`` are repeated two times
(on place 3,4,5 and 7,8,9) thus *only* their last occurence will be kept in the list. So the
resulting MRO is the following:

``[DefaultHeaderContextCustomClassView, DefaultHeaderBetterCustomClassView, DefaultContextBetterCustomClassView, BetterCustomClassView, CustomClassView, object]``.

One funny thing here is that the ``DefaultHeaderContextCustomClassView`` *will actually work* properly because the 
``get_header`` will be found in ``DefaultHeaderBetterCustomClassView`` and the
``get_context`` will be found in ``DefaultContextBetterCustomClassView`` so this
result to the correct functionality.

Yes it does work but at what cost? Do you really want to do the mental exercise
of finding out the MRO for each class you define to see which method will be actually used? Also, what would happen if the 
``DefaultHeaderContextCustomClassView`` class also had a ``get_context`` method defined
(hint: that ``get_context`` would be used and the ``get_context`` of ``DefaultContextBetterCustomClassView``
would be ignored).

That's why I
propose implementing common functionality that needs to be re-used between
classes only with mixins (hint: that's also what Django does). Each re-usable functionality
will be implemented in its own mixin;  class views that need to implement that
functionality will just inherit from the mixin along with the base class view. Each
one of the view classes you define should inherit from *one and only one* other class
view and any number of mixins you want. Make sure that the view class is righmost in
the ancestors list and the mixins are to the left (so that they will properly override
its behavior; remember that the methods of the ancestors to the left are searched first
in the MRO list -- and the methods of the defined class have of course the highest priority
since it goes first in the MRO list).

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
where you want to use the functionality of more than one mixins for the same thing. For example, let's suppose
that we had a mixin that added some data to the context and a different mixing that added
some different data to the context. Both would use the ``get_context`` method
and you'd like to have the context data of both of them to your context. But
this is not possible using the implementations above because when a
``get_context`` is found in the MRO list it will be called and the MRO search
will finish there.

. 
So how could we add the functionality of both these mixins to a class based view? This is the same problem as 
if we wanted to inherit from a mixin (or a class view) and override one of its methods
but *also* call its parent (overriden) method for example to get its output and use it as the base
of the output for the overriden method. Both are the same because what stays in the end is
the MRO list. For example say we we had the following base class 

.. code::

    class V:pass

and we wanted to override it either using mixins or by using normal inheritance. 

Using mixins we'll have the following MRO:

.. code::

    class M1:pass
    class M2:pass
    class MIXIN(M2, M1, V):pass
    
    # MIXIN.mro()
    # [MIXIN, M2, M1, V, object, ]

and using inheritance we'll have the following MRO:

.. code::

    class M1V(V):pass
    class M2M1V(M1V):pass
    class INHERITANCE(M2M1V):pass
    
    # INHERITANCE.mro()
    # [INHERITANCE, M2M1V, M1V, V, object ]

As we can see in both cases the base class V is the last one and between there are
the classes that define the extra (mixin) functionality: ``M2`` and ``M1`` (start from
left to right) in the first case and ``M2M1V`` and ``M1V`` (follow the inheritance hierarchy)
in the second case. So in both cases when calling a method they will be searched using
the MRO list and when the method is found it will be exetuted and the search will stop.

But what if we needed to re-use some method from ``V`` (or from some other ancestor) and
a leftmost MRO class has the same method? 
The answer is ``super``.

The ``super`` method can be used by a class method to call a method of *its ancestors* respecting
the MRO. Thus, running ``super().x()`` from a method instance will try to find method ``x()``
on the MRO ancestors of this instance *even if the instance defines the ``x()`` method* i.e it will
not search the first element of the MRO list. Notice
that if the ``x()`` method does not exist in the headless-MRO chain you'll get an attribute error.

Let's take a closer look at how ``super()`` works using a simple example. For this, we'll define a method calld ``x()`` on all classes
of the previous example:

.. code-block:: python

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

Notice when each message is printed: Because x() first calls its ``super()`` method
and then it prints the message in both cases first the ``From V`` message is printed
from the base class and then from the following classes in the hierarch (as per the MRO)
ending with the class of the isntance (either ``MIXIN`` or ``INHERITANCE``).

Using super and mixins it is easy to mix and match functionality to create new
classes. Here's how we could add a prefix to
the header:

.. code-block:: python

    class HeaderPrefixMixin:
        def get_header(self, ):
            return "PREFIX: " + super().get_header()

and here's how it could be used:

.. code-block:: python

    class HeaderPrefixBetterCustomClassView(mixins.HeaderPrefixMixin, BetterCustomClassView):
        header='Hello!'

This will properly print the header displaying both PREFIX and Hello.
What if we wanted to re-use the default header mixin? First let's change ``DefaultHeaderMixin``
to properly use ``super()``:

.. code-block:: python

    class DefaultHeaderSuperMixin:
        def get_header(self, ):
            return super().get_header() if super().get_header() else "DEFAULT HEADER"

.. code-block:: python

    class HeaderPrefixDefaultBetterCustomClassView(mixins.HeaderPrefixMixin, mixins.DefaultHeaderSuperMixin, BetterCustomClassView):
        pass

Notice the order of the ancestor classes. The ``get_header()`` of  ``HeaderPrefixMixin`` will be called which
will call the ``get_header()`` of 
``DefaultHeaderSuperMixin`` (which will call the ``get_header()`` of ``BetterCustomClassView`` returning ``None``). 
So the result will be ``"PREFIX: DEFAULT HEADER"``. However if instead we had defined this class like

.. code-block:: python

    class HeaderPrefixDefaultBetterCustomClassView(mixins.DefaultHeaderSuperMixin, mixins.HeaderPrefixMixin, BetterCustomClassView):
        pass

the result would be ``"PREFIX: "`` (DEFAULT HEADER won't be printed). Can you understand why?

For another example of super, let's define a couple of mixins that add things to the context:

.. code-block:: python

    class ExtraContext1Mixin:
        def get_context(self, ):
            ctx = super().get_context()
            ctx.append('data1')
            return ctx


    class ExtraContext2Mixin:
        def get_context(self, ):
            ctx = super().get_context()
            ctx.insert(0, 'data2')
            return ctx

The first one retrieves the ancestor context list and appends ``'data1'`` to the 
it while the second one will insert ``'data2'`` to the start of the list. To use
these mixins just add them to the ancestor list of your class hierarchy as usually.
One interesting thing to notice here is that because of how ``get_context`` is
defined we'll get the same output no matter the order of the mixins in the hierarchy
since ``ExtraContext1Mixin`` will append ``data1`` to the end of the context list and
the ``ExtraContext2Mixin`` will insert ``data2`` to the start of the context list.

.. code-block:: python

    class ExtraContext12BetterCustomClassView(mixins.ExtraContext1Mixin, mixins.ExtraContext2Mixin, BetterCustomClassView):
        pass

    class ExtraContext21BetterCustomClassView(mixins.ExtraContext2Mixin, mixins.ExtraContext1Mixin, BetterCustomClassView):
        pass

If instead both of these mixins appended the item to the end of the list, then
the output would be different depending on the ancestor order.
Of course, since we've already defined ``HeaderPrefixMixin`` and ``DefaultHeaderSuperMixin`` nothing stops us
from using all those mixins together!

.. code-block:: python

    class AllTogetherNowBetterCustomClassView(
            mixins.HeaderPrefixMixin,
            mixins.DefaultHeaderSuperMixin,
            mixins.ExtraContext1Mixin,
            mixins.ExtraContext2Mixin,
            BetterCustomClassView
        ):
        pass

This will have the desired behavior!

A high level overview of CBVs
=============================

After the previous rather long (but I hope gentle enough) introduction to implementing
our own class based view hierarchy using inheritance, mixins, MRO, method overriding
and super we can now start talking about the Django Class Based Views (CBVs). Our
guide will be the `CBV inspector` application which displays all classes and mixins
that Django CBVs are using along with their methods and attributes. Using this application
and after reading this article you should be able to quickly and definitely know
which method or attribute you need to define to each one of your mixins or views.

To use CBV inspector, just click on a class name (for example ``CreateView``) - you will
immediately see its MRO ancestors, its list of attributes (and the ancestor class that defines
each one) and finally a list of methods that this class and all its ancestors define.
Of course when a method is defined by multiple classes the MRO ordering will be used - 
super is used when the functionality of the ancestor classes is also used. Unfortunately the CBV
inspector has Python 2 (and Django 1.11) syntax which has the following syntax to call super for method ``x()``:

.. code-block:: python

    super(ClassName, self).x()

this is the same as calling

.. code-block:: python

    super().x() 

in Python 3.x.

Taking a look at the ... View
-----------------------------

In any case, our travel starts from the central CBV class which is (intuitively) called ... View_!

This class is used as the base view in Django's CBV hierarchy (similar to how  ``CustomClassView``
was used in our own hierarchy). It has only one attribute
(``http_method_names``) and a very small number of methods. The most important method is the
``as_view`` class method (which is similar to the one we defined in the previous section).
The ``as_view`` will instatiate an instance object of the ``View`` class
(actually the class that inhhertis from ``View``) and use this object to properly generate a functional view.

The ``View`` class cannot be used as it is
but it must be inherited by a child class. The child class needs to define a method
that has the same name as each http method that is supported - for example if
only HTTP GET and HTTP POST are supported then the inherited class must define a
``get`` and a ``post`` method; these methods are called from the functional view
through a method called ``dispatch`` and need to return a proper response object. So,
we have two central methods here: The ``as_view`` class method that creates the
object instance and returns its view function and ``dispatch`` that will call 
the proper named class method depending on the HTTP method (i.e post, get, put
etc). One thing to keep from this discussion is that you shouldn't ever need to
mess with ``as_view`` but, because ``dispatch`` is the only instance method that is
guaranteed to run everytime the class based view will run, you will frequently 
need to override it especially to control authentication.

As an example, we can implemented the ``BetterCustomClassView`` from the first
section using ``View`` as its ancestor:

.. code-block:: python

    class DjangoBetterCustomClassView(View, ):
        header = ''
        context =''
        
        def get_header(self, ):
            return self.header if self.header else ""

        def get_context(self , ):
            return self.context if self.context else []

        def render_context(self):
            context = self.get_context()
            if context:
                return '<br />'.join(context)
            return ""

        def get(self, *args, **kwargs):
            resp = """
                <html>
                    <body>
                        <h1>{header}</h1>
                        {body}
                    </body>
                </html>
            """.format(
                    header=self.get_header(), body=self.render_context(),
                )
            return HttpResponse(resp)

This method won't print anything but of course it could use the mixins from
before to have some default values:

.. code-block:: python

    class DefaultHeaderContextDjangoBetterCustomClassView(DefaultHeaderMixin, DefaultContextMixin, DjangoBetterCustomClassView):
        pass

Of course instead of using our mixins and render methods it would be much better
to use the proper ones defined by Django - that's what we're going to do from
now on I just wanted to make clear that there's nothing special in Django's CBV
hiearchy and can be overriden as we'd like.

RedirectView and TemplateView
-----------------------------

Continuing our tour of Django CBVs I'd like to talk a little about the classes
that the CBV Inspector puts in the same level as ``View`` (GENERIC BASE):
RedirectView_ and TemplateView_. Both inherit directly from ``View`` and, the
first one defines a ``get`` method that returns a redirect to another page
while the latter one renders and returns a django template in the ``get``
method. 

The ``TemplateView`` however inherits from two more classes (actually
these are mixins) beyond ``View``: ``TemplateResponseMixin`` and
``ContextMixin``. If you take a look at them you'll see that the
``TemplateResponseMixin`` defines some template-related attributes and two
methods: One that retrieves the template that will be used to render this View
(``get_template_names``) 
and one that actually renders the template (``render_to_response``) using a
TemplateResponse_ instance. The
``ContextMixin`` on the other hand provides the ``get_context_data`` that is
passed to the template to be rendered and should be overriden if you want to
pass more context variables. 

We can already see many opportunities of reusing and overriding
functionality and improving our DRY score, for example: Create a catch all RedirectView
that depending on the remainder of the url it will redirect to a different page,
create a mixin that appends some things to the context of all CBVs using it, use dynamic templates
based on some other condition (that's actually what Detail/List/UpdateView
are doing), render a template to a different output than Html (for example a
text file). I'll try to present examples for these in the next section.

The FormView
------------

The next view we're going to talk about is FormView_. This is a view that can be
used whenever we want to display a form (*not* a form related to a Model i.e for
Create/Update/Delete, for these cases there are specific CBVs we'll see later). 
It is interesting to take a look at the list of its
ancestors: ``TemplateResponseMixin``, ``BaseFormView``, ``FormMixin``, ``ContextMixin``, ``ProcessFormView`` and ``View``.
We are familiar with TemplateResponseMixin, ContextMixin and View but not with
the others. Before discussing these classes let's take a look at the FormView
hierarchy, courtesy of http://ccbv.cco.uk and http://yuml.me:

.. raw:: html 

      <img src="https://yuml.me/diagram/plain;/class/[TemplateResponseMixin%7Bbg:white%7D]%5E-[FormView%7Bbg:green%7D],%20[BaseFormView%7Bbg:white%7D]%5E-[FormView%7Bbg:green%7D],%20[FormMixin%7Bbg:white%7D]%5E-[BaseFormView%7Bbg:white%7D],%20[ContextMixin%7Bbg:white%7D]%5E-[FormMixin%7Bbg:white%7D],%20[ProcessFormView%7Bbg:white%7D]%5E-[BaseFormView%7Bbg:white%7D],%20[View%7Bbg:lightblue%7D]%5E-[ProcessFormView%7Bbg:white%7D].svg" alt="FormView">

The above diagram should make everything easier: The ``FormMixin`` inherits
from ``ContextMixin`` and overrides its ``get_context_data`` method to add the
form. Beyond this, it adds some attributes and methods for proper form handling for
example ``form_class`` (attribute when the form class will be the same always) and 
``get_form_class()`` (method when the form class will be dynamic for example on
the logged in user), ``initial`` and ``get_initial()`` (same logic as before for
the form's initial values), ``form_valid()`` and ``form_invalid()`` to define
what should happen when the form is valid or invalid etc. Notice that FormMixin
does not define any form handling logic (i.e check if the form is valid and call
its ``form_valid()`` method) -- this logic is defined in the ``ProcessFormView``
which inherits from ``View`` and defines proper ``get()`` (just render the form)
and ``post()`` (check if the form is valid and call ``form_valid`` else call
``form_invalid``) methods. 

One interesting here is to notice here is that Django defines both the ``FormMixin`` and ``ProcessFormView``.
The ``FormMixin`` offers the basic Form elements (the form class, initial data
etc) and could be re-used in a different flow beyond the one offered by
``ProcessFormView`` (for example display the form as a JSON object instead of a
django template). On the other hand, ``ProcessFormView`` is required in order to
define the ``get`` and ``post`` methods that are needed from the ``View``. These
methods can't be overriden in the FormMixin since that would mean that the mixin
would behave as a view! 


Finally, the ``BaseFormView`` class is used to
inherit from ``ProcessFormView`` and ``FormMixin``. It does not do anything
more than providing a base class that other classes that want to use the form
functionality (i.e both the ``ProcessFormView`` and ``FormMixin``) will inherit from.

The ListView and DetailView
---------------------------

Next in our Django CBV tour is the ListView_. The ``ListView`` is used to render multiple
objects in a template, for example in a list or table. Here's a diagram of the class
hierarchy (courtesy of http://ccbv.cco.uk and http://yuml.me):

.. raw:: html 

    <img src="https://yuml.me/diagram/plain;/class/[MultipleObjectTemplateResponseMixin%7Bbg:white%7D]%5E-[ListView%7Bbg:green%7D],%20[TemplateResponseMixin%7Bbg:white%7D]%5E-[MultipleObjectTemplateResponseMixin%7Bbg:white%7D],%20[BaseListView%7Bbg:white%7D]%5E-[ListView%7Bbg:green%7D],%20[MultipleObjectMixin%7Bbg:white%7D]%5E-[BaseListView%7Bbg:white%7D],%20[ContextMixin%7Bbg:white%7D]%5E-[MultipleObjectMixin%7Bbg:white%7D],%20[View%7Bbg:lightblue%7D]%5E-[BaseListView%7Bbg:white%7D].svg" alt="ListView">

The ``MultipleObjectMixin`` is used make a query to the database (either using a
model or a queryset) and pass the results to the context. It also supports
custom ordering (``get_ordering()``) and pagination (``paginate_queryset()``).
However, the most important method of this mixin is ``get_queryset()``. This
method checks to see if the ``queryset`` or ``model`` attribute are defined
(``queryset`` will be checked first so it has priority of both are defined) and
returns a queryset result (taking into account the ordering). This queryset
result will be used by the ``get_context_data()`` method of this mixin to
actually put it to the context. The ``MultipleObjectMixin`` can be used and
overriden when we need to put multiple objects in a View. This mixin is
inherited (along with ``View``) from ``BaseListView`` that adds a proper ``get``
method to call ``get_context_data`` and pass the result to the template.

As we can also see, Django uses the ``MultipleObjectTemplateResponseMixin`` that
inherits from ``TemplateResponseMixin`` to render the template. This mixin does
some magic with the queryset or model so that it will automagically create a
template name (so you won't need to define it yourself) - that's from where the
``app_label/app_model_list.html`` default template name is created.

Similar to the ``ListView`` is the DetailView_ which has the same class hierarcy as the ``ListView`` with two differnces:
It uses ``SingleObjectMixin`` instead of ``MultipleOjbectMixin``,  
``SingleObjectTemplateResponseMixin`` instead of ``MultipleObjectTemplateResponseMixin``
and ``BaseDetailView`` instead of ``BaseListView``. The
``SingleObjectMixin`` will use the ``get_queryset()`` (in a similar manner to the ``get_queryset()`` of
``MultipleObjectMixin``) method to return a single object (so all attributes and methods
concerning ordering or pagination are missing) but instead has the ``get_object()`` method which
will pick and return a single object from that queryset (using a pk or slug parameter). This object
will be put to the context of this view by the ``get_context_data``. The ``BaseDetailView`` just
defines a proper ``get`` to call the ``get_context_data`` (of ``SingleObjectMixin``) and finally
the ``SingleObjectTemplateResponseMixin`` will automatically generate the template name (i.e generate
``app_label/app_model_detail.html``).

The CreateView
--------------

The next Django CBV we'll talk about is CreateView_. This class is used to create a new instance
of a model. It has a rather complex hierarchy diagram but we've already discussed most of these classes:

.. raw:: html 

      <img src="https://yuml.me/diagram/plain;/class/[SingleObjectTemplateResponseMixin%7Bbg:white%7D]%5E-[CreateView%7Bbg:green%7D],%20[TemplateResponseMixin%7Bbg:white%7D]%5E-[SingleObjectTemplateResponseMixin%7Bbg:white%7D],%20[BaseCreateView%7Bbg:white%7D]%5E-[CreateView%7Bbg:green%7D],%20[ModelFormMixin%7Bbg:white%7D]%5E-[BaseCreateView%7Bbg:white%7D],%20[FormMixin%7Bbg:white%7D]%5E-[ModelFormMixin%7Bbg:white%7D],%20[ContextMixin%7Bbg:white%7D]%5E-[FormMixin%7Bbg:white%7D],%20[SingleObjectMixin%7Bbg:white%7D]%5E-[ModelFormMixin%7Bbg:white%7D],%20[ContextMixin%7Bbg:white%7D]%5E-[SingleObjectMixin%7Bbg:white%7D],%20[ProcessFormView%7Bbg:white%7D]%5E-[BaseCreateView%7Bbg:white%7D],%20[View%7Bbg:lightblue%7D]%5E-[ProcessFormView%7Bbg:white%7D].svg" />

As we can see the ``CreateView`` inherits from ``BaseCreateView`` and ``SingleObjectTemplateResponseMixin``. The
``SingleObjectTemplateResponseMixin`` is mainly used to automagically create the template names that will be seached for
(i.e ``app_label/app_model_form.html``), while the ``BaseCreateView`` 
is used to combine the functionality of ``ProcessFormView`` (that handles the basic form workflow as we have
already discussed) and ``ModelFormMixin``. The ``ModelFormMixin`` is a rather complex mixin that inherits from
both ``SingleObjectMixin`` and ``FormMixin``. The ``SingleObjectMixin`` functionality is not really used by ``CreateView`` 
(since no object will need to be retrieved for the ``CreateView``) however the ``ModelFormMixin`` is also used
by ``UpdateView`` that's why ``ModelFormMixin`` also inherits from it. This mixin adds functionality
for handling forms related to models and object instances. More specifically it adds functionality for
* creating a form class (if one is not provided) by the configured model / queryset 
* overrides the ``form_valid`` in order to save the object instance of the form
* fixes ``get_success_url`` to redirect to the saved object's absolute_url when the object is saved
* pass the current object (if it has one - CreateView does not for example) to the form as the ``instance`` attribute

The UpdateView and DeleteView
-----------------------------

The UpdateView_ class is almost identical to the ``CreateView`` - the only difference is that 
``UpdateView`` inherits from ``BaseUpdateView`` (and ``SingleObjectTemplateResponseMixin``) instead
of ``BaseCreateView``.  The ``BaseUpdateView`` overrides the ``get`` and ``post`` methods of
``ProcessFormView`` to retrieve the object (using ``SingleObjectMixin``'s ``get_object()``) 
and assign it to an instance variable - this will then be picked up by the ``ModelFormMixin`` and used
properly in the form as explained before. One thing I notice here is that probably the hierarchy would
be better if the ``ModelFormMixin`` inherited *only* from ``FormMixin`` (instead of both from
``FormMixin`` and ``SingleObjectMixin``) and ``BaseUpdateView`` inheriting from ``ProcessFormView``,
``ModelForMixin`` *and* ``SingleObjectMixin``. This way the ``BaseCreateView`` wouldn't get the
non-needed ``SingleObjectMixin`` functionality. I am not sure why Django is implemented this way
(i.e the ``ModelFormMixin`` also inheriting from ``SingleObjectMixin`` thus passing this non-needed
functionality to ``BaseCreateView``) -- if a reader has a clue I'd like to know it. 

In any way, I'd like to also present the DeleteView_ which is more or less the same as the DetailView_
with the addition of the ``DeleteMixin`` in the mix. The ``DeleteMixin`` adds a ``post()`` method
that will delete the object when called and makes success_url required (since there would be no
object to redirect to after this view is posted).

Access control mixins
---------------------

Another small hierarchy of class based views (actually these are all mixins) are the authentication ones which
can be used to control acccess to a view.
These are ``AcessMixin``, ``LoginRequiredMixin``, ``PermissionRequiredMixin`` and ``UserPassesTestMixin``.
The ``AccessMixin`` provides some basic functionality (i.e what to do when the user does not have access
to the view, find out the login url to redirect him etc) and is used as a base for the other three. These
three override the ``dispatch()`` method of ``View`` to check if the user has the specific rights (i.e
if he has logged in for ``LoginRequiredMixin``, if he has the defined permissions for ``PermissionRequiredMixin``
or if he passes the provided test in ``UserPassesTextMixin``). If the user has the rights the view will procceed
as normally (call super's dispatch) else the access denied functionality from ``AccessMixin`` will be implemented.

Some other CBVs
---------------

Beyond the class based views I discussed in this section, Django also has a bunch of CBVs related
to account views (``LoginView``, ``LogoutView``, ``PasswordChangeView`` etc) and Dates (``DateDetailView``, ``YearArchiveView`` etc).
I won't go into detail about these since they follow the same concepts and use most of the mixins
we've discussed before. Using the CBV Inspector you should be able to follow along and decide the methods you need
to override for your needs.



Real world use cases
====================

In this section I am going to present a number of use cases demonstrating the usefulness of Django CBVs. In most of
these examples I am goint to override one of the methods of the mixins I discussed in the previous section. There
are *two* methods you can use for integrating the following use cases to your application.

Create your own class inheriting from one of the Django CBVs and add to it directly the method to override. For example, 
if you wanted to override the ``get_queryset()`` method a ``ListView`` you would do a:

.. code-block:: python

    class GetQuerysetOverrideListView(ListView):
        def get_queryset(self):
            qs = super().get_queryset()
            return qs.filter(status='PUBLISHED')

This is useful if you know that you aren't going to need the overriden ``get_queryset`` functionality to a different
method and following the YAGNI principle. However, if you know that there may be more CBVs that would need their
queryset filtered by ``status='PUBLISHED'`` then you should add a mixin that would be used by your CBVs:

.. code-block:: python

    class GetQuerysetOverrideMixin:
        def get_queryset(self):
            qs = super().get_queryset()
            return qs.filter(status='PUBLISHED')

    class GetQuerysetOverrideListView(GetQuerysetOverrideMixin, ListView):
        pass

Now, one thing that needs some discussion here is that the method ``get_queryset`` is provided by a mixin (in fact
it is provided by two mixins: ``MultipleObjectMixin`` for ``ListView`` and ``SingleObjectMixin`` for ``DetailView``,
``UpdateView`` and ``DeleteView``). Because of how MRO works, I won't need to inhert ``GetQuerysetOverrideMixin`` from
``MultipleObjectMixin`` (or ``SingleObjectMixin`` but let's ignore that for now) but I can just inherit from object
and make sure that, as already discussed, put the mixin *before* (to the left) of the CBV. Notice that even if I had
defined ``GetQuerysetOverrideMixin`` as ``GetQuerysetOverrideMixin(MultipleObjectMixin)`` the ``MultipleObjectMixin`` class would
be found *twice* in the MRO list so only the rightmost instance would remain. So the MRO for both ``GetQuerysetOverrideMixin(object, )``
and ``GetQuerysetOverrideMixin(MultipleObjectMixin)`` *would be the same*! Also, inheriting directly from object makes
our ``GetQuerysetOverrideMixin`` more DRY since if it inherited from ``MultipleObjectMixin`` we'd need to create *another*
version of it that would inherit from ``SingleObjectMixin``; this is because ``get_queryset`` exists in both these mixins.

For some of the following use cases I am also going to use the following models for user generated content (articles and uploaded files):

.. code-block:: python

    STATUS_CHOICES = (
        ('DRAFT', 'Draft', ),
        ('PUBLISHED', 'Published', ),
        ('REMOVED', 'Removed', ),
    )


    class Category(models.Model):
        name = models.CharField(max_length=128, )


    class AbstractGeneralInfo(models.Model):
        category = models.ForeignKey('category', on_delete=models.PROTECT, )
        created_on = models.DateTimeField(auto_now_add=True, )
        created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_created_by', )
        modified_on = models.DateTimeField(auto_now=True, )
        modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_modified_by', )
        published_on = models.DateTimeField(blank=True, null=True)

        class Meta:
            abstract = True


    class Article(AbstractGeneralInfo):
        title = models.CharField(max_length=128, )
        content = models.TextField()


    class Document(AbstractGeneralInfo):
        description = models.CharField(max_length=128, )
        file = models.FileField()

Auto-fill created_by and modified_by
------------------------------------

The ``Article`` and ``Document`` models which both inherit (abstract) from ``AbstractGeneralInfo`` have a ``created_by`` and
a ``modified_by`` field. These fields have to be filled automatically from the current logged in user. Now, there are various
options to do that but what I vote for is using an ``AuditableMixin`` as I have already described in `my Django model auditing article`_.

To replicate the functionality we'll create the ``AuditableMixin`` like this:

.. code-block:: python

    class AuditableMixin(object,):
        def form_valid(self, form, ):
            if not form.instance.created_by:
                form.instance.created_by = self.request.user
            form.instance.modified_by = self.request.user
            return super().form_valid(form)

This mixin can be used by both the create and update view of both ``Article`` and ``Document``. So all four of these
classes will share the same functionality. Notice that the ``form_valid`` method is overriden - the ``created_by`` 
of the form's instance (which is the object that was edited, remember how ``ModelFormMixin`` works) will by set
to the current user if it is null (so it will be only set once) while the ``modified_by`` will be set always to the
current user. Finally we call ``super().form_valid`` and return its response so
that the form will be actually saved and the redirect will go to the proper success url. To use it for example for the
``Article``, ``CreateView`` should be defined like this:

.. code-block:: python

    class ArticleCreateView(AuditableMixin, CreateView):
        class Meta:
            model = Article


Allow each user to list/view/edit/delete only his own items
-----------------------------------------------------------

Let's suppose that we want to create a managerial backend where each user would be able to list the items (articles and
documents) he has created and view/edit/delete them. We also want to allow superusers to view/edit everything.

Since the ``Article`` and ``Document`` models both have a ``created_by`` element we can use use this to filter
the results returned by ``get_queryset()``. Here's how this mixin could be implemented:


.. code-block:: python

    class LimitAccessMixin:
        def get_queryset(self):
            qs = super().get_queryset()
            if self.request.user.is_superuser:
                return qs
            return qs.filter(created_by=self.request.user)


Configure the form's initial values from GET parameters
-------------------------------------------------------

Sometimes we want to have a ``CreateView`` with some fields already filled. I usually
implement this by passing the proper parameters to the queryset and then using the following
mixin to generate the form's initial data from it:

.. code-block:: python

    class SetInitialMixin(object,):
        def get_initial(self):
            initial = super(SetInitialMixin, self).get_initial()
            initial.update(self.request.GET.dict())
            return initial

So if the /article_create url can be used to initialte the ``CreateView`` for the article,
using ``/article_create?category_id=3`` will show the CreateView with the Category with id=3
pre-selected in the category field.

Pass extra kwargs to the FormView form
--------------------------------------

This is a very common requirement. The form may need to be modified by an external condition,
for example the current user or something that can be calculated from the view. Here's a
sample mixin that passes the current request (which also includes the user) to the form:

.. code-block:: python

    class RequestArgMixin:
        def get_form_kwargs(self):
            kwargs = super(RequestArgMixin, self).get_form_kwargs()
            kwargs.update({'request': self.request})
            return kwargs

Please notice that the form has to properly handle the extra kwarg in its constructor,
before calling the super's constructor. For
example, here's how a form that can accept the request could be implemented:

.. code-block:: python

    class RequestForm(forms.Form):
        def __init__(self, *args, **kwargs):
            self.request = kwargs.pop('request', None)
            super().__init__(*args, **kwargs)

We use ``pop`` to remove the request from the received ``kwargs`` and only then we call the 
parent constructor.

Add values to the context
-------------------------

To add values to the context of a CBV we override the ``get_context_data()`` method. Here's
a mixin that adds a list of categories to all CBVs using it:

.. code-block:: python

    class CategoriesContextMixin:
        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['categories'] = Category.objects.all()
            return ctx

Notice that the mixin calls super to get the context data of its ancestors and appends to it. This
mean that if we also had a mixin that f.e added the current logged in user to the context (this isn't really
needed since there's a context processor for this but anyway) then when a CBV inherited from both of
them then the data of both of them would be added to the context.

As a general comment there are three other methods the same functionality could be achieved:

* Just override the ``get_context_data`` of the CBV you want to add extra data to its context
* Add a template tag that will bring the needed data to the template
* Use a context processor to bring the data to all templates

As can be understood, each of the above methods has certain advantages and disadvantages. For
example, if the extra data will query the database then the context processor method will add
one extra query for all page loads (even if the data is not needed). On the other hand,
the template tag will query the database only on specific views but it makes debugging and 
reasoning about your template more difficult since if you have a lot of template tags you'll have 
various context variables appearing from thing air!

Support for success messages
----------------------------

Django has a very useful `messages framework`_ which can be used to add flash messages
to a view. A flash message is a message that persists in the sesion until it is viewed
by the user. So, for example when a user edits an object and saves it, he'll be redirected
to the success page - if you have configured a flash message to inform the user that the 
save was ok then he'll see this message once and then if he reloads the page it will
be removed.

Here's a mixin that can be used to support flash messages using Django's message framework:

.. code-block:: python

    class SuccessMessageMixin:
        success_message = ''

        def get_success_message(self):
            return self.success_message

        def form_valid(self, form):
            messages.success(self.request, self.get_success_message())
            return super().form_valid(form)

This mixin overrides the ``form_valid`` and adds the message using ``get_success_message`` - this
can be overriden if you want to have a dynamic message or just set the ``success_message`` attribute
for a static message, for example something like this:

.. code-block:: python

    class SuccesMessageArticleCreateView(SuccessMessageMixin, CreateView):
        success_message = 'Object was created!'

        class Meta:
            model = Article

I'd like to once again point out here that since the ``super().form_valid(form)`` method is properly used
then if a CBV uses multiple mixins that override form_valid (for example if your CBV overrides both
``SuccessMessageMixin`` and ``AuditableMixin`` then the form_valid of *both* will be called so you'll
get both the created_by/modified_by values set to the current user and the success message!

Notice that Django actually provides an implementation of `a message mixin`_ which can be used instead
of the proposed implementation here (I didn't know it until recently that's why I am using this to some
projects and I also present it here).

Implement moderation
--------------------

It is easy to implement some moderation to our model publishing. For example, let's suppose that we only
allow publishers to publish a model. Here's how it can be done:

.. code-block:: python

    class ModerationMixin:
        def form_valid(self, form):
            redirect_to = super().form_valid(form)
            if self.object.status != 'REMOVED':
                if self.request.user.has_perm('spots.publisher_access'):
                    self.object.status = 'PUBLISHED'
                else:
                    self.object.status = 'DRAFT'
                self.object.save()
                
            return redirect_to
            
So, first of all we call the parent ``form_valid`` to properly save the form and save
the redirect to value. We then make sure that the object is not ``REMOVED`` (if it is
remove it we don't do anything else). Next we check if the current user has 
``publisher_access`` if yes we change the object's status to ``PUBLISHED`` - on any
other case we change its status to ``DRAFT``. Notice that this means that whenever a
publisher saves the object it will be published and whenever a non-publisher saves it
it will be made a draft. 

I'd like to repeat here that this mixin, since it calls super, can work concurrently
with any other mixins that override ``form_valid`` (and also call their super method
of course), for example it can be used together with the audit (auto-fill created_by
and moderated_by) and the success mixins we defined previously!


Allow access to a view if a user has one out of a group of permissions
----------------------------------------------------------------------

For this we'll need to use the authentication mixins functionality. We could implement 
this by overriding ``PermissionRequiredMixin`` or by overriding ``UserPassesTestMixin``.

Using ``PermissionRequiredMixin`` is not very easy because the way it works
it will allow access if the user has *all* permissions from the group (not only one as is the requirement). 
Of course you could override its ``has_permission`` method to change the way it checks if
the user has the permissions (i.e make sure it has one permission instead of all):

.. code-block:: python

    class AnyPermissionRequiredMixin(PermissionRequiredMixin, ):
        def has_permission(self):
            perms = self.get_permission_required()
            return any(self.request.user.has_perm(perm) for perm in perms)

Also we could implement our mixin using ``UserPassesTestMixin`` as its base:

.. code-block:: python

    class AnyPermissionRequiredAlternativeMixin(UserPassesTestMixin):
        permissions = []

        def test_func(self):
            return any(self.request.user.has_perm(perm) for perm in self.permissions)


The functionality is very simple: If the user has one of the list of the configured permissions then the test will pass (so he'll have access to the view).
If instead the user has none of the permissions then he won't be able to access the view.            
            
Notice that for the above implementations we inherited from ``PermissionRequiredMixin`` or ``UserPassesTextMixin`` to keep their functionality - if we had inherited
these mixins from object then we'd need to inherit our CBVs from both ``AnyPermissionRequiredMixin`` and ``PermissionRequiredMixin`` or 
``AnyPermissionRequiredAlternativeMixin`` and ``UserPassesTestMixin`` (with the correct MRO order of course).


Now, the whole permission cheking functionality can be even more DRY. Let's suppose that we know that there are a couple of views which should only
be visible to users having either the ``app.admin`` or ``app.curator`` permission. Instead of inheriting all these views from ``AnyPermissionRequiredMixin``
and configuring the permissions list to each one, the DRY way to implement this is to add yet another mixin from which the CBVs will actually inhert:

.. code-block:: python

    class AdminorUserPermissionRequiredMixin(AnyPermissionRequiredMixin):
        permissions = ['app.admin', 'app.curator']


Disable a view based on some condition
--------------------------------------

There are times you want to disable a view based on an arbitrary condition - for example example make the view
disabled before a specific date. Here's a simple mixin that overrides ``dispatch`` to do this:

.. code-block:: python

    class DisabledDateMixin(object, ):
        the_date = datetime.date(2018,1,1)
        
        def dispatch(self, request, *args, **kwargs):
            if datetime.date.today() < the_date:
                raise PermissionDenied
            return super().dispatch(request, *args, **kwargs)
            
You can even disable a view completely  in case you want to keep it in your urls.py using this mixin:

.. code-block:: python

    class DisabledDateMixin(object, ):
        def dispatch(self, request, *args, **kwargs):
            raise PermissionDenied

Output a view as a PDF
----------------------

It is very easy to create a mixin that will output a view to PDF - I have already written
an `essential guide for outputting PDFs in Django`_ so I am just going to refer you to this article for
(much more) information!

Create a catch all RedirectView
-------------------------------

Using dynamic templates
-----------------------

Add a dynamic filter to the context
-----------------------------------


.. _`CBV inspector`: http://ccbv.co.uk`
.. _`request`: https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpRequest
.. _`response`: https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponse
.. _View: https://ccbv.co.uk/View
.. _`python decorators`: https://wiki.python.org/moin/PythonDecorators
.. _login_required: https://docs.djangoproject.com/en/2.0/topics/auth/default/#the-login-required-decorator
.. _RedirectView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/base/#redirectview
.. _TemplateView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/base/#templateview
.. _TemplateResponse: https://docs.djangoproject.com/en/2.0/ref/template-response/#django.template.response.TemplateResponse
.. _FormView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-editing/#formview
.. _ListView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-display/#listview
.. _DetailView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-display/#detailview
.. _CreateView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-display/#createview
.. _UpdateView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-display/#updateview
.. _DeleteView: https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-display/#deleteview
.. _`my Django model auditing article`: https://spapas.github.io/2015/01/21/django-model-auditing/#adding-simple-auditing-functionality-ourselves
.. _`messages framework`: https://docs.djangoproject.com/en/2.0/ref/contrib/messages/
.. _`a message mixin`: https://docs.djangoproject.com/en/2.0/ref/contrib/messages/#adding-messages-in-class-based-views
.. _`essential guide for outputting PDFs in Django`: https://spapas.github.io/2015/11/27/pdf-in-django/#using-a-cbv 
 
