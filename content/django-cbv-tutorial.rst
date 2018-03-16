A comprehensive Django CBV guide
################################

:status: draft
:date: 2018-03-15 12:20
:tags: python, cbv, class-based-views, django
:category: django
:slug: comprehensive-django-cbv-guide
:author: Serafeim Papastefanos
:summary: A comprehensive guide to Django CBVs - from neophyte to more advanced

.. contents:: :backlinks: none


Class Based Views (CBV) is one of my favourite things about Django. During my
first Django projects (using Django 1.4 around 6 years ago) I was mainly using
functional views -- that's what the tutorial recommended then anyway. However,
slowly in my next projects I started reducing the amount of functional views
and embracing CBVs, slowly understanding their usage and usefulness. Right now,
I more or less only use CBVs for my views; even if sometimes it seems more work
to use a CBV instead of a functional one I know that sometime in the future I'd
be glad that I did it since I'll want to re-use some view functionality and
CBVs are more or less the only way to have DRY views in Django.

I've heard various rants about them, mainly that they are too complex and difficult to
understand and use, however I believe that they are not really difficult when
you start from the basics. Even if it is a little work to become comfortable with
the CBV logic, when they are used properly they will greatly improve your Django experience
so it is definitely worth it.

Notice
that to properly understand CBVs you must have a good understanding of how
Python's (multiple) inheritance and MRO work. Yes, this is a rather complex and
confusing thing but I'll try to also explain this as good as I can to the first chapter
of this article so if you follow along you shouldn't have any problems.

This guide has four parts:

- A gentle introduction to how CBVs are working and to the the problems that do solve. For this we'll implement
  our own simple Custom Class Based View variant and take a look at python's inheritance model.
- A high level overview of the real Django CBVs using `CBV inspector`_ as our guide.
- A number of use cases where CBVs can be used to elegantly solve real world problems
- Describing the usage of some of the previous use cases to a real Django application

I've implemented an accompanying project to this article which you can find at https://github.com/spapas/cbv-tutorial.
This project has two separate parts. One that is the implementation of the Custom Class Based View variant
to see how it is working and the other is the application that contains the usage of the various CBV use cases.

A gentle introduction to CBVs
=============================

In this part of the guide we'll do a gentle introduction to how CBVs work by implementing
our own class based views variant - along with it we'll introduce and try to understand
some concepts of  python (multiple) inheritance and how it applies to CBVs.

Before continuing, let's talk about the concept of the "view" in Django:
Django is considered an MVT (Model View Template) framework - the View as
conceived by Django is not the same as the MVC-View. A Django View is more or
less a way to define the data that the Template (which is cloased to the MVC-View)
will display, so the Django View (with the help of the Django Framework) is similar
to the MVC-Controller.

In any case, traditionally a view in Django is a normal python function that takes a single parameter,
the request_ object and must return a response_ object (notice that if the
view uses request parameters for example the id of an object to be edited
they will also be passed to the function). The responsibility of the
view function is to properly parse the request parameters and construct the
response object - as can be understood there is a lot of work that need to be
done for each view (for example check if the method is GET or POST, if the user
has access to that page, retrieve objects from the database, crate a context dict
and pass it to the template to be rendered etc).

Now, since functional views are simple python functions it is *not* easy to override,
reuse or extend their behaviour. There are more or less two methods for this: Use function
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
you can't do anything about the way the original view works.

For the second one (adding extra view parameters) you must
write your function view in a way which allows it to be reused, for example instead
of hard-coding the template name allow it to be passed as a parameter or instead
of using a specific form class for a form make it configurable through a parameter. Then,
when you add this function to your urls you will pass different parameters
depending on how you want to configure your view. Using this method you can
override the original function behaviour however there's a limit to the number of
parameters you can allow your function views to have and notice that these
function views cannot be further overridden. The login_ authentication view (which
is now deprecated in favour of a CBV one)
is using this technique, for example you can pass it
the template name that will be used, a custom authentication form etc.

It should be obvious that both these methods have severe limitations and do not allow you to be as DRY as
you should be. When using the wrapped views you can't actually
change the functionality of the original view (since that original function needs
to be called) but only do things before and after calling it. Also, using the
parameters will lead to spaghetti code with multiple if / else conditions in order
to take into account the various cases that may arise. All the above lead to
very reduced re-usability and DRYness of functional views - usually the best thing
you can do is to gather the common things in external normal python functions (not view functions) that could be
re-used from other functional views as already discussed.

Class based views solve the above problem of non-DRY-ness by using the well known
concept of OO inheritance: The view is defined from a class which has methods
for implementing the view functionality - you inherit from that class and override
the parts you want so the inherited class based view will use the overridden methods instead
of the original ones. You can also create re-usable classes (mixins) that offer a specific
functionality to your class based view by implementing some of the methods of the
original class. Each one of your class based views can inherit its functionality from
multiple mixins thus allowing you to define a single class for each thing you need
and re-using it everywhere. Notice of course that this is possible only if the
CBVs are *properly implemented* to allow overriding their functionality. We'll see
how this is possible in the next section.

Hand-made CBVs
--------------

To make things more clear we'll start implementing our own class based views hierarchy. Here's
a rather naive first try:

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
a list of items in the body (named ``context``). There are two things to notice here: The ``__init__`` method (which
will be called as the object's constructor) will assign all the keyword arguments (``kwargs``) it receives
as instance attributes (for example ``CustomClassView(header='hello')`` will create
an instance with ``'hello'`` as its ``header`` attribute). The ``as_view`` is a class method
(i.e it can be called directly on the *class* without the need to instantiate an object
for example you can call ``CustomClassView.as_view()`` ) that
defines and returns a traditional functional view (named ``view``) that will be used to
actually serve the view. The returned
functional view is very simple - it just instantiates a new instance (object)
of ``CustomClassView`` passing
the ``kwargs`` it got in the constructor and then returns a normal ``HttpResponse`` with
the instance's ``render()`` result. This ``render()`` method will just output some html
using the instance's header and context to fill it.

Notice that the instance of the ``CustomClassView`` inside the ``as_view`` class method
is not created using
``CustomClassView(**kwargs)`` but using ``cls(**kwargs)`` - ``cls`` is the name of the
class that ``as_view`` was called on and is actually passed as a parameter for
class methods (in a similar manner to how ``self`` is passed to instance methods).
This is important to instantiate an object instance of the proper class.

For example, if you created a class that inherited from ``CustomClassView``
and called its ``as_view`` method then when you use the ``cls`` parameter to instantiate
the object it will correctly create an object of the *inherited* class and not the *base* one
(if on the other hand you had used ``CustomClassView(**kwargs)`` to instantiate the instance
then the ``as_view`` method of the inheriting classes would instantiate instances of
``CustomClassView`` so inheritance wouldn't really work!).

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
with the object's ``render()`` reuslts. To add some output we can either
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

The above will create a ``CustomClassView`` instance with the provided values as its attributes.

Although this method of configuration is used in normal django CBVs (for example
setting the ``template_name`` in a ``TemplateView``) I recommend you avoid using it because passing parameters
to the ``as_view`` method pollutes the urls.py with configuration
that (at least in my opinion) should *not* be there (and there's no reason to have to take a look at both
your urls.py and your views.py to understand the behavior of your views) and also, even for very simple views I know that after some time I'll need
to add some functionality that cannot be implemented by passing the parameters so I prefer to bite the
bullet and define all my views as inherited classes so it will be easy for me to further customize them later (we'll
see how this is done in a second). Thus, even if you have

In any case, I won't discuss passing parameters to the ``as_view`` method any more,
so from now on any class based views I define will be added to urls py using ``ClassName.as_view()`` without any
parameters to the ``as_view()`` class method.

Is this really DRY ?
--------------------

Let's now suppose that we wanted to allow our class based view to print something on the header even if no header is provided
when you configure it. The only way to do it would be to re-define the ``render`` method like this:

.. code-block:: python

    def render(self):
        header=self.header if self.header else "DEFAULT HEADER"
        return """
            <html>
                <body>
                    <h1>{header}</h1>
                    {body}
                </body>
            </html>
        """.format(
                header=header, body='<br />'.join(self.context),
            )

This is definitely not the DRY way to do it because you would need to re-define the whole ``render`` method. Think
what would happen if
you wanted to print ``"ANOTHER DEFAULT HEADER"`` as a default header for some other view - once again re-defining
``render``! In fact, the above
``CustomClassView`` is naively implemented because it does not allow proper customization through inheritance. The
same problems for the header arise also when you need modify the body; for
example, if you wanted to add an index number before displaying the items of the list then you'd need to again re-implement the
whole ``render`` method.

If that was our only option then we could just stick to functional views. However, we can do
much better if we define the class based view in such a way that allows inherited classes to override methods that
define specific parts of the functionality. To do this the class-based-view must be properly implemented so each
part of its functionality is implemented by a different method.

Here's how we could improve the ``CustomClassView`` to make it more DRY:

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
``as_view`` method which doesn't need changing. Beyond this, the render
uses methods (``get_header`` and ``render_context``) to retrieve the values from the header and the body - this means
that we could re-define these methods to an inherited class in order to override
what these methods will return. Beyond ``get_header`` and ``render_contex`` I've added
a ``get_context`` method that is used by ``render_context`` to make this CBV even
more re-usable. For example I may
need to configure the context (add/remove items from the context i.e have a CBV
that adds a last item with the number of list items to the list to be displayed). Of course this could
be done from ``render_context`` *but* this means that I would need to define my new functionality
(modifying the context items) *and* re-defining the context list formatting. It is much
better (in my opinion always) to keep properly separated these things.

Now, the above is a first try that I created to mainly fulfil my requirement of
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
be overridden) however I recommend to follow the YAGNI rule (i.e implement everything
as normal and when you see that some functionality needs to be overridden then refactor
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
user generated input, this is your source code!).

Re-using view functionality
---------------------------

We have come now to a crucial point in this chapter, so please stick with me. Let's say that you have
*more than one* class based views that contain a header attribute. You want to include
the default header functionality on all of them so that if any view instantiated from these
class based views doesn't define a header
the default string will be output (I know that this may be a rather trivial example but I want
to keep everything simple to make following easy - instead of the default header the functionality
you want to override may be adding stuff to the context or filtering the objects you'll retrieve
from the database).

To re-use this default header functionality from multiple classes you have *two* options:
Either inherit all classes that need this functionality from ``DefaultHeaderBetterCustomClassView`` or
extract the custom ``get_header`` method to a *mixin* and inherit from the mixin. A mixin is a class not
related to the class based view hierarchy we are using - the mixin inherits from object (or from another
mixin) and just defines the methods and attributes that need to be overridden. When the mixin is *mixed*
with the ancestors of a class its functionality will be used by that class (we'll see how shortly). So
the mixin will only define ``get_header`` and not all other methods like
``render``, ``get_context`` etc. Using the
``DefaultHeaderBetterCustomClassView`` is enough for some cases but for the general case
of re-using the functionality you'll need to create the mixin. Let's see why:

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
    class DefaultHeaderJsonCustomClassView(DefaultHeaderBetterCustomClassView, JsonCustomClassView):
        pass

    # OR
    # OPTION 2
    class JsonDefaultHeaderCustomClassView(JsonCustomClassView, DefaultHeaderBetterCustomClassView):
        pass


What will happen here? Notice that the methods ``get_header`` and ``as_view`` exist in *both* ancestor classes! So
which one will be used in each case? Actually, there's a (rather complex) rule for that called
MRO (Method Resolution Order). The MRO is also what can used to know which ``get_header``
and ``as_view`` will be used in each case in the previous example.


Interlude: An MRO primer
------------------------

What is MRO? For every class that Python sees, it tries to create a *list* (MRO list) of ancestor classes containing that class as
the first element and its ancestors in a specific order I'll discuss in the next paragraph. When a method
of an object of that specific class needs to be
called, then the method will be searched in the MRO list (from the first element of the MRO list i.e. starting with the class it self) - when a class is found
in the list that defines the method then that method instance (i.e. the method defined in this class) will be called and the search will stop (careful readers: I haven't
yet talked about *super* so please be patient).

Now, how is the MRO list created? As I explained, the first element
is the class itself. The second element is the MRO of the *leftmost* ancestor of that object (so MRO will
run recursively on each ancestor), the third element will be the MRO of the ancestor right next to the leftmost
ancestor etc. There is one extra and important rule: When a class is found multiple times in the MRO list (for example
if some elements have a common ancestor) then *only the last occurrence in the list will be kept* - so each class
will exist only once in the MRO list. The above rule implies that the
rightmost element in every MRO list will always be object - please make sure you
understand why before continuing.

Thus, the MRO list for ``DefaultHeaderJsonCustomClassView`` defined in the previous section
is (remember, start
with the class to the left and add the MRO of each of its ancestors starting
from the leftmost one):
``[DefaultHeaderJsonCustomClassView, DefaultHeaderBetterCustomClassView, BetterCustomClassView, CustomClassView, JsonCustomClassView, object]``, while
for ``JsonDefaultHeaderCustomClassView`` is
``[JsonDefaultHeaderCustomClassView, JsonCustomClassView, DefaultHeaderBetterCustomClassView, BetterCustomClassView, CustomClassView, object]``. What this
means is that for ``DefaultHeaderJsonCustomClassView`` the ``CustomClassView.as_view()`` and ``DefaultHeaderBetterCustomClassView.get_header()``  (thus
we will not get the JSON output) and for ``JsonDefaultHeaderCustomClassView`` the ``JsonCustomClassView.as_view()`` and ``JsonCustomClassView.get_header()``
will be used (so we won't get the default header functionality) - i.e none of those two options will result to the desired behaviour.

Let's try an example that has the same base class twice in the hierarchy (actually the previous examples also had a class twice in
the hierarchy - ``object`` but let's be more explicit). For this, we'll create a
``DefaultContextBetterCustomClassView`` that returns a default context if the context is empty
(similar to the default header functionality).

.. code-block:: python

    class DefaultContextBetterCustomClassView(BetterCustomClassView, ):
        def get_context(self, ):
            return self.context if self.context else ["DEFAULT CONTEXT"]

Now we'll create a class that inherits from both ``DefaultHeaderBetterCustomClassView`` and ``DefaultContextBetterCustomClassView``:

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
(on place 3,4,5 and 7,8,9) thus *only* their last (rightmost) occurrences will be kept in the list. So the
resulting MRO is the following (3,4,5 are removed):

``[DefaultHeaderContextCustomClassView, DefaultHeaderBetterCustomClassView, DefaultContextBetterCustomClassView, BetterCustomClassView, CustomClassView, object]``

One funny thing here is that the ``DefaultHeaderContextCustomClassView`` *will actually work* properly because the
``get_header`` will be found in ``DefaultHeaderBetterCustomClassView`` and the
``get_context`` will be found in ``DefaultContextBetterCustomClassView`` so this
result to the correct functionality.

Yes it does work but at what cost? Do you really want to do the mental exercise
of finding out the MRO for each class you define to see which method will be actually used? Also, what would happen if the
``DefaultHeaderContextCustomClassView`` class also had a ``get_context`` method defined
(hint: that ``get_context`` would be used and the ``get_context`` of ``DefaultContextBetterCustomClassView``
would be ignored).

Before finising this interlude, I'd like to make a confession: The Python MRO is *a little more* complex
than the procedure I described. It uses an algorithm called ``C3 linearization`_ which seems way too complex
to start explaining or understanding if you not a CS student. What you'll need to remember is that the
procedure I described works fine in normal cases when you don't try to do something stupid. Here's a
`post that explains the theory more`_. However if you  follow along my recommendations below you won't
have any problems with MRO, actually you won't really need to use the MRO that much to understand
the method calling hierarchy.


Using mixins for code-reuse
---------------------------

The above explanation of MRO should convince you that you should avoid
mixing hierarchies of classes - if you are not convinced then wait until I introduce ``super()``
in the next section and I guarantee that you'll be!

So, that's why I
propose implementing common functionality that needs to be re-used between
classes only with mixins (hint: that's also what Django does). Each re-usable functionality
will be implemented in its own mixin;  class views that need to implement that
functionality will just inherit from the mixin along with the base class view. Each
one of the view classes you define should inherit from *one and only one* other class
view and any number of mixins you want. Make sure that the view class is rightmost in
the ancestors list and the mixins are to the left of it (so that they will properly override
its behaviour; remember that the methods of the ancestors to the left are searched first
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
the method is not found there continue from left to right to the ancestor list; since the mixins
do only one thing and do it well you'll know what each class does simply by looking at its definition.

The super situation
-------------------

The final (and most complex) thing and extension I'd like to discuss for our custom class based views is the case
where you want to use the functionality of more than one mixins for the *same thing*. For example, let's suppose
that we had a mixin that added some data to the context and a different mixing that added
some different data to the context. Both would use the ``get_context`` method
and you'd like to have the context data of both of them to your context. But
this is not possible using the implementations above because when a
``get_context`` is found in the MRO list it will be called and the MRO search
will finish there!

So how could we add the functionality of both these mixins to a class based view? This is the same problem as
if we wanted to inherit from a mixin (or a class view) and override one of its methods
but *also* call its parent (overridden) method for example to get its output and use it as the base
of the output for the overridden method. Both these situations (re-use
functionality of two mixins with the same method or re-use functionality
from a parent method you override) are the same because what stays in the end is
the MRO list. For example say we we had the following base class

.. code::

    class V:pass

and we wanted to override it either using mixins or by using normal inheritance.

When using mixins for example like this:

.. code::

    class M1:pass
    class M2:pass
    class MIXIN(M2, M1, V):pass

we'll have the following MRO:

.. code::

    # MIXIN.mro()
    # [MIXIN, M2, M1, V, object, ]

while when using inheritance like this:

.. code::

    class M1V(V):pass
    class M2M1V(M1V):pass
    class INHERITANCE(M2M1V):pass

we'll have the following MRO:

    # INHERITANCE.mro()
    # [INHERITANCE, M2M1V, M1V, V, object ]

As we can see in both cases the base class V is the last one (just next to object)
and between this class and the one that needs the functionality (``MIXIN`` in the first
case and ``INHERITANCE`` in the second case) there are
the classes that will define the extra functionality that needs to be re-used: ``M2`` and ``M1`` (start from
left to right) in the first case and ``M2M1V`` and ``M1V`` (follow the inheritance hierarchy)
in the second case. So in both cases when calling a method they will be searched the same way using
the MRO list and when the method is found it will be executed and the search will stop.

But what if we needed to re-use some method from ``V`` (or from some other ancestor) and
a class on the left of the MRO list has the same method?
The answer, as you should have guessed by now if you have some Python knowledge is ``super()``.

The ``super`` method can be used by a class method to call a method of *its ancestors* respecting
the MRO. Thus, running ``super().x()`` from a method instance will try to find method ``x()``
on the MRO ancestors of this instance *even if the instance defines the ``x()`` method* i.e it will
not search the first element of the MRO list. Notice
that if the ``x()`` method does not exist in the headless-MRO chain you'll get an attribute error.
So, usually, you'll can ``super().x()`` from *inside* the ``x()`` method to call your parent's (as
specified by the MRO list) same-named method and retrieve its output.

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
from the base class and then from the following classes in the hierarchy (as per the MRO)
ending with the class of the instance (either ``MIXIN`` or ``INHERITANCE``). Also the
print order is the same in both cases as we've already explained. Please make
sure you understand why the output is like this before continuing.

Using super in our hierarchy
----------------------------

Using super and mixins it is easy to mix and match functionality to create new
classes. Of course, super can be used without mixins when overriding a method from
a class you inherit from and want to also call your ancestor's method.

Here's how we could add a prefix to the header:

.. code-block:: python

    class HeaderPrefixMixin:
        def get_header(self, ):
            return "PREFIX: " + super().get_header()

and here's how it could be used:

.. code-block:: python

    class HeaderPrefixBetterCustomClassView(mixins.HeaderPrefixMixin, BetterCustomClassView):
        header='Hello!'

This will retrieve the header from the ancestor and properly print the header displaying both PREFIX and Hello.
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

One thing to keep in mind is that most probably you'll need to call ``super()`` and return its output when you override a method.
Even if you think that you don't need to call it for this view or mixin, you may need it later from some other view or mixin that
inherits from this view. Also notice that ``super()`` may not return anything but may have some
side-effects in your class (for example set a ``self`` attribute) which you won't get if you don't call it!

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

This will have the desired behaviour of adding a prefix to the header, having a default header if not one was defined
and adding the extra context from both mixins!

Testing all this
----------------

In the accompanying project at https://github.com/spapas/cbv-tutorial you can take a look at how this
custom CBV hierarchy works by running it and taking a look at the ``core`` project (visit http://127.0.0.1:8001/non-django-cbv/).
There you can take a look at the views.py and mixins.py to see all the views and mixins we've discussed in this chapter.

A high level overview of CBVs
=============================

After the previous rather long (but I hope gentle enough) introduction to implementing
our own class based view hierarchy using inheritance, mixins, MRO, method overriding
and ``super`` we can now start talking about the Django Class Based Views (CBVs). Our
guide will be the `CBV inspector`_ application which displays all classes and mixins
that Django CBVs are using along with their methods and attributes. Using this application
and after reading this article you should be able to quickly and definitely know
which method or attribute you need to define to each one of your mixins or views.

To use CBV inspector, just click on a class name (for example ``CreateView``); you will
immediately see its MRO ancestors, its list of attributes (and the ancestor class that defines
each one) and finally a list of methods that this class and all its ancestors define.
Of course when a method is defined by multiple classes the MRO ordering will be used -
super is used when the functionality of the ancestor classes is also used. The CBV
inspector (and our project) has Python 3 syntax. If you want to follow along with
Python 2 (I don't recommend it though since Django 2.0 only supports Python 3.x) use the following
syntax to call super for method ``x()``:

.. code-block:: python

    super(ClassName, self).x()

this is the same as calling

.. code-block:: python

    super().x()

in Python 3.x.

Taking a look at the View
-------------------------

In any case, our travel starts from the central CBV class which is (intuitively) called ... View_!

This class is used as the base in Django's CBV hierarchy (similar to how  ``CustomClassView``
was used in our own hierarchy). It has only one attribute
(``http_method_names``) and a very small number of methods. The most important method is the
``as_view`` class method (which is similar to the one we defined in the previous section).
The ``as_view`` will instantiate an instance object of the ``View`` class
(actually the class that inherits from ``View``) and use this object to properly generate a functional view.

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
guaranteed to run every time the class based view will run, you will frequently
need to override it especially to control access control.

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
hierarchy and can be overridden as we'd like.

RedirectView and TemplateView
-----------------------------

Continuing our tour of Django CBVs I'd like to talk a little about the classes
that the CBV Inspector puts in the same level as ``View`` (GENERIC BASE):
RedirectView_ and TemplateView_. Both inherit directly from ``View`` and, the
first one defines a ``get`` method that returns a redirect to another page
while the latter one renders and returns a Django template in the ``get``
method.

The ``RedirectView`` inherits directly from view and has attributes like ``url``
(to use a static url)
or ``pattern_name`` (to use one of the patterns define in your urls.py)
to define where it should redirect. These attributes are
used by the ``get_redirect_url`` which will generate the actual url to redirect
to and can be overriden for example to redirect to a different location depending
on the current user.

The ``TemplateView`` on the other hand inherits from ``View`` and two more classes (actually
these are mixins) beyond ``View``: ``TemplateResponseMixin`` and
``ContextMixin``. If you take a look at them you'll see that the
``TemplateResponseMixin`` defines some template-related attributes (most important being
the ``template_name``) and two
methods: One that retrieves the template that will be used to render this View
(``get_template_names``)
and one that actually renders the template (``render_to_response``) using a
TemplateResponse_ instance. The
``ContextMixin`` provides the ``get_context_data`` that is
passed to the template to be rendered and should be overridden if you want to
pass more context variables.

We can already see many opportunities of reusing and overriding
functionality and improving our DRY score, for example: Create a catch all RedirectView
that depending on the remainder of the url it will redirect to a different page,
create a mixin that appends some things to the context of all CBVs using it, use dynamic templates
based on some other condition (that's actually what Detail/List/UpdateView
are doing), render a template to a different output than Html (for example a
text file) etc. I'll try to present examples for these in the next section.

The FormView
------------

The next view we're going to talk about is FormView_. This is a view that can be
used whenever we want to display a form (*not* a form related to a Model i.e for
Create/Update/Delete, for these cases there are specific CBVs we'll see later).
It is interesting to take a look at the list of its
ancestors: ``TemplateResponseMixin``, ``BaseFormView``, ``FormMixin``, ``ContextMixin``, ``ProcessFormView`` and ``View``.
We are familiar with ``TemplateResponseMixin``, ``ContextMixin`` and ``View`` but not with
the others. Before discussing these classes let's take a look at the FormView
hierarchy, courtesy of http://ccbv.cco.uk and http://yuml.me:

.. raw:: html

      <img src="https://yuml.me/diagram/plain;/class/[TemplateResponseMixin%7Bbg:white%7D]%5E-[FormView%7Bbg:green%7D],%20[BaseFormView%7Bbg:white%7D]%5E-[FormView%7Bbg:green%7D],%20[FormMixin%7Bbg:white%7D]%5E-[BaseFormView%7Bbg:white%7D],%20[ContextMixin%7Bbg:white%7D]%5E-[FormMixin%7Bbg:white%7D],%20[ProcessFormView%7Bbg:white%7D]%5E-[BaseFormView%7Bbg:white%7D],%20[View%7Bbg:lightblue%7D]%5E-[ProcessFormView%7Bbg:white%7D].svg" alt="FormView">

The above diagram should make everything easier: The ``FormMixin`` inherits
from ``ContextMixin`` and overrides its ``get_context_data`` method to add the
form to the view. Beyond this, it adds some attributes and methods for proper form handling, for
example the ``form_class`` (attribute when the form class will be the same always) and
``get_form_class()`` (method when the form class will be dynamic for example
depending on the logged in user), ``initial`` and ``get_initial()`` (same logic as before for
the form's initial values), ``form_valid()`` and ``form_invalid()`` to define
what should happen when the form is valid or invalid, ``get_form_kwargs`` to pass
some keyword arguments to the form's constructor etc. Notice that FormMixin
does not define any form handling logic (i.e check if the form is valid and call
its ``form_valid()`` method) -- this logic is defined in the ``ProcessFormView``
which inherits from ``View`` and defines proper ``get()`` (just render the form)
and ``post()`` (check if the form is valid and call ``form_valid`` else call ``form_invalid``) methods.

One interesting here is to notice here is that Django defines both the ``FormMixin`` and ``ProcessFormView``.
The ``FormMixin`` offers the basic Form elements (the form class, initial data
etc) and could be re-used in a different flow beyond the one offered by
``ProcessFormView`` (for example display the form as a JSON object instead of a
Django template). On the other hand, ``ProcessFormView`` is required in order to
define the ``get`` and ``post`` methods that are needed from the ``View``. These
methods can't be overridden in the FormMixin since that would mean that the mixin
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
(``queryset`` will be checked first so it has priority if both are defined) and
returns a queryset result (taking into account the ordering). This queryset
result will be used by the ``get_context_data()`` method of this mixin to
actually put it to the context by saving to a context variable named ``object_list``.
Notice that you can set the ``context_object_name`` attribute to add and extra
another variable to the context with the queryset beyond ``object_list`` (for
example if you have an ``ArticleLsitView`` you can set ``context_object_name = articles`` to
be able to do ``{% for article in articles %}`` in your context instead of
``{% for article in object_list %}``).

The ``MultipleObjectMixin`` can be used and
overridden when we need to put multiple objects in a View. This mixin is
inherited (along with ``View``) from ``BaseListView`` that adds a proper ``get``
method to call ``get_context_data`` and pass the result to the template.

As we can also see, Django uses the ``MultipleObjectTemplateResponseMixin`` that
inherits from ``TemplateResponseMixin`` to render the template. This mixin does
some magic with the queryset or model to define a
template name (so you won't need to define it yourself) - that's from where the
``app_label/app_model_list.html`` default template name is created.

Similar to the ``ListView`` is the DetailView_ which has the same class hierarchy as the ``ListView`` with two differences:
It uses ``SingleObjectMixin`` instead of ``MultipleOjbectMixin``,
``SingleObjectTemplateResponseMixin`` instead of ``MultipleObjectTemplateResponseMixin``
and ``BaseDetailView`` instead of ``BaseListView``. The
``SingleObjectMixin`` will use the ``get_queryset()`` (in a similar manner to the ``get_queryset()`` of
``MultipleObjectMixin``) method to return a single object (so all attributes and methods
concerning ordering or pagination are missing) but instead has the ``get_object()`` method which
will pick and return a single object from that queryset (using a ``pk`` or ``slug`` parameter). This object
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
``SingleObjectTemplateResponseMixin`` is mainly used to define the template names that will be searched for
(i.e ``app_label/app_model_form.html``), while the ``BaseCreateView``
is used to combine the functionality of ``ProcessFormView`` (that handles the basic form workflow as we have
already discussed) and ``ModelFormMixin``. The ``ModelFormMixin`` is a rather complex mixin that inherits from
both ``SingleObjectMixin`` and ``FormMixin``. The ``SingleObjectMixin`` functionality is not really used by ``CreateView``
(since no object will need to be retrieved for the ``CreateView``) however the ``ModelFormMixin`` is also used
by ``UpdateView`` that's why ``ModelFormMixin`` also inherits from it (to retrieve the object that will be updated).

``ModelFormMixin`` mixin adds functionality
for handling forms related to models and object instances. More specifically it adds functionality for:
* creating a form class (if one is not provided) by the configured model / queryset. If you don't provide the form class (by using the ``form_class`` attribute) then you need to configure the fields that the generated form will display by passing an array of field names through the ``fields`` attribute
* overrides the ``form_valid`` in order to save the object instance of the form
* fixes ``get_success_url`` to redirect to the saved object's absolute_url when the object is saved
* pass the current object to be updated (that was retrieving through the ``SingleObjectMixin``) -if there is a current object- to the form as the ``instance`` attribute

The UpdateView and DeleteView
-----------------------------

The UpdateView_ class is almost identical to the ``CreateView`` - the only difference is that
``UpdateView`` inherits from ``BaseUpdateView`` (and ``SingleObjectTemplateResponseMixin``) instead
of ``BaseCreateView``.  The ``BaseUpdateView`` overrides the ``get`` and ``post`` methods of
``ProcessFormView`` to retrieve the object (using ``SingleObjectMixin``'s ``get_object()``)
and assign it to an instance variable - this will then be picked up by the ``ModelFormMixin`` and used
properly in the form as explained before. One thing I notice here is that it seems that the hierarchy would
be better if the ``ModelFormMixin`` inherited *only* from ``FormMixin`` (instead of both from
``FormMixin`` and ``SingleObjectMixin``) and ``BaseUpdateView`` inheriting from ``ProcessFormView``,
``ModelForMixin`` *and* ``SingleObjectMixin``. This way the ``BaseCreateView`` wouldn't get the
non-needed ``SingleObjectMixin`` functionality. I am not sure why Django is implemented this way
(i.e the ``ModelFormMixin`` also inheriting from ``SingleObjectMixin`` thus passing this non-needed
functionality to ``BaseCreateView``) -- if a reader has a clue I'd like to know it.

In any way, I'd like to also present the DeleteView_ which is more or less the same as the DetailView_
with the addition of the ``DeleteMixin`` in the mix. The ``DeleteMixin`` adds a ``post()`` method
that will delete the object when called and makes ``success_url`` required (since there would be no
object to redirect to after this view is posted).

Access control mixins
---------------------

Another small hierarchy of class based views (actually these are all mixins) are the authentication ones which
can be used to control access to a view.
These are ``AcessMixin``, ``LoginRequiredMixin``, ``PermissionRequiredMixin`` and ``UserPassesTestMixin``.
The ``AccessMixin`` provides some basic functionality (i.e what to do when the user does not have access
to the view, find out the login url to redirect him etc) and is used as a base for the other three. These
three override the ``dispatch()`` method of ``View`` to check if the user has the specific rights (i.e
if he has logged in for ``LoginRequiredMixin``, if he has the defined permissions for ``PermissionRequiredMixin``
or if he passes the provided test in ``UserPassesTextMixin``). If the user has the rights the view will proceed
as normally (call super's dispatch) else the access denied functionality from ``AccessMixin`` will be implemented.

Some other CBVs
---------------

Beyond the class based views I discussed in this section, Django also has a bunch of CBVs related
to account views (``LoginView``, ``LogoutView``, ``PasswordChangeView`` etc) and Dates (``DateDetailView``, ``YearArchiveView`` etc).
I won't go into detail about these since they follow the same concepts and use most of the mixins
we've discussed before. Using the CBV Inspector you should be able to follow along and decide the methods you need
to override for your needs.

Also, most well written Django packages will define their own CBVs that inherit
from the Django CBVs - with the knowledge you acquired here you will be able to follow along on their source code to understand how everything works.


Real world use cases
====================

In this section I am going to present a number of use cases demonstrating the usefulness of Django CBVs. In most of
these examples I am going to override one of the methods of the mixins I discussed in the previous section. There
are *two* methods you can use for integrating the following use cases to your application.

Create your own class inheriting from one of the Django CBVs and add to it directly the method to override. For example,
if you wanted to override the ``get_queryset()`` method a ``ListView`` you would do a:

.. code-block:: python

    class GetQuerysetOverrideListView(ListView):
        def get_queryset(self):
            qs = super().get_queryset()
            return qs.filter(status='PUBLISHED')

This is useful if you know that you aren't going to need the overriden ``get_queryset`` functionality to a different
method and following the YAGNI principle (or if you know that even if you need it you could inherit from ``GetQuerysetOverrideListView``
i.e in another ListView).
However, if you know that there may be more CBVs that would need their
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
``UpdateView`` and ``DeleteView``). Because of how MRO works, I won't need to inherit ``GetQuerysetOverrideMixin`` from
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

        def __str__(self):
            return self.name

        class Meta:
            permissions = (
                ("publisher_access", "Publisher Access"),
                ("admin_access", "Admin Access"),
            )


    class AbstractGeneralInfo(models.Model):
        status = models.CharField(max_length=16, choices=STATUS_CHOICES, )
        category = models.ForeignKey('category', on_delete=models.PROTECT, )
        created_on = models.DateTimeField(auto_now_add=True, )
        created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_created_by', )
        modified_on = models.DateTimeField(auto_now=True, )
        modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_modified_by', )

        owned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_owned_by', )
        published_on = models.DateTimeField(blank=True, null=True)

        class Meta:
            abstract = True


    class Article(AbstractGeneralInfo):
        title = models.CharField(max_length=128, )
        content = models.TextField()


    class Document(AbstractGeneralInfo):
        description = models.CharField(max_length=128, )
        file = models.FileField()

All this can be found on the accompanying project https://github.com/spapas/cbv-tutorial on the djangocbv app (visit http://127.0.0.1:8001/djangocbv/).



Do something when a valid form is submitted
-------------------------------------------

When a form is submitted and the form is valid
the ``form_valid`` method of ``ModelForMixin`` (and ``FormMixin``) will be called. This method
can be overridden to do various things before (or after) the form is saved. For example,
you may want have a field whose value is calculated from other fields in the form or you want to
create an extra object. Let's see a generic example of overriding a ``CreateView`` or ``UpdateView`` with comments:

    def form_valid(self, form, ):
        # let's calculate a field value
        form.instance.calculated_field = form.cleaned_data['data1'] + form.cleaned_data['data2']

        # save the form by calling super().form_valid(); keep the return value - it is the value of get_success_url
        redirect_to = super().form_valid(form)

        # For Create or UpdateView, the just-saved object will be assigned to self.object
        logger.log("Created an object with id {0}".format(self.object.id)

        # return the redirect
        return redirect_to

This is rather complex so I'll also explain it: The form_valid gets the actual form which, since is validated
has a ``cleaned_data`` dictionary of values. This form also has an ``instance`` attribute which is the object
that this form is bound to - notice that a normal ``Form`` won't have an instance only a ``ModelForm``.
This can be used to modify the instance of this form as needed - before saving it. When you want to actually save
the instance you call ``super().form_valid()`` passing it the modified form (and instance). This method does
three things

* It saves the instance to the database
* It assigns the saved object to the ``object`` instance attribute (so you can refer to it by ``self.instance``)
* It uses ``get_redirect_url`` to retrieve the location where you should redirect after the form is submitted

Thus in this example we save ``redirect_to`` to return it also from our method also and then can use ``self.object.id``
to log the id of the current object.

On a more specific example, notice the ``Article`` and ``Document`` models which both inherit (abstract)
from ``AbstractGeneralInfo`` have a ``created_by`` and
a ``modified_by`` field. These fields have to be filled automatically from the current logged in user. Now, there are various
options to do that but what I vote for is using an ``AuditableMixin`` as I have already described in `my Django model auditing article`_.

To replicate the functionality we'll create an ``AuditableMixin`` like this:

.. code-block:: python

    class AuditableMixin(object,):
        def form_valid(self, form, ):
            if not form.instance.created_by:
                form.instance.created_by = self.request.user
            form.instance.modified_by = self.request.user
            return super().form_valid(form)

This mixin can be used by both the create and update view of both ``Article`` and ``Document``. So all four of these
classes will share the same functionality. Notice that the ``form_valid`` method is overridden - the ``created_by``
of the form's instance (which is the object that was edited, remember how ``ModelFormMixin`` works) will by set
to the current user if it is null (so it will be only set once) while the ``modified_by`` will be set always to the
current user. Finally we call ``super().form_valid`` and return its response so
that the form will be actually saved and the redirect will go to the proper success url. To use it for example for the
``Article``, ``CreateView`` should be defined like this:

.. code-block:: python

    class ArticleCreateView(AuditableMixin, CreateView):
        class Meta:
            model = Article


Change the queryset of the CBV
-------------------------------

All CBVs that inherit from ``SingleObjectMixin`` or ``MultipleObjectMixin`` (``ListView``, ``DetailView``, ``UpdateView`` and ``DeleteView``)
have a ``model`` and a ``queryset`` property that can be used (either one or the other) to define the queryset that will be used for
querying the database for that CBVs results. This queryset can be further dynamically refined by overriding the ``get_queryset()`` method.
What I usually do is that I define the ``model`` attribute and then override ``get_querset`` in order to dynamically modify the queryset.

For example, let's say that I wanted to add a count of articles and documents per each category. Here's how the ``CategoryListView`` could be done:

.. code-block:: python

    class CategoryListView(ExportCsvMixin, AdminOrPublisherPermissionRequiredMixin, ListView):
        model = Category
        context_object_name = 'categories'

        def get_queryset(self):
            qs = super().get_queryset()
            return qs.annotate(article_cnt=Count('article'), document_cnt=Count('document'))

Notice that I also use some more mixins for this ``ListView`` (they'll be explained later). The ``get_queryset`` adds
the annotation to the ``super()`` queryset (which will be ``Category.objects.all()``). One final comment is that instead
of this, I could have more or less the same functionality by implementing ``CategoryListView``:

.. code-block:: python

    class CategoryListView(ExportCsvMixin, AdminOrPublisherPermissionRequiredMixin, ListView):
        context_object_name = 'categories'
        query = Category.objects.all().annotate(article_cnt=Count('article'), document_cnt=Count('document'))

This has the same functionality (return all categories with the number of articles and documents for each one) and
saves some typing from overriding the ``get_queryset``  method. However as I said most of the time I use the model
attribute and override the ``get_queryset`` method because it seems more explicit and descriptive to me and most of
the time I'll need to add some more filtering (based on the current user, based on some query parameter etc) that
can only be implemented on the ``get_queryset``.


Allow each user to list/view/edit/delete only his own items
-----------------------------------------------------------
Continuing from the previous example of modifying the queryset, let's suppose that we want to allow each
user to be able to list the items (articles and
documents) he has created and view/edit/delete them. We also want to allow admins and publishers to view/edit everything.

Since the ``Article`` and ``Document`` models both have an ``owned_by`` element we can use use this to filter
the results returned by ``get_queryset()``. For example, here's a mixin that checks if the current user is
admin or publisher. If he is a publisher then he will just return the ``super()`` queryset. If however he is a simple
user it will return only the results that are owned by him with ``qs.filter(owned_by=self.request.user)``.


.. code-block:: python

    class LimitAccessMixin:
        def get_queryset(self):
            qs = super().get_queryset()
            if self.request.user.has_perm('djangocbv.admin_access') or self.request.user.has_perm('djangocbv.publisher_access') :
                return qs
            return qs.filter(owned_by=self.request.user)
            
Another similar mixin that is used is the ``HideRemovedMixin`` that, for simple users, excludes from the queryset the objects that
are removed:

.. code-block:: python

    class HideRemovedMixin:
        def get_queryset(self):
            qs = super().get_queryset()
            if self.request.user.has_perm('djangocbv.admin_access') or self.request.user.has_perm('djangocbv.publisher_access'):
                return qs
            return qs.exclude(status='REMOVED')
            
One thing that needs a little discussion is that for both of these mixins I am using ``get_queryset`` to implement access control to
allow using the same mixin for views that inherit from both ``SingleObjectMixin`` and ``MultipleObjectMixin`` (since the ``get_queryset`` is
used in both of them). This
means that when a user tries to access an object that has not access to he'll get a nice 404 error. 

Beyond this, instead of filtering the queryset,
for views inheriting from ``SingleObjectMixin`` (i.e ``DetailView``, ``UpdateView`` and ``DeleteView``)
we could have overridden the ``get_object`` method to raise an access denied exception. Here's how ``get_object`` could be
overridden to raise a 403 Forbidden status when a user tries to access an object that does not belong to him:

.. code-block:: python

    from django.core.exceptions import PermissionDenied

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.owned_by=self.request.user:
            raise PermissionDenied
        return obj


Configure the form's initial values from GET parameters
-------------------------------------------------------

Sometimes we want to have a ``CreateView`` with some fields already filled. I usually
implement this by passing the proper parameters to the URL (i.e by calling it as /create_view?category_id=2)
and then using the following mixin to override the ``FormMixin`` ``get_initial`` method in order to
return the form's initial data from it:

.. code-block:: python

    class SetInitialMixin(object,):
        def get_initial(self):
            initial = super(SetInitialMixin, self).get_initial()
            initial.update(self.request.GET.dict())
            return initial

So if the /article_create url can be used to initialte the ``CreateView`` for the article,
using ``/article_create?category_id=3`` will show the CreateView with the Category with id=3
pre-selected in the category field!

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

One final comment is that overriding the ``get_context_data`` method will probably be the most
common thing you're going to do when using CBVs (you'll definitely need to add things to the context)
so try to remember the following 3 needed lines:

.. code-block:: python

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            # ... here we add stuff to the ctx
            return ctx


Add a simple filter to a ListView
---------------------------------

For filtering I recommend using the excellent `django-filter`_ package as I've already
presented in `my essential Django package list`_. Here's how a mixin can be created that
adds a filter to the context:

.. code-block:: python

    class AddFilterMixin:
        filter_class = None

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            if not self.filter_class:
                raise NotImplementedError("Please define filter_class when using AddFilterMixin")
            filter = self.filter_class(self.request.GET, queryset=self.get_queryset())
            ctx['filter'] = filter
            if self.context_object_name:
                ctx[self.context_object_name] = filter.qs
            return ctx

Notice that the ``get_context_data`` checks to see if the ``filter_class`` attribute has been
defined (if not it will raise a useful explanation). It will then instantiate the filter class
passing it the ``self.request.GET`` and the current queryset (``self.get_queryset()``) - so for
example any extra filtering you are doing to the queryset (for example only show content owned by the
current user) will be also used. Finally, pass the filter to the context and assign the
contect_object_name to the filtered queryset.

Here's for example how this mixin is used for ``ArticleListView``:

.. code-block:: python

    class ArticleListView(AddFilterMixin, ListView):
        model = Article
        context_object_name = 'articles'
        filter_class = ArticleFilter

And then just add the following to the ``article_list.html`` template:

.. code-block:: python

    <form method='GET'>
        {{ filter.form }}
        <input type='submit' value='Filter' />
    </form>
    {% for article in articles %}
        Display article info - only filtered articles will be here
    {% endfor %}


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

Implement a quick moderation
----------------------------

It is easy to implement some moderation to our model publishing. For example, let's suppose that we only
allow publishers to publish a model. Here's how it can be done:

.. code-block:: python
           
    def form_valid(self, form):
        if form.instance.status != 'REMOVED':
            if self.request.user.has_perm('djangocbv.publisher_access'):
                form.instance.status = 'PUBLISHED'
            else:
                form.instance.status = 'DRAFT'
        
        return super().form_valid(form)

So, first of all we make sure that the object is not ``REMOVED`` (if it is
remove it we don't do anything else). Next we check if the current user has
``publisher_access`` if yes we change the object's status to ``PUBLISHED`` - on any
other case we change its status to ``DRAFT``. Notice that this means that whenever a
publisher saves the object it will be published and whenever a non-publisher saves it
it will be made a draft. We then call our ancestor's ``form_valid`` to save the object
and return to success url.

I'd like to repeat here that this mixin, since it calls super, can work concurrently
with any other mixins that override ``form_valid`` (and also call their super method
of course), for example it can be used together with the audit (auto-fill created_by
and moderated_by) and the success mixin we defined previously!


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

Output non-html views
---------------------

I've written a whole article about this, please take a look at my `Django non-HTML responses`_ article.

Also, notice that is very easy to create a mixin that will output a view to PDF - I have already written
an `essential guide for outputting PDFs in Django`_ so I am just going to refer you to this article for
(much more) information!

Finally, let's take a look at a generic Mixin that you can use to add CSV exporting capabilities to a
``ListView``:

.. code-block:: python


    class ExportCsvMixin:
        def render_to_response(self, context, **response_kwargs):
            if self.request.GET.get('csv'):
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="export.csv"'

                writer = csv.writer(response)
                for idx, o in enumerate(context['object_list']):
                    if idx == 0: # Write headers
                        writer.writerow(k for (k,v) in o.__dict__.items() if not k.startswith('_'))
                    writer.writerow(v for (k,v) in o.__dict__.items() if not k.startswith('_'))

                return response
            return super().render_to_response(context, **response_kwargs)

As you can see this mixin overrides the ``render_to_response`` method. It will check if there's a
``csv`` key to the ``GET`` queryset dictionary, thus the url must be called with ``?csv=true`` or something similar. You
can just add this link to your template:

.. code-block:: html

    <a class='button' href='?csv=true'>Export csv</a>

So if the view needs to be exported to CSV, it will create a new ``HttpResponse`` object with the correct content type.
The next line will add a header that (``Content-Disposition``) will mark the response as an attachment and give it a default filename.
We then crate a new ``csv.writer`` passing the just-created response as the place to write the csv. The ``for`` loop that follows
enumerates the ``object_list`` value of the context (remember that this is added by the ``MultipleObjectMixin`` and contains the
result of the ``ListView``). It will then use the object's ``__dict__`` attribute to write the headers (for the first time) and then
write the values of all objects.

As another simple example, let's create a quick JSON output mixin for our DetailViews:

    class JsonDetailMixin:
        def render_to_response(self, context, **response_kwargs):
            if self.request.GET.get('json'):
                response = HttpResponse(content_type='application/json')
                response.write(json.dumps(dict( (k,str(v)) for k,v in self.object.__dict__.items() )))
                return response
            return super().render_to_response(context, **response_kwargs)
            
If you add this to a view inheriting from ``DetailView`` and pass it the ``?json=true`` queryparameter
you'll get a JSON response!


Use one TemplateView for multiple html templates
------------------------------------------------

Using a ``TemplateView`` you could display an html template without much problem just by
settings the ``template`` attribute of your class. What if you wanted to have a single
``TemplateView`` that would display many templates based on the query path? Simple, just
override ``get_template_names`` to return a different template based on the path. For example,
using this view:

.. code-block:: html

    class DynamicTemplateView(TemplateView):
        def get_template_names(self):
            what = self.kwargs['what']
            return '{0}.html'.format(what)

You can render any template you have depending on the value of the ``what`` kwarg. To allow
only specific template names you can either add a check to the above implementation (i.e that
what is ``help`` or ``about``) or you may do it to the urls.py if you use a regular expression. Thus,
to only allow ``help.html`` and ``about.html`` to be rendered with this method add it to your urls like this:

.. code-block:: html

    re_path(r'^show/(?P<what>help|about)/', views.DynamicTemplateView.as_view(), name='template-show'),

Finally, to use it to render the ``help.html`` you'll just call it like <a href='{% url "template-show" "help" %}'>Help</a>

Notice that of course instead of creating the ``DynamicTemplateView`` you could just dump these html files in your
static folder and return them using the static files functionality. However the extra thing that the ``DynamicTemplateView``
brings to you is that this is a full Django template thus you can use template tags, filters, your context variables, inherit
from your site-base and even override ``get_context_data`` to add extra info to the template! All this is not possible with
static files!

Implement a partial Ajax view
-----------------------------

Overriding ``get_template_names`` can also be used to create a DRY Ajax view
of your data! For example, let's say that you have a ``DetailView`` for one of your models that
has overriden the ``get_template_names`` like this:

.. code-block:: python

    def get_template_names(self):
        if self.request.is_ajax() or self.request.GET.get('ajax_partial'):
            return 'core/partial/data_ajax.html'
        return super().get_template_names()

and you have also defined a normal template for classic request response viewing and an ajax template
that contains only the specific data for this instances (i.e it does not containg html body, headers, footers etc,
only a <div> with the instance's data). Notice I'm using either the ``is_ajax`` method or I directly passed GET
value (``ajax_partial``) - this is needed because sometimes ``is_ajax`` is not working as expected (depending on
how you're going to do the request), also this way you can easily test the partial ajax view through your browser
by passing it ``?ajax_partia=true``.

Using this technique you can create an Ajax view of your data just by requesting the DetailView through an
Ajax call and dumping the response you get to a modal dialog (for example)  - no need for fancy REST APIs. Also as
a bonus, the classic DetailView will work normally, so you can have the Ajax view to give a summary of the instance's
data (i.e have a subset of the info on the Ajax template) and the normal view to display everything.

Add a dynamic filter and/or table to the context
------------------------------------------------

If you have a lot of similar models you can add a mixin that dynamically creates tables and a filters
for these models  - take a look at my `dynamic tables and filters for similar models`_ article!


Configure forms for your views
------------------------------

As I've already explained if you are using a ``FormView`` you'll need to set a ``form_class`` for
your view (needed by ``FormMixin``) while, for an Update or ``CreateView`` which use the ``ModelFormMixin``
you can either set the ``form-class`` or directly configure the instance's fields that will be displayed
to the form using the ``fields`` attribute.

For example, let's say that you have a rather generic ``FormView`` that will display a different form
depending on the user permissions. Here's how you could do this to return a ``SuperForm`` if the
current user is a superuser and a ``SimpleForm`` in other cases:


.. code-block:: python

    def get_form_class(self):
        if self.request.user.is_superuser:
            return SuperForm
        return SimpleForm

Display a different form for Create and Update
----------------------------------------------

There are various ways you can do this (for example you can just declare a different ``form_class`` for your
``Create`` and ``UpdateView``) but I think that the most DRY one, especially if the create and update form are
similar is to pass an ``is_create`` argument to the form which it will then be used to properly configure the form.

Thus, on your ``CreateView`` you'll add this ``get_form_kwargs``:

.. code-block:: python

    def get_form_kwargs(self):
        kwargs = super(MyCreateView, self).get_form_kwargs()
        kwargs.update({'is_create': True})
        return kwargs

while on your ``UpdateView`` you'll add this:

.. code-block:: python

    def get_form_kwargs(self):
        kwargs = super(MyUpdateView, self).get_form_kwargs()
        kwargs.update({'is_create': False})
        return kwargs

Please notice that the form has to properly handle the extra kwarg in its constructor as I've already explained previously.

Only allow specific HTTP methods for a view
-------------------------------------------

Let's say that you want to create an ``UnpublishView`` i.e a view that will change the status of your content
to ``DRAFT``. Since this view will change your model instance it must be called through ``POST``, however
you may not want to display an individual form for this view, just a button that when called will display
a client-side (Javascript) prompt and if the user clicks it it will immediately do a ``POST`` request
by submitting the form. The best way to create this is to just implement an ``UpdateView`` for your model
and change its form valid to change the status to ``DRAFT``, something like this:

.. code-block:: python

    def form_valid(self, form, ):
        form.instance.status = 'DRAFT'
        return super().form_valid(form)

Beyond this, you'll need to add a ``fields = []`` attribute to your ``UpdateView`` to denote that you won't
need to update any fields from the model (since you'll update the status directly) and finally, to only allow
this view to be called through an http ``POST`` method add the following attribute:

.. code-block:: python

        http_method_names = ['post',]


Create an umbrella View for multiple models
-------------------------------------------

Let's say that you have a couple of models (called ``Type1`` and ``Type2`` that are more or less the same and
you want to quickly create a ``ListView`` for both of them but you'd like to create just one ``ListView`` and
separate them by their url. Here's how it could be done:

.. code-block:: python


    class UmbrellaListView(ListView):
        template_name='umbrella_list.html'

        def dispatch(self, request, *args, **kwargs):
            self.kind = kwargs['kind']
            if self.kind == 'type1':
                self.queryset = models.Type1.objects.all()
            elif self.kind == 'type2':
                self.queryset = models.Type2.objects.all()
            return super(UmbrellaListView, self).dispatch(request, *args, **kwargs)

Notice that for this to work properly you must setup your urls like this:

.. code-block:: python

    ...
    url(r'^list/(?P<kind>type1|type2)/$', UmbrellaListView.as_view() ) , name='umbrella_list' ),
    ...




A heavy CBV user project
========================

In this small chapter I'd like to present a bunch of mixins and views that I've defined to the 
accompanying project (https://github.com/spapas/cbv-tutorial). 

Let's start with the mixins (I won't show the mixins I've already talked about in the previous chapter): 

.. code-block:: python

        
    class SetOwnerIfNeeded:
        def form_valid(self, form, ):
            if not form.instance.owned_by_id:
                form.instance.owned_by = self.request.user
            return super().form_valid(form)


    class ChangeStatusMixin:
        new_status = None 
        
        def form_valid(self, form, ):
            if not self.new_status:
                raise NotImplementedError("Please define new_status when using ChangeStatusMixin")
            form.instance.status = new_status
            return super().form_valid(form)

        
    class ContentCreateMixin(SuccessMessageMixin,
                            AuditableMixin,
                            SetOwnerIfNeeded,
                            RequestArgMixin,
                            SetInitialMixin,
                            ModerationMixin,
                            LoginRequiredMixin):
        success_message = 'Object successfully created!'


    class ContentUpdateMixin(SuccessMessageMixin,
                            AuditableMixin,
                            SetOwnerIfNeeded,
                            RequestArgMixin,
                            SetInitialMixin,
                            ModerationMixin,
                            LimitAccessMixin,
                            LoginRequiredMixin):
        success_message = 'Object successfully updated!'


    class ContentListMixin(ExportCsvMixin, AddFilterMixin, HideRemovedMixin, ):
        pass


    class ContentRemoveMixin(SuccessMessageMixin
                             AdminOrPublisherPermissionRequiredMixin,
                             AuditableMixin,
                             HideRemovedMixin,
                             ChangeStatusMixin,):
        http_method_names = ['post',]
        new_status = 'REMOVED'
        fields = []
        success_message = 'Object successfully removed!'


    class ContentUnpublishMixin(SuccessMessageMixin
                                AdminOrPublisherPermissionRequiredMixin,
                                AuditableMixin,
                                UnpublishSuccessMessageMixin,
                                ChangeStatusMixin,):
        http_method_names = ['post',]
        new_status = 'DRAFT'
        fields = []
        success_message = 'Object successfully unpublished!'

The ``SetOwnerIfNeeded`` and  ``ChangeStatusMixin`` are simple mixins that override ``form_valid`` to
introduce some functionality before saving the object). The other mixins are used to gather functionality of 
other mixins together. Thus, ``ContentCreateMixin`` has the mixin functionality needed to create something (i.e an
``Article`` or a ``Document``) i.e show a success message, add auditing information, set the object's owner,
pass the request to the form, set the form's initial values, do some moderation and only allow logged in users. On
a similar fashion, the ``ContentUpdateMixin`` collects the functionality needed to update something and is similar to
``ContentCreateMixin`` (with the difference that it also as the ``LimitAccessMixin`` to only allow simple users to
edit their own content). The ``ContentListMixin`` adds functionality for export to CSV, simple filter and hiding removed
things. 
 
 
The ``ContentRemoveMixin`` and ``ContentUnpublishMixin`` are used to implement Views for Removing and Unpublishing
an object. Both of them inherit from ``ChangeStatusMixin`` - one setting
the ``new_status`` to ``REMOVED`` the other to ``DRAFT``. 


Continuing in this
fashion I could remove both ``ContentRemoveMixin`` and ``ContentUnpublishMixin`` and add a ``ContentChangeStatusMixin`` like this:

    class ContentChangeStatusMixin(AdminOrPublisherPermissionRequiredMixin,
                                AuditableMixin,
                                UnpublishSuccessMessageMixin,
                                ChangeStatusMixin,):
        http_method_names = ['post',]
        fields = []

Thus the ``new_status`` attribute wouldn't be there so my ``*RemoveView`` and ``*UnpublishView`` would 
all inherit from this mixin and define the ``new_status`` field differently.
This is definitely valid (and more DRY) but less explicit than the way I've implemented this - i.e you may 
wanted to not allow publishers to remove objects, only admins (so you could implement that in the ``get_queryset``
or ``dispatch`` method of ``ContentRemoveMixin`` and ``ContentUpdateMixin``.

Now let's take a look at the views:
        

    class ArticleListView(ContentListMixin, ListView):
        model = Article
        context_object_name = 'articles'
        filter_class = ArticleFilter
        

    class ArticleCreateView(ContentCreateMixin, RedirectToArticlesMixin, CreateView):
        model = Article
        form_class = ArticleForm


    class ArticleUpdateView(ContentUpdateMixin, RedirectToArticlesMixin, UpdateView):
        model = Article
        form_class = ArticleForm

    class ArticleDetailView(HideRemovedMixin, JsonDetailMixin, DetailView):
        model = Article
        context_object_name = 'article'

        def get_template_names(self):
            if self.request.is_ajax() or self.request.GET.get('partial'):
                return 'djangocbv/_article_content_partial.html'
            return super().get_template_names()


    class ArticleRemoveView(ContentRemoveMixin, RedirectToArticlesMixin, UpdateView):
        model = Article


    class ArticleUnpublishView(ContentUnpublishMixin, RedirectToArticlesMixin, UpdateView):
        model = Article


    class CategoryListView(ExportCsvMixin, AdminOrPublisherPermissionRequiredMixin, ListView):
        model = Category
        context_object_name = 'categories'

        def get_queryset(self):
            qs = super().get_queryset()
            return qs.annotate(article_cnt=Count('article'), document_cnt=Count('document'))


    class CategoryCreateView(CreateSuccessMessageMixin, RedirectToHomeMixin, AdminOrPublisherPermissionRequiredMixin, CreateView):
        model = Category
        fields = ['name']


    class CategoryUpdateView(UpdateSuccessMessageMixin, RedirectToHomeMixin, AdminOrPublisherPermissionRequiredMixin, UpdateView):
        model = Category
        fields = ['name']
        
        
    class CategoryDetailView(CategoriesContextMixin, DetailView):
        model = Category
        context_object_name = 'category'
        
        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['article_number'] = Article.objects.filter(category=self.object).count()
            ctx['document_number'] = Document.objects.filter(category=self.object).count()
            return ctx

    class DocumentListView(ContentListMixin, ListView):
        model = Document
        context_object_name = 'documents'
        filter_class = DocumentFilter


    class DocumentCreateView(ContentCreateMixin, RedirectToDocumentsMixin, CreateView):
        model = Document
        form_class = DocumentForm


    class DocumentUpdateView(ContentUpdateMixin, RedirectToDocumentsMixin, UpdateView):
        model = Document
        form_class = DocumentForm


    class DocumentDetailView(HideRemovedMixin, JsonDetailMixin, DetailView):
        model = Document
        context_object_name = 'document'


    class DocumentRemoveView(ContentRemoveMixin, RedirectToDocumentsMixin, UpdateView):
        model = Document


    class DocumentUnpublishView(ContentUnpublishMixin, RedirectToDocumentsMixin, UpdateView):
        model = Document

        
    class DynamicTemplateView(TemplateView):
        def get_template_names(self):
            what = self.kwargs['what']
            return '{0}.html'.format(what)

Conclusion
==========

asdasd


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
.. _`dynamic tables and filters for similar models`: https://spapas.github.io/2015/10/05/django-dynamic-tables-similar-models/
.. _`Django non-HTML responses`: https://spapas.github.io/2014/09/15/django-non-html-responses/
.. _django-filter: https://github.com/carltongibson/django-filter
.. _`my essential Django package list`: https://spapas.github.io/2017/10/11/essential-django-packages/
.. _login: https://docs.djangoproject.com/en/2.0/topics/auth/default/#django.contrib.auth.views.login
.. _`C3 linearization`: https://en.wikipedia.org/wiki/C3_linearization
.. _`post that explains the theory more`: https://medium.com/technology-nineleaps/python-method-resolution-order-4fd41d2fcc