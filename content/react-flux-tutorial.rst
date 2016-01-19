A comprehensive React and Flux tutorial part 2: Flux
####################################################

:date: 2015-07-02 14:20
:tags: javascript, python, django, react, flux
:category: javascript
:slug: comprehensive-react-flux-tutorial-2
:author: Serafeim Papastefanos
:summary: A React and Flux tutorial that tries to be as comprehensive as possible! Part 2 is about Flux.

.. contents::

Introduction
------------

In the `first part of this series <{filename}react-tutorial.rst>`_ we implemented a
not-so-simple one page application with full CRUD capabilities. In this part, we will
modify that application to make it use the Flux architecture. The full source code can
be found at https://github.com/spapas/react-tutorial (tag name react-flux). In the 
In `next part, <{filename}react-flux-complex.rst>`_ we will create an even more complex application
using react/flux!

I recommend reading Facebook's `Flux overview`_ before reading this article -- please
read it even if you find some concepts difficult to grasp (I know I found it difficult
the first time I read it), I will try to explain everything here. Also,
because a rather large number of extra components will need to be created, we are
going to split our javascript code to different files using browserify_ - you can
learn `how to use browserify here <{filename}using-browserify.rst>`_.


Flux components
---------------

To implement the Flux architecture, an application needs to have at least a store and a
dispatcher.

The store is the central place of truth for the application and the dispacher is the central
place of communications. The store should hold the 
state (and any models/DAOs) of the application and notify the react components when this state is changed. Also,
the store will be notified by the dispatcher when an action happens (for example a button is clicked)
so that it will change the state. As a flow, we can think of something like this:

.. code::

  a ui action on a component (click, change, etc) ->
   ^   dispatcher is notified -> 
   |   store is notified (by the dispacher)-> 
   |   store state is changed -> 
   └─  component is notified (by the store) and updated to reflect the change
     
  
  
One thing to keep in mind is that although each flux application will have only one dispatcher, it may
have more stores, depending on the application's architecture and separation of concerns. If there are 
more than store, all will be notified by the dispatcher and change their state (if needed of course).
The ui will pass the action type and any optional parameters to the dispatcher and the dispatcher 
will notify all stores with these parameters.

An optional component in the Flux architecture is the Action. An action is a store related class that
acts as an intermediate between the ui and the dispatcher. So, when a user clicks a button, an action
will be called that will notify the dispatcher. As we will see we can just call the dispatcher directly
from the components ui, but calling it through the Action makes the calls more consistent and creates
an interface.

The react-flux version
----------------------

Since we are using browserify, we will include a single file in our html file with a ``<script>`` tag
and everything else will be included through the ``require`` function. We have the following packages
as requirements for browserify:

.. code::

  "dependencies": {
    "flux": "^2.0.3",
    "jquery": "^2.1.4",
    "react": "^0.13.3",
    "reactify": "^1.1.1"
  }
  
Also, in order to be able to use JSX with browserify, will use the reactify_ transform. To apply it to
your project, change the ``scripts`` of your ``package.json`` to:

.. code::

  "scripts": {
    "watch": "watchify -v -d static/main.js -t reactify -o static/bundle.js",
    "build": "browserify static/main.js -t reactify  | uglifyjs -mc warnings=false > static/bundle.js"
  },

main.js
~~~~~~~

The ``main.js`` file will 
just render the BookPanel component (the ``components.js`` file contains the source for all React components) and call
the ``reloadBooks`` function from ``stores.js`` that will reload all books from the REST API:

.. code::

  var React = require('react');
  var components = require('./components');
  var stores = require('./stores');

  React.render(<components.BookPanel url='/api/books/' />, document.getElementById('content'));

  stores.reloadBooks();

constants.js
~~~~~~~~~~~~
  
Before going into more complex modules, let's present the ``constants.js`` which just
exports some strings that will be passed to the dispatcher to differentiate between each
ui action:

.. code::

  module.exports = {
      BOOK_EDIT: 'BOOK_EDIT',
      BOOK_EDIT_CANCEL: 'BOOK_EDIT_CANCEL',
      BOOK_SAVE: 'BOOK_SAVE',
      BOOK_SEARCH: 'BOOK_SEARCH',
      BOOK_DELETE: 'BOOK_DELETE',
  };

As we can see, these constants are exported as a single object so when we do something like
``var BookConstants = require('./constants')`` we'll the be able to refer to each constant
through ``BookConstants.CONSTANT_NAME``.

actions.js
~~~~~~~~~~
  
The ``actions.js`` creates the dispatcher singleton and a BookActions object that defines the
actions for books. 

.. code::

    var BookConstants = require('./constants')
    var Dispatcher = require('flux').Dispatcher;
    var AppDispatcher = new Dispatcher();

    var BookActions = {
        search: function(query) {
            AppDispatcher.dispatch({
                actionType: BookConstants.BOOK_SEARCH,
                query: query
            });
        },
        save: function(book) {
            AppDispatcher.dispatch({
                actionType: BookConstants.BOOK_SAVE,
                book: book
            });
        },
        edit: function(book) {
            AppDispatcher.dispatch({
                actionType: BookConstants.BOOK_EDIT,
                book: book
            });
        },
        edit_cancel: function() {
            AppDispatcher.dispatch({
                actionType: BookConstants.BOOK_EDIT_CANCEL
            });
        },
        delete: function(bookId) {
            AppDispatcher.dispatch({
                actionType: BookConstants.BOOK_DELETE,
                bookId: bookId
            });
        }
    };
    
    module.exports.BookActions = BookActions;
    module.exports.AppDispatcher = AppDispatcher;
    
As we can see, the BookActions is just a collection of methods that will
be called from the ui. Instead of calling BookActions.search() we could 
just call the dispatch method with the correct parameter object (actionType
and optional parameter), both the BookActions object and the AppDispatcher 
singleton are exported.

The dispatcher is imported from the flux requirement: It offers a functionality
to register callbacks for the various actions as we will see in the 
next module. This is a rather simple class that we could implement ourselves 
(each store passes a callback to the dispatcher that is called on the dispatch
method, passing actionType and any other parameters). The dispatcher also
offers a ``waitFor`` method that can be used to ensure that the dispatch callback
for a store will be finished before another store's dispatch callback (
when the second store uses the state of the first store -- for example 
when implementing a series of related dropdowns ). 


stores.js
~~~~~~~~~

The next module we will discuss is the ``stores.js`` that contains the
``BookStore`` object. 

.. code::

    var $ = require('jquery');
    var EventEmitter = require('events').EventEmitter;
    var AppDispatcher = require('./actions').AppDispatcher;
    var BookConstants = require('./constants')

    var _state = {
        books: [],
        message:"",
        editingBook: null
    }

    var _props = {
        url: '/api/books/'
    }

    var _search = function(query) {
        $.ajax({
            url: _props.url+'?search='+query,
            dataType: 'json',
            cache: false,
            success: function(data) {
                _state.books = data;
                BookStore.emitChange();
            },
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                _state.message = err.toString();
                BookStore.emitChange();
            }
        });
    };

    var _reloadBooks = function() {
        _search('');
    };

    var _deleteBook = function(bookId) {
        $.ajax({
            url: _props.url+bookId,
            method: 'DELETE',
            cache: false,
            success: function(data) {
                _state.message = "Successfully deleted book!"
                _clearEditingBook();
                _reloadBooks();
            },
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                _state.message = err.toString();
                BookStore.emitChange();
            }
        });
    };

    var _saveBook = function(book) {
        if(book.id) {
            $.ajax({
                url: _props.url+book.id,
                dataType: 'json',
                method: 'PUT',
                data:book,
                cache: false,
                success: function(data) {
                    _state.message = "Successfully updated book!"
                    _clearEditingBook();
                    _reloadBooks();
                },
                error: function(xhr, status, err) {
                    _state.message = err.toString()
                    BookStore.emitChange();
                }
            });
        } else {
            $.ajax({
                url: _props.url,
                dataType: 'json',
                method: 'POST',
                data:book,
                cache: false,
                success: function(data) {
                    _state.message = "Successfully added book!"
                    _clearEditingBook();
                    _reloadBooks();
                },
                error: function(xhr, status, err) {
                    _state.message = err.toString()
                    BookStore.emitChange();
                }
            });
        }
    };

    var _clearEditingBook = function() {
        _state.editingBook = null;
    };

    var _editBook = function(book) {
        _state.editingBook = book;
        BookStore.emitChange();
    };

    var _cancelEditBook = function() {
        _clearEditingBook();
        BookStore.emitChange();
    };

    var BookStore = $.extend({}, EventEmitter.prototype, {
        getState: function() {
            return _state;
        },
        emitChange: function() {
            this.emit('change');
        },
        addChangeListener: function(callback) {
            this.on('change', callback);
        },
        removeChangeListener: function(callback) {
            this.removeListener('change', callback);
        }
    });

    AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case BookConstants.BOOK_EDIT:
                _editBook(action.book);
            break;
            case BookConstants.BOOK_EDIT_CANCEL:
                _cancelEditBook();
            break;
            case BookConstants.BOOK_SAVE:
                _saveBook(action.book);
            break;
            case BookConstants.BOOK_SEARCH:
                _search(action.query);
            break;
            case BookConstants.BOOK_DELETE:
                _deleteBook(action.bookId);
            break;
        }
        return true;
    });

    module.exports.BookStore = BookStore;
    module.exports.reloadBooks = _reloadBooks;

The ``stores.js`` module exports only the ``BookStore`` object and the ``reloadBooks`` method (that could also be 
called from inside the module since it's just called when the application is loaded to load the books for the
first time). All other objects/funtions are private to the module. 

As we saw, the ``_state`` objects keep the global state of the application which are the list of books, the book
that is edited right now and the result message for any update we are doing. The ajax methods are more or less
the same as the ones in the react-only version of the application. However, please notice that when the ajax methods
return and have to set the result, instead of setting the state of a React object they are just calling the 
``emitChange`` method of the ``BookStore`` that will notify all react objects that "listen" to this store.
This is possible because the ajax (DAO) methods are in the same module with the store - if we wanted instead
to put them in different modules, we'd just need to add another action (e.g ``ReloadBooks``) that would 
be called when the ajax method returns -- this action would call the dispatcher which would in turn update the 
state of the store.

We can see that we are importing the 
AppDispatcher singleton and, depending on the action type we call the correct method that changes the state. So
when a BookActions action is called it will call the corresponding ``AppDispatcher.register`` case branch which
will call the corresponding state-changing function.

The  BookStore extends the ``EventEmitter`` object (so we need to ``require`` the ``events`` module) in order to
notify the React components when the state of the store is changed. Instead of using ``EventEmitter`` we could
just implement the emit change logic ourselves by saving all the listener callbacks to an array and calling them
all when there's a state change (if we wanted to also add the 'change' parameter to group the listener
callbacks we'd just make the complex more complex, something not needed for our case): 

.. code::

    var BookStore = {
        listeners: [],
        getState: function() {
            return _state;
        },
        emitChange: function() {
            var i;
            for(i=0;i<this.listeners.length;i++) {
                this.listeners[i]();
            }
        },
        addChangeListener: function(callback) {
            this.listeners.push(callback);
        },
        removeChangeListener: function(callback) {
            this.listeners.splice(this.listeners.indexOf(callback), 1);
        }
    };
    
components.js
~~~~~~~~~~~~~
    
Finally, the ``components.js`` module contains all the React components. These are more
or less the same with the react-only version with three differences: 

* When something happens in the ui, the corresponding ``BookAction`` action is called with the needed parameter -- no callbacks are passed between the components
* The ``BookPanel`` component registers with the ``BookStore`` in order to be notified when the state changes and just gets its state from the store -- these values are propagated to all other components through properties
* The ``BookForm`` and ``SearcchPanel`` now hold their own temporary state instead of using the global state -- notice that when a book is edited this book will be propagated to the ``BookForm`` through the book property, however ``BookForm`` needs to update its state through the ``componentWillReceiveProps`` method.

.. code::

    var React = require('react');
    var BookStore = require('./stores').BookStore;
    var BookActions = require('./actions').BookActions;

    var BookTableRow = React.createClass({
        render: function() {
            return (
                <tr>
                    <td>{this.props.book.id}</td>
                    <td>{this.props.book.title}</td>
                    <td>{this.props.book.category}</td>
                    <td><a href='#' onClick={this.onClick}>Edit</a></td>
                </tr>
            );
        },
        onClick: function(e) {
            e.preventDefault();
            BookActions.edit(this.props.book);
        }
    });

    var BookTable = React.createClass({
        render: function() {
            var rows = [];
            this.props.books.forEach(function(book) {
                rows.push(<BookTableRow key={book.id} book={book} />);
            });
            return (
                <table>
                    <thead>
                        <tr>
                            <th>Id</th>
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

    var BookForm = React.createClass({
        getInitialState: function() {
            if (this.props.book) {
                return this.props.book;
            } else {
                return {};
            }
        },
        componentWillReceiveProps: function(props) {
            if (props.book) {
                this.setState(props.book);
            } else {
                this.replaceState({});
            }
        },
        render: function() {
            return(
                <form onSubmit={this.onSubmit}>
                    <label forHtml='title'>Title</label><input ref='title' name='title' type='text' value={this.state.title} onChange={this.onFormChange} />
                    <label forHtml='category'>Category</label>
                    <select ref='category' name='category' value={this.state.category} onChange={this.onFormChange} >
                        <option value='CRIME' >Crime</option>
                        <option value='HISTORY'>History</option>
                        <option value='HORROR'>Horror</option>
                        <option value='SCIFI'>SciFi</option>
                    </select>
                    <br />
                    <input type='submit' value={this.state.id?"Save (id = " +this.state.id+ ")":"Add"} />
                    {this.state.id?<button onClick={this.onDeleteClick}>Delete</button>:""}
                    {this.state.id?<button onClick={this.onCancelClick}>Cancel</button>:""}
                    {this.props.message?<div>{this.props.message}</div>:""}
                </form>
            );
        },
        onFormChange: function() {
            this.setState({
                title: React.findDOMNode(this.refs.title).value,
                category: React.findDOMNode(this.refs.category).value
            })
        },
        onSubmit: function(e) {
            e.preventDefault();
            BookActions.save(this.state)
        },
        onCancelClick: function(e) {
            e.preventDefault();
            BookActions.edit_cancel()
        },
        onDeleteClick: function(e) {
            e.preventDefault();
            BookActions.delete(this.state.id)
        }
    });

    var SearchPanel = React.createClass({
        getInitialState: function() {
            return {
                search: '',
            }
        },
        render: function() {
            return (
                <div className="row">
                    <div className="one-fourth column">
                        Filter: &nbsp;
                        <input ref='search' name='search' type='text' value={this.state.search} onChange={this.onSearchChange} />
                        {this.state.search?<button onClick={this.onClearSearch} >x</button>:''}
                    </div>
                </div>
            )
        },
        onSearchChange: function() {
            var query = React.findDOMNode(this.refs.search).value;
            if (this.promise) {
                clearInterval(this.promise)
            }
            this.setState({
                search: query
            });
            this.promise = setTimeout(function () {
                BookActions.search(query);
            }.bind(this), 200);
        },
        onClearSearch: function() {
            this.setState({
                search: ''
            });
            BookActions.search('');
        }
    });

    var BookPanel = React.createClass({
        getInitialState: function() {
            return BookStore.getState();
        },
        render: function() {
            return(
                <div className="row">
                    <div className="one-half column">
                        <SearchPanel></SearchPanel>
                        <BookTable books={this.state.books} />
                    </div>
                    <div className="one-half column">
                        <BookForm
                            book={this.state.editingBook}
                            message={this.state.message}
                        />
                    </div>
                    <br />
                </div>
            );
        },
        _onChange: function() {
            this.setState( BookStore.getState() );
        },
        componentWillUnmount: function() {
            BookStore.removeChangeListener(this._onChange);
        },
        componentDidMount: function() {
            BookStore.addChangeListener(this._onChange);
        }
    });

    module.exports.BookPanel = BookPanel ;

Only the ``BookPanel`` is exported -- all other react components will be private to the module.
    
We can see that, beyond BookPanel, the code of all other components
are more or less the same. However, *not* having to pass callbacks for state upddates
is a huge win for readability and DRYness. 

Explaining the data flow
------------------------

I've added a bunch of console.log statements to see how the data/actions flow between
all the components when the "Edit" book is clicked. So, when we click "Edit" we see
the following messages to our console:

.. code:: 

    Inside BookTableRow.onClick
    Inside BookActions.edit
    Inside AppDispatcher.register
    Inside AppDispatcher.register case BookConstants.BOOK_EDIT
    Inside _editBook
    Inside BookStore.emitChange
    Inside BookPanel._onChange
    Inside BookForm.componentWillReceiveProps
    Inside BookForm.render

First of all the ``onClick`` method of ``BookTableRow`` will be called (which is the onClick property of the
a href link) which will call ``BookActions.edit`` and pass it the book of that specific row. The ``edit``
method will create a new dispatcher object by setting the ``actionType`` and passing the ``book`` and
pass it to ``AppDispatcher.register``. ``register`` will go to the ``BookConstants.BOOK_EDIT`` case branch
which will call the private ``_editBook`` function. ``_editBook`` will update the state of the store (by 
setting the ``_state.editingBook`` property and will call the ``BookStore.emitChange`` method 
which calls the dispatcher's emit method, so all listening components will update. We only have one
component that listens to this emit, ``BookPanel`` whose ``_onChange`` method is called. This method
gets the application state from the ``BookStore`` and updates its own state. Now, the state will be
propagated through properties - for example, for ``BookForm``, first its ``componentWillReceiveProps``
method will be called (with the new properties) and finally its ``render`` method!

So the full data flow is something like this:

.. code:: 

    user action/callback etc -> 
      component calls action -> 
        dispatcher informes stores -> 
          stores set their state ->
            state holding components are notified and update their state -> 
              all other components are updated through properties


A better code organization
--------------------------

As you've seen, I've only created four javascript modules (components, stores, actions and constants)
and put them all in the same folder. I did this for clarity and to keep everything together since 
our tutorial is a very small project. Facebook proposes a much better organization that what I did
as can be seen in the `TodoMVC tutorial`_: Instead of putting everything to a single folder, create
a different foloder for each type of object: actions (for all your actions), components (for all
your React components), constants and stores and put inside the objects each in a different javascript
module, for example, the components folder should contain the following files: 

* BookTable.react.js
* BookTableRow.react.js
* BookForm.react.js
* BookPanel.react.js
* SearchPanel.react.js

Each one will export only the same-named React component and ``require`` only the components that it
uses. 

If you want to see the code of this tutorial organized like this go to the tag ``react-flux-better-organization``.


Conclusion
----------

In this two-part series we saw how we can create a full CRUD application with React.js and how can
we enable it with the Facebook proposed Flux architecture. Comparing the react-only with the react-flux
version we can see that we added a number of objects in the second version (dispatcher, store, actions, constants)
whose usefulness may not be obvious from our example. However, our created application (and especially
the better organized version) is war-ready and can easily fight any complexities that we throw to it!
Unfortunately, if we really wanted to show the usefulness of the Flux architecture we'd need to create
a really complex application that won't be suitable for a tutorial.

However, we can already understand the obvious advantages of the React / Flux architecture:

* Components can easily be re-used by changing their properties - DRY
* Easy to grasp (but a little complex) data flow between components and stores 
* Separation of concerns - react components for the view, stores to hold the state/models, dispatcher to handle the data flow 
* Really easy to test - all components are simple objects and can be easily created fom tests
* Works well for complex architectures - one dispatcher, multiple stores/action collections, react components only interact with actions and get their state from stores

I've tried to make the above as comprehensive as possible for the readers of these posts
(and also resolve some of my own questions). I have to mention again that although React/Flux may
seem complex at a first glance, when it is used in a complex architecture it will shine and 
make everything much easier. Everything is debuggable and we can always understand what's
really going on! This is in contrast with more complex frameworks that do various hidden
stuff (two way data binding, magic in the REST etc) where, although it is easier to
create a simple app, moving to something more complex (and especially debugging it) is a real nightmare!




.. _React: https://facebook.github.io/react/
.. _`Flux overview`: https://facebook.github.io/flux/docs/overview.html
.. _django-rest-framework: http://www.django-rest-framework.org/
.. _browserify: http://browserify.org/
.. _watchify: https://github.com/substack/watchify
.. _skeleton: http://getskeleton.com/
.. _jquery: https://jquery.com/
.. _bind: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind
.. _`functions are objects`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function
.. _`TodoMVC tutorial`: https://facebook.github.io/flux/docs/todo-list.html
.. _`reactify`: https://github.com/andreypopp/reactify
