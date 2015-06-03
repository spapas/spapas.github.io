A comprehensive React and Flux tutorial
#######################################

:date: 2015-06-03 14:20
:tags: javascript, python, django, react, flux
:category: javascript
:slug: comprehensive-react-flux-tutorial
:author: Serafeim Papastefanos
:summary: A React and Flux tutorial that tries to be as comprehensive as possible!

.. contents::

Introduction
------------

React_ is a rather new library from Facebook for building dynamic components for web pages.
It introduces a really simple, fresh approach to javascript user interface building. React
allows you to define composable and self-contained HTML components through Javascript (or a special syntax that compiles
to javascript named JSX) and that's all -- it doesn't force you into any specific
framework or architecture, you may use whatever you like. It's like writing pure
HTML but you have the advantage of using classes with all their advantages for your
components (self-contained, composable, reusable, mixins etc).

Although React components can be used however you like in your client-side applications, Facebook proposes a specific
architecture for the data flow of your events/data between the components called Flux_.
It's important to keep in your mind that Flux is not a
specific framework but a way to organize the flow of events and data in your applicition.
Unfortunately, although Flux is a rather simple architecture it is a little difficult to understand
without a proper example (at least it was difficult for me to understand by reading the
Facebook documentation and some tutorials I found).

So, in this tutorial we are going to build a (not-so-simple) single page CRUD application using
React and Flux. Two versions of the same application will be built and explained: One with
React only and one with React and Flux. This will help us understand how
Flux architecture fits to our project and why it greatly improves the experience with React.

Our project
-----------

We are going to built a CRUD single-page application for editing views, let's take a look at how it works:

.. image:: /images/demo.gif
  :alt: Our project
  :width: 780 px

Our application will be seperated to two panels: In  the left one the user will be able to filter (search) for
a book and in the right panel she'll be able to add / edit / delete a book. Everything is supported by
a django-rest-framework_ implemented REST API. You can find the complete source code at
https://github.com/spapas/react-tutorial. I've added a couple of git tags to the source history in
order to help us identify the differences between variou stages of the project (before and
after integrating the Flux architecture).

Django-rest-framework is used in the server-side back-end to create a really simple REST API - I won't
provide any tutorial details on that (unless somebody wants it !), however
you may either use the source code as is or create it from scratch using a different language/framework
or even just a static json file (however you won't see any changes to the data this way). 

For styling (mainly to have a simple grid) we'll use skeleton_. For the ajax calls and some utils we'll
use jquery_.



All client-side code will be contained in the file static/main.js. The placeholder HTML for our
application is:

.. code:: 

  <html>
      <!-- styling etc ignored -->
    <body>
      <h1>Hello, React!</h1>
      <div class="container"><div id="content"></div></div>
    </body>
    <script src="//fb.me/react-0.13.3.js"></script>
    <script src="//fb.me/JSXTransformer-0.13.3.js"></script>
    <script src="//code.jquery.com/jquery-2.1.3.min.js"></script>
    <script type="text/jsx" src="{% static 'main.js' %}"></script>
  </html>
    

A top-level view of the components
----------------------------------

The following image shows how our components are composed:

.. image:: /images/components.png
  :alt: Our components
  :width: 780 px
  
So, the main component of our application is ``BookPanel`` which contains three
components:

* ``SearchPanel``: To allow search (filtering) books based on their title/category
* ``BookForm``: To add/update/delete books
* ``BookTable``: To display all available books - each book is displayed in a ``BookTableRow`` component.

``BookPanel`` is the only component having state -- all other components will be initialized by property
passing. The ``BookPanel`` element will be mounted to the ``#content`` element when the page loads.

The react-only version
----------------------

The first version, using only react (and not flux) will use ``BookPanel`` as a central information HUB.

``SearchPanel``
===============

``SearchPanel`` renders an input element with a value defined by the ``search`` key of this component'same
properties. When this is changed the ``onSearchChanged`` method of the component will be called, which in turn,
retrieves the value of the input (using refs) and passes it to the properties ``onSearchChanged`` callback function.
Finally, with the line ``{this.props.search?<button onClick={this.props.onClearSearch} >x</button>:null}``
we check if the search property contains any text and if yes, we display a clear filter button that will call 
properties onClearSearch method:

.. code::


  var SearchPanel = React.createClass({
    render: function() {
      return (
        <div className="row">
          <div className="one-fourth column">
            Filter: &nbsp;
            <input ref='search' type='text' value={this.props.search} onChange={this.onSearchChanged} />
            {this.props.search?<button onClick={this.props.onClearSearch} >x</button>:null}
          </div>
        </div>
      )
    },
    onSearchChanged: function() {
      var query = React.findDOMNode(this.refs.search).value;
      this.props.onSearchChanged(query);
    }
  });

So, this component uses three properties:

* search which is the text to display in the input box
* onSearchChanged which is called when the contents of the input box are changed
* onClearSearch which is called when the button is pressed

Notice that this component doesn't do anything - for all actions it uses the callbacks passed to it --this
means that exactly the same component would easily be reused in a totally different application or could
be duplicated if we wanted to have a different search component for the book title and category. 
Another thing to notice is that the local ``onSearchChanged`` method is defined only to help us retrieve the
value of the input and use it to call the ``onSearchChanged`` callback. 

``BookTableRow``
================

``BookTable``
=============

``BookForm``
============

``BookPanel``
=============


.. _React: https://facebook.github.io/react/
.. _Flux: https://facebook.github.io/flux/docs/overview.html
.. _django-rest-framework: http://www.django-rest-framework.org/
.. _browserify: http://browserify.org/
.. _watchify: https://github.com/substack/watchify
.. _skeleton: http://getskeleton.com/
.. _jquery: https://jquery.com/