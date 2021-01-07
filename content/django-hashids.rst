Using hashids to hide ids of objects in Django
##############################################

:date: 2021-01-07 12:20
:tags: django, hashids, python
:category: django
:slug: django-hashides
:author: Serafeim Papastefanos
:summary: How to hide the ids (primary keys) of your objects in Django using the hashids library

A common pattern in Django urls is to have the following setup for CRUD operations of your objects. Let's suppose we 
have a ``Ship`` object. It's CRUD urls would be something like:

* ``/ships/create/`` To add a new object
* ``/ships/list/`` To display a list of your objects
* ``/ships/detail/id/`` To display the particular object with that id (primary key)
* ``/ships/update/id/`` To update/edit the particular object with that id (primary key) 
* ``/ships/delete/id/`` To delete the particular object with that id (primary key) 

This is very easy to implement using class based views. For example for the detail view add the following to your views.py:

.. code::

  class ShipDetailView(DetailView):
      model = models.Ship

and then in your urls.py add the line:

.. code::

  urlpatterns = [
    # ...
    path(
        "detail/<int:pk>/",
        login_required(views.ShipDetailView.as_view()),
        name="ship_detail",
    ),

This path means that it expects an integer (`int`) which will be used as the primary key of the ship (`pk`).

Now, a common requirement if you are using integers as primary keys is to not display them to the public. So you 
shouldn't allow the users to write something like ``/ships/detail/43`` to see the details of ship 43. Even if you
have add proper authorization (each user only sees the ids he has access to) you are opening a window for abuse. Also
you don't want the users to be able to estimate how many objects there are in your database (if a user creates a 
new ship he'll get the latest id and know approximately how many ships are in your database).

One simple requirement is to use some encryption mechanism to encode the ids to some string and display that string
to the public urls. When you receive the string you'll then decode it to get the id. 

Thankfully, not only there's a particular library that makes this whole encode/decode procedure very easy but Django
has functionality to make trivial to integrate this functionality to an existing project with only miniman changes!

The library I propose for this is called hashids-python_. This is the python branch of the hashids_ library that works 
for many languages. If you take a look at the documentation you'll see that it can be used like this:

.. code::

  from hashids import Hashids
  hashids = Hashids()
  hashid = hashids.encode(123) # 'Mj3'
  ints = hashids.decode('xoz') # (456,)

This library offers two useful utilities: Define a random salt so that the generated hashids will be unique for your app
and add a minimum hash length so that the real length of the id will be obfuscated. I've found out that a length of 8 characters 
will be more than enough to encode all possible ids up to 99 billion: 

.. code::
  
  hashids = Hashids(min_length=8)
  len(hashids.encode(99_999_999_999)) # 8

This is more than enough since by default django will use an integer to store the primary keys which is around 4 billion (you actually can 
 use 7 characters to encode up to 5 billion but I prefer even numbers.

Finally, you can use a different alphabet, for example to use all greek characters:

.. code:: 

  hashids = Hashids(alphabet='ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ')
  hashids.encode(123) # 'ΣΝΦ'

This isn't recommended though for our case because not all characters are url-safe.

To integrate the hashids with Django we are going to use a `custom path converter`_. The custom path converter
is similar to the ``int`` portion of the ``"detail/<int:pk>/"`` of the url i.e it will retrieve something and convert it
to a python object. To implement your custom path converter just add a file named utils.py in one of your applications with
the following conents:


.. code::

  from hashids import Hashids
  from django.conf import settings

  hashids = Hashids(settings.HASHIDS_SALT, min_length=8)


  def h_encode(id):
      return hashids.encode(id)


  def h_decode(h):
      z = hashids.decode(h)
      if z:
          return z[0]


  class HashIdConverter:
      regex = '[a-zA-Z0-9]{8,}'

      def to_python(self, value):
          return h_decode(value)

      def to_url(self, value):
          return h_encode(value)


The above will generate a ``hashids`` global object with a min length of 8 as discussed above and retrieving 
a custom salt from your settings (just add ``HASHIDS_SALT=some_random_string`` to your project settings). The
``HashIdConverter`` defines a regex that will match the default aplhabet that hasid uses and two methods to convert 
from url to python and vice versa. Notice that ``hashids.decode`` returns an array so we'll retrieve the first number only.

To use that custom path converter you will need to add the following lines to your urls.py to register your 
``HashIdConverter`` as ``hashid``:

.. code::

  from core.utils import HashIdConverter

  register_converter(HashIdConverter, "hashid")

and then use it in your urls.py like this:

.. code::

  urlpatterns = [
    # ...
    path(
        "detail/<hashid:pk>/",
        login_required(views.ShipDetailView.as_view()),
        name="ship_detail",
    ),

That's it! No other changes are needed to your CBVs! The ``hashid`` will match the hashid in the url and convert it to 
the model's pk using the to_python method we defined above!

Of course you should also add the opposite direction (i.e convert from the primary key to the hashid). To do that we'll
add a ``get_absolute_url`` method to our Ship model, like this:

.. code::

  class Ship(models.Model):  
    def get_hashid(self):
        return h_encode(self.id)
    
    def get_absolute_url(self):
        return reverse("ship_detail", args=[self.id])

Notice that you just call the ``reverse`` function passing ``self.id``; everything else will be done 
automatically from the ``hashid`` custom path generator ``to_url`` method. I've also added a ``get_hashid`` 
method to my model to have quick access to the id in case I need it.

Now you don't have any excuses to not hide your database ids from the public!


.. _`custom path converter`: https://docs.djangoproject.com/en/3.1/topics/http/urls/#registering-custom-path-converters
.. _hashids-python: https://github.com/davidaurelio/hashids-python
.. _hashids: https://hashids.org/