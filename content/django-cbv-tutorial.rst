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
the `request`_ object and must return a `response`_ object (notice that if the
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

To make things more clear we'll try to implement our own class based views hierarchy.



A high level overview of CBVs
=============================

Real world use cases
====================


.. code-block:: python

    >>> [ y for x in non_flat if len(x) > 2 for y in x ]
    [1, 2, 3, 4, 5, 6]

Success!

One final, more complex example: Let's say that we have a list
of lists of words and we want to get a list of all the letters of these words
along with the index of the list they belong to
but only for words with more than two characters. Using the same
for-loop syntax for the nested list comprehensions we'll get:

.. code-block:: python

    >>> strings = [ ['foo', 'bar'], ['baz', 'taz'], ['w', 'koko'] ]
    >>> [ (letter, idx) for idx, lst in enumerate(strings) for word in lst if len(word)>2 for letter in word]
    [('f', 0), ('o', 0), ('o', 0), ('b', 0), ('a', 0), ('r', 0), ('b', 1), ('a', 1), ('z', 1), ('t', 1), ('a', 1), ('z', 1), ('k', 2), ('o', 2), ('k', 2), ('o', 2)]




.. _`CBV inspector`: http://ccbv.co.uk`
.. _`request`: https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpRequest
.. _`response`: https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponse
