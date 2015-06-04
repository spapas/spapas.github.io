A comprehensive React and Flux tutorial part 1: React
#####################################################

:date: 2015-06-04 14:20
:tags: javascript, python, django, react, flux
:category: javascript
:slug: comprehensive-react-flux-tutorial
:author: Serafeim Papastefanos
:summary: A React and Flux tutorial that tries to be as comprehensive as possible! Part 1 is about React.

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

So, in this two-part tutorial we are going to build a (not-so-simple) single page CRUD application using
React and Flux. Two versions of the same application will be built and explained: One with
React (this part) only and one with React and Flux (part two). This will help us understand how
Flux architecture fits to our project and why it greatly improves the experience with React.

**Warning**: This is not an introduction to react. Before reading this you need
to be familiar with basic react usage, having read  at least the following three
pages from react documentation:

* https://facebook.github.io/react/docs/getting-started.html
* https://facebook.github.io/react/docs/tutorial.html
* https://facebook.github.io/react/docs/thinking-in-react.html

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

We are using the version 0.13.3 of react and the same version of the JSXTransformer to translate JSX
code to pure javascript.

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

So, this component has three properties:

* search which is the text to display in the input box
* onSearchChanged (callback) which is called when the contents of the input box are changed
* onClearSearch (callback) which is called when the button is pressed

Notice that this component doesn't do anything - for all actions it uses the callbacks passed to it --this
means that exactly the same component would easily be reused in a totally different application or could
be duplicated if we wanted to have a different search component for the book title and category.

Another thing to notice is that the local ``onSearchChanged`` method is defined only to help us retrieve the
value of the input and use it to call the ``onSearchChanged`` callback. Instead, we could just call the
passed
``this.props.onSearchChanged`` -- however to do this we'd need a way to find the value of the input. This
could be done if we added a ref to the included ``SearchPanel`` from the parent component, so
we'd be able to use something like
``React.findDOMNode(this.refs.searchPanel.refs.search).value`` to find out the value of the input
(see that we use a ref to go to the searchPanel component and another ref to go to input component).

Both versions (getting the value directly from the child component or using the callback) could be used, however I
believe that the callback version defines a more clear interface since the parent component shouldn't need
to know the implementation details of its children.


``BookTableRow``
================

``BookTableRow`` will render a table row by creating a simple table row that will contain the ``title``
and ``category`` attributes of the passed book property and an edit link that will call the ``handleEditClickPanel``
property by passing the id of that book:

.. code::

  var BookTableRow = React.createClass({
    render: function() {
      return (
        <tr>
          <td>{this.props.book.title}</td>
          <td>{this.props.book.category}</td>
          <td><a href='#' onClick={this.onClick}>Edit</a></td>
        </tr>
      );
    },
    onClick: function(id) {
      this.props.handleEditClickPanel(this.props.book.id);
    }
  });

This component is used by ``BookTable`` to render each one of the books.

``BookTable``
=============

This component create the left-side table using an array of ``BookTableRow``s by passing it each one of the
books of the ``books`` array property. The ``handleEditClickPanel``
property is retrieved from the parent of the component and passed as is to the row.

.. code::

  var BookTable = React.createClass({
    render: function() {
      var rows = [];
      this.props.books.forEach(function(book) {
        rows.push(<BookTableRow key={book.id} book={book} handleEditClickPanel={this.props.handleEditClickPanel}  />);
      }.bind(this));
      return (
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Category</th>
              <th>Edit</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      );
    }
  });

The key attribute is used by React to uniquely identify each component - we are using the id (primary key)
of each book. Before continuing with the other components, I'd like to explain what is the purpose of that
strange ``bind`` call!

Interlude: The ``bind`` function method
=======================================

bind_ is a method of the function javascript object, since in javascript `functions are objects`_! This
method is useful for a number of things, however here we use it to set the ``this`` keyword of the
anonymous function that is passed to foreach to the ``this`` keyword of the ``render`` method of ``BookTable``,
which will be the current BookTable instance.

To make things crystal: Since we are using an anonymous function to pass to ``forEach``, this anonymous
function won't have a ``this`` keyword set to the current ``BookTable`` object so we will get an error
that ``this.props`` is undefined. That's why we use bind to set ``this`` to the current ``BookTable``. If
instead of using the anonymous function we had created a ``createBookTableRow`` method inside the
``BookTable`` object that returned the ``BookTableRow`` and passed ``this.createBookTableRow`` to
``forEach``, we wouldn't have to use bind (notice that we'd also need to make rows a class attribute
and  refer to it through ``this.rows`` for this to work).

``BookForm``
============

``BookForm`` will create a form to either create a new book or update/delete an existing one. It has a ``book`` object
property - when this object has an ``id`` (so it is saved to the database) the update/delete/cancel buttons will be shown,
when it doesn't have an id the add button will be shown.

.. code::

  var BookForm = React.createClass({
    render: function() {
      return(
        <form onSubmit={this.props.handleSubmitClick}>
          <label forHtml='title'>Title</label><input ref='title' name='title' type='text' value={this.props.book.title} onChange={this.onChange}/>
          <label forHtml='category'>Category</label>
          <select ref='category' name='category' value={this.props.book.category} onChange={this.onChange} >
            <option value='CRIME' >Crime</option>
            <option value='HISTORY'>History</option>
            <option value='HORROR'>Horror</option>
            <option value='SCIFI'>SciFi</option>
          </select>
          <br />
          <input type='submit' value={this.props.book.id?"Save (id = " +this.props.book.id+ ")":"Add"} />
          {this.props.book.id?<button onClick={this.props.handleDeleteClick}>Delete</button>:null}
          {this.props.book.id?<button onClick={this.props.handleCancelClick}>Cancel</button>:null}
          {this.props.message?<div>{this.props.message}</div>:null}
        </form>
      );
    },
    onChange: function() {
      var title = React.findDOMNode(this.refs.title).value;
      var category = React.findDOMNode(this.refs.category).value;
      this.props.handleChange(title, category);
    }
  });

As we can see, this component uses many properties -- most are passed callbacks functions for various actions:

* ``book``: This will either be a new book object (without and id) when adding one or an existing (from the database) book when updating one.
* ``message``: To display the result of the last operation (save/delete) -- this is passed by the parent and probably it would be better if I had put it in a different component (and added styling etc).
* ``handleSubmitClick``: Will be called when the submit button is pressed to save the form (either by adding or updating).
* ``handleCancelClick``: Will be called when the cancel button is pressed -- we decide that we want actually want to edit a book.
* ``handleDeleteClick``: Will be called when the delete button is pressed.
* ``handleChange``: Will be called whenever the title or the category of the currently edited book is changed through the local onChange method. The onChange will retrieve that values of title and category and pass them to handleChange to do the state update. As already discussed, we could retrieve the values immediately from the parent but this creates a better interface to our component.


``BookPanel``
=============

The ``BookPanel`` component will contain all other components, will keep the global state
and will also act as a central communications HUB between the components and the server. Because
it is rather large class, I will explain it in three parts:

Component methods
~~~~~~~~~~~~~~~~~

In the first part of ``BookPanel``, its react component methods will be presented:

.. code::

  var BookPanel = React.createClass({
    getInitialState: function() {
      return {
        books: [],
        editingBook: {
          title:"",
          category:"",
        },
        search:"",
        message:""
      };
    },
    render: function() {
      return(
        <div className="row">
          <div className="one-half column">
            <SearchPanel
              search={this.state.search}
              onSearchChanged={this.onSearchChanged}
              onClearSearch={this.onClearSearch}
            />
            <BookTable books={this.state.books} handleEditClickPanel={this.handleEditClickPanel} />
          </div>
          <div className="one-half column">
            <BookForm
              book={this.state.editingBook}
              message={this.state.message}
              handleChange={this.handleChange}
              handleSubmitClick={this.handleSubmitClick}
              handleCancelClick={this.handleCancelClick}
              handleDeleteClick={this.handleDeleteClick}
            />
          </div>
        </div>
      );
    },
    componentDidMount: function() {
      this.reloadBooks('');
    },
    // To be continued ...
    
    
``getInitialState`` is called the first time the component is created or mounted (attached to an HTML component in the page
and should return the initial values of the state - here we return an object with empty placeholders. ``componentDidMount``
will be called *after* the component is mounted and that's the place we should do any initializationn -- here we call the
``reloadBooks`` method (with an empty search string) to just retrieve all books. Finally, the ``render`` method creates a
``div`` that will contain all other components and initializes their properties with either state variables or object methods
(these are the callbacks that were used in all other components).

Non-ajax object methods
~~~~~~~~~~~~~~~~~~~~~~~

.. code::

  // Continuing from above
  onSearchChanged: function(query) {
    if (this.promise) {
      clearInterval(this.promise)
    }
    this.setState({
      search: query
    });
    this.promise = setTimeout(function () {
      this.reloadBooks(query);
    }.bind(this), 200);
  },
  onClearSearch: function() {
    this.setState({
      search: ''
    });
    this.reloadBooks('');
  },
  handleEditClickPanel: function(id) {
    var book = $.extend({}, this.state.books.filter(function(x) {
      return x.id == id;
    })[0] );

    this.setState({
      editingBook: book,
      message: ''
    });
  },
  handleChange: function(title, category) {
    this.setState({
      editingBook: {
        title: title,
        category: category,
        id: this.state.editingBook.id
      }
    });
  },
  handleCancelClick: function(e) {
    e.preventDefault();
    this.setState({
      editingBook: {}
    });
  },
  // to be continued ...

All the above function change the ``BookPanel`` state so that the properties of the child components will
also be updated:

* ``onSearchChanged`` is called when the search text is changed. The behavior here is interesting: Instead of immediately reloading the books, we create a timeout to be executed after 200 ms (also notice the usage of the ``bind`` function method to allow us call the ``reloadBooks`` method). If the user presses a key before these 200 ms, we cancel the previous timeout (using ``clearInterval``) and create a new one. This technique greatly reduces ajax calls to the server when the user is just typing something in the search box -- we could even increase the delay to reduce even more the ajax calls (but hurt the user experience a bit since the user will notice that his search results won't be updated immediately).
* ``onClearSearch`` is called when the clear filter button is pressed and removes the search text and reloads all books.
* ``handleEditClickPanel`` is called when the edit link of a ``BookTableRow`` is clicked. The book with the passed ``id`` will be found (using filter) and then a clone of it will be created with (``$.extend``) and will be used to set the ``editingBook`` state attribute. If instead of the clone we passed the filtered book object we'd see that when the title or category in the ``BookForm`` were changed they'd also be changed in the ``BookTableRow``!
* ``handleChange`` just changes the state of the currently edited book based on the values passed (it does not modify the id of the book)
* ``handleCancelClick`` when the cancel editing is pressed we clear the ``editingBook`` state attribute. Notice the ``e.preventDefault()`` method that needs to be there in order to prevent the form from submitting since the form submitting would result in an undesirable full page reload!

Ajax object methods
~~~~~~~~~~~~~~~~~~~

Finally, we need a buncch of object methods that use ajax calls to retrieve or update books:

.. code::

    // Continuing from above
    reloadBooks: function(query) {
      $.ajax({
        url: this.props.url+'?search='+query,
        dataType: 'json',
        cache: false,
        success: function(data) {
          this.setState({
            books: data
          });
        }.bind(this),
        error: function(xhr, status, err) {
          console.error(this.props.url, status, err.toString());
          this.setState({
            message: err.toString(),
            search: query
          });
        }.bind(this)
      });
    },
    handleSubmitClick: function(e) {
      e.preventDefault();
      if(this.state.editingBook.id) {
        $.ajax({
          url: this.props.url+this.state.editingBook.id,
          dataType: 'json',
          method: 'PUT',
          data:this.state.editingBook,
          cache: false,
          success: function(data) {
            this.setState({
              message: "Successfully updated book!"
            });
            this.reloadBooks('');
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
            this.setState({
              message: err.toString()
            });
          }.bind(this)
        });
      } else {
        $.ajax({
          url: this.props.url,
          dataType: 'json',
          method: 'POST',
          data:this.state.editingBook,
          cache: false,
          success: function(data) {
            this.setState({
              message: "Successfully added book!"
            });
            this.reloadBooks('');
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
            this.setState({
              message: err.toString()
            });
          }.bind(this)
        });
      }
      this.setState({
        editingBook: {}
      });
    },
    handleDeleteClick: function(e) {
    e.preventDefault();
    $.ajax({
      url: this.props.url+this.state.editingBook.id,
      method: 'DELETE',
      cache: false,
      success: function(data) {
        this.setState({
            message: "Successfully deleted book!",
            editingBook: {}
        });
        this.reloadBooks('');
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
        this.setState({
            message: err.toString()
        });
      }.bind(this)
      });
    },
  });

* ``reloadBooks`` will try to load the books using an ajax GET and pass its query parameter to filter the books (or get all books if query is an empty string). If the ajax call was successfull the state will be updated with the retrieved books and the search text (to clear the  search text when we reload because of a save/edit/delete) while if there was an error the state will be updated with the error message.
* ``handleSubmitClick`` checks if the state's ``editingBook`` has an id and  will do either a POST to create a new book or a PUT to update the existing one. Depending on the result of the operation will either reload books and clear the editingBook or set the error message.
* ``handleDeleteClick`` will do a DELETE to delete the state's ``editingBook`` and clear it.

Notice that all success and error functions above were binded to ``this`` so
that they could update the state of the current ``BookPanel`` object.

Local state
-----------

One decision that we took in ``BookForm`` (and also to the ``SearchPanel`` before) is to *not* keep a local state for the
book that is edited. This means that whenever the value of the ``title`` or ``category`` is changed the parent
component will be informed (through ``handleChange``) so that it will change its state and the new values will
be passed down to ``BookForm`` as properties so our changes will be reflected to the inputs. To make it more
clear, when you press a letter on the ``title`` input:

* the ``onChange`` method of ``BookForm`` will be called,
* it will get the values of both ``title`` and ``category`` fields
* and call ``handleChange`` with these values.
* The ``handleChange`` method of  ``BookPanel`` will update the ``editingBook`` state attribute,
* so the ``book`` property of ``BookForm`` will be also updated
* and the new value of the ``title`` will be displayed (since the components will be re-rendered due to the state update)

Conceptually, the above seems like a lot of work for just pressing a simple key! However, due to how react
is implemented (virtual DOM) it won't actually introduce any performance problems in our application.
If nevertheless we wanted to have a local state of the currently edited book inside the ``BookForm`` then we'd need to use
``state.book`` and update the state using the ``componentWillReceiveProps`` method of ``BookForm``: If we
have a book to edit in the properties then copy it to the state or else just create an empty book. Also,
the ``onChange`` method of the ``BookForm`` won't need to notify the parent component that there is a
state change (but only update the local state) and of course when the submit button is pressed the
current book should be passed to the parent component (to either save it or delete it) since it won't
know the book that is currently edited.



Conclusion to the first part
----------------------------



.. _React: https://facebook.github.io/react/
.. _Flux: https://facebook.github.io/flux/docs/overview.html
.. _django-rest-framework: http://www.django-rest-framework.org/
.. _browserify: http://browserify.org/
.. _watchify: https://github.com/substack/watchify
.. _skeleton: http://getskeleton.com/
.. _jquery: https://jquery.com/
.. _bind: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind
.. _`functions are objects`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function