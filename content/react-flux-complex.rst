A (little more) complex react and flux example
##############################################

:date: 2015-09-08 12:55
:tags: javascript, python, django, react, flux
:category: javascript
:slug: more-complex-react-flux-example
:author: Serafeim Papastefanos
:summary: A (little more) complex React and Flux example, continuing from the previous posts.

.. contents::

Introduction
------------

In `previous <{filename}react-tutorial.rst>`_
`two <{filename}react-flux-tutorial.rst>`_ parts of this series, we have seen
how we could implement a
not-so-simple single page application with full CRUD capabilities
using react only (in the `first part <{filename}react-tutorial.rst>`_ ) and then how to
change it to use the flux architecture (in the `second part <{filename}react-flux-tutorial.rst>`_).

In this, third, part, we will
add some more capabilities to the previous app
to prove how easy it is to create complex apps
and continue the discussion on
the Flux architecture. The source code of this project
can
be found at https://github.com/spapas/react-tutorial (tag name react-flux-complex).

Here's a demo of the final application:

.. image:: /images/demo2.gif
  :alt: Our project
  :width: 780 px

We can see that, when compared to the previous version this one has:

* Sorting by table columns
* Pagination
* Message for loading
* Client side url updating (with hashes)
* Cascading drop downs (selecting category will filter out subcategories)
* Integration with jquery-ui datepicker
* Add a child object (author)
* Add authors with a modal dialog (popup)
* Delete authors (using the "-" button)
* Colored ajax result messages (green when all is ok, red with error)
* A statistics panel (number of books / authors)

In the paragraphs below, beyond the whole architecture, we'll see
a bunch of techniques such as:

* Creating reusable flux components
* Integrating react with jquery
* Creating cascading dropdowns
* Updating URLs with hashes
* Adding pagination/sorting/querying to a table of results
* Displaying pop ups

More about Flux components
--------------------------

Before delving into the source code of the above application, I'd like to
make crystal what is the proposed way to call methods in the flux chain
and which types of components can include other types of components. Let's
take a look at the following diagram:

.. image:: /images/react_flux_deps1.png
  :alt: flux dependencies
  :width: 480 px

The arrows display the dependencies of the Flux architecture - an arrow
from X to Y means that a component of type Y could depend on an Component
of type X (of example, a store could depend on an action or another store
but not on a panel).

In more detail, we can see that in the top of the hierarchy,
having no dependencies are the
Dispatcher and the Constants. The Dispatcher is just a single component
(which actually is a singleton - only one dispatcher exists in each
single page react-flux application)
that inherits from the Facebook's dispatcher and is imported by the
action components (since action methods defined in action components
call the ``dispatch`` method of the dispatcher passing the correct
parameters) and the stores which do the real actions when an action
is dispatched, depending on the action type. The Constant components
define constant values for the action types and are used by both
the actions (to set the action types to the dispatch calls) and by
the stores to be used on the switch statement when an action is
dispatched. As an example, for BookActions we have the following

.. code::

    var BookConstants = require('../constants/BookConstants')
    var AppDispatcher = require('../dispatcher/AppDispatcher').AppDispatcher;

    var BookActions = {
        change_book: function(book) {
            AppDispatcher.dispatch({
                actionType: BookConstants.BOOK_CHANGE,
                book: book
            });
        },
    // Other book actions [...]

and for BookStore

.. code::

    var $ = require('jquery');
    var AppDispatcher = require('../dispatcher/AppDispatcher').AppDispatcher;
    var BookConstants = require('../constants/BookConstants')

    // [...]

    BookStore.dispatchToken = AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case BookConstants.BOOK_EDIT:
                _editBook(action.book);
            break;
    // [...] other switch branches

An interesting thing to see is that the actions depend only on the Dispatcher
and on the Constants, while the stores also depend on actions (not only
from the same action types as the store type, for example AuthorStore depends
on both AuthorActions and MessageActions) and on *other* stores. This means
that the actions should be a "clean" component: Just declare your action methods
whose only purpose is to pass the action type along with the required parameters
to the dispatcher.

On the other hand, the stores are depending on both actions and other stores.
The action dependency is because sometimes when something is done in a store
we need to notify another store to do something as a response to that. For
example, in our case, when a book is updated we need to notify the message
store to show the "Book updated ok" message. This preferrably should not be done by
directly calling the corresponding method on the message store but instead
by calling the corresponding action of MessageAction and passing the correct
parameters (actually, the method that updates the message in MessageStore
should be a private method that is called *only* through the action).

One thing to notice here is that you *cannot* call (and dispatch) an action in the
same call stack (meaning it is directly called) as of another dispatch or you'll get a
``Invariant Violation: Dispatch.dispatch(...): Cannot dispatch in the middle of a dispatch.``
error in your javascript console. Let's see an example of what this means and how
to avoid it because its a common error. Let's say that we have the following
code to a store:

.. code::

    AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case Constants.TEST_ERR:
                TestActions.action1();
            break;
            case Constants.TEST_OK1:
                setTimeout(function() {
                    TestActions.action1();
                }, 0);

            break;
            case Constants.TEST_OK2:
                $.get('/get/', function() {
                    TestActions.action1();
                });

            break;
        }
        return true;
    });

Here, the ``TEST_ERR`` branch will throw an error because the ``TestAction.action1`` is *in the same call stack*
as this dispatch! On the other hand, both ``TEST_OK1`` and ``TEST_OK2`` will work: ``TEST_OK2`` is the most
usual, since most of the times we want to call an action as a result of an ajax call - however, sometimes we
want to call an action without any ajax -- in this case we use the setTimeout (with a timeout of 0 ms) in
order to move the call to ``TestActions.action1()`` to a different call stack.


Now, as I mentioned before, there's also a *different-store* dependency on stores.
This dependency is needed because some stores may offer public methods for other stores to use
(methods that don't actually need to be dispatched through the dispatcher) and
for the ``waitFor`` method , in case there are two different
stores that respond to a single action and want to have one store executing
its dispatch method before the other.
(the waitFor method takes the dispatchToken, which is the result of ``Dispatcher.register`` of
a different store as a parameter in order to wait for that action to finish).

Finally, the Panels depend on both actions (to initiate an action as a response
to user input) and stores (to read the state of the each required store when it
is changed). Of course, not all panels actually depend on stores, since as we
already know the state of a React app should be kept as high in the hierarchy
as possible, so a central component will get the state of a store and pass the
required state attributes to its children through parameters. On the other
hand, every component that responds to user input will have to import
am action object and call the corresponding method -- we should never pass
callbacks from a parent to a child component as a parameter anymore *unless*
we want to make the component reusable (more on this later).

Finally, as expected, because of their hierarchy the compoents depend on their
child components (a BookTable depends on a BookTableRow etc).


Explaining the application components
-------------------------------------

There are a lot of components that are needed for
the above application. A bird's eye view of the components
and their hierarchies can be seen on the following figure:

.. image:: /images/complex_react_components.png
  :alt: Our components
  :width: 780 px


We will first explain a bit the components that could be easily reused
by other applications and after that the components that are specifically
implemented for our book/author single page application.

Reusable application components
-------------------------------

We can see that beyond the specific components (``BookPanel``, ``BookTable`` etc)
there's a bunch of more general components (``DropDown``, ``DatePicker``, ``PagingPanel``, ``SearchPanel``,
``MessagePanel``) that have names like they could be used by other applications (for example every application
that wants to implement a DropDown could use our component) and not only by the
Book-Author application. Let's take a quick look at these components and if they
are actually reusable:


DropDown.react.js
=================

.. code::

    var React = require('react');

    var DropDown = React.createClass({
        render: function() {
            var options = [];
            options.push(<option key='-1' value='' >---</option>);
            if(this.props.options) {
                this.props.options.forEach(function(option) {
                    options.push(<option key={option.id} value={option.id}>{option.name}</option>);
                });
            }

            return(
                <select ref='dropdown' value={this.props.value?this.props.value:''} onChange={this.onFormChange} >
                    {options}
                </select>
            );
        },
        onFormChange: function() {
            var val = React.findDOMNode(this.refs.dropdown).value
            this.props.dropDownValueChanged(val);
        }
    });

    module.exports.DropDown = DropDown;

What we see here is that this component does not actually have a local state and will need three parameters:

- the list of options (``props.options``)
- the curently selected option (``props.value``)
- a callback to be called when the dropdown is changed (``props.dropDownValueChanged``)

By passing the above three parameters this dropdown component can be reused whenever a dropdown is needed!
As we can see here we need to pass a callback function to this dropdown and call the corresponding action
directly. This is important to have a reusable component: The component that includes each dropdown decides
which should be the action on the dropdown value change. Another option if we wanted to avoid callbacks
would be to pass an identifier as a property for each dropdown and the dropdown would call a generic
dropdown action and passing this identifier -- however I think that actually passing the callback is
easier and makes the code much more readable.

DropDown.react.js
=================

The datepicker component has more or less the same structure as with the dropdown: It needs one parameter
for its current value (``props.value``) and another as the callback to the function when the date is
changed (once again this is required to have a reusable component):

.. code::

    var React = require('react');

    var DatePicker = React.createClass({
        render: function() {
            return(
                <input type='text' ref='date' value={this.props.value} onChange={this.handleChange} />
            );
        },
        componentDidMount: function() {
            $(React.findDOMNode(this)).datepicker({ dateFormat: 'yy-mm-dd' });
            $(React.findDOMNode(this)).on('change', this.handleChange);
        },
        componentWillUnmount: function() {

        },
        handleChange: function() {
            var date = React.findDOMNode(this.refs.date).value
            this.props.onChange(date);
        }
    });

    module.exports.DatePicker = DatePicker ;

Another thing we can see here is how can integrate jquery components with react: When
the component is mounted, we get its DOM component using ``React.findDomNode(this)`` and
convert it to a datepicker. We also set its change function to be the passed callback.

PagingPanel.react.js
====================

The paging panel is not actually a reusable component because it requires BookActions
(to handle next and previous page clicks) - so
it can't be used by Authors (if authors was a table that is). However, we can easily
change it to be reusable if we passed callbacks for next and previous page so that
the component including PagingPanel would call the correct action on each click. Having
a reusable PagingPangel is not needed for our application since only books have a table.

.. code::

    var React = require('react');
    var BookActions = require('../actions/BookActions').BookActions;

    var PagingPanel = React.createClass({
        render: function() {
            return(
                <div className="row">
                    {this.props.page==1?'':<button onClick={this.onPreviousPageClick}>&lt;</button>}
                    &nbsp; Page {this.props.page} of {this.getTotalPages()} &nbsp;
                    {this.props.page==this.getTotalPages()?'':<button onClick={this.onNextPageClick} >&gt;</button>}
                </div>
            );
        },
        onNextPageClick: function(e) {
            e.preventDefault();
            BookActions.change_page(this.props.page+1)
        },
        onPreviousPageClick: function(e) {
            e.preventDefault();
            BookActions.change_page(this.props.page-1)
        },
        getTotalPages: function() {
            return Math.ceil(this.props.total / this.props.page_size);
        }
    })

    module.exports.PagingPanel = PagingPanel;

The component is very simple, it needs three parameters:

- the current page (``props.page``)
- the page size (``props.page_size``)
- the total pages number (``props.total``)

and just displayd the current page along with buttons to go to the next or previous page (if these buttons should be visible of course).

SearchPanel.react.js
====================

The SearchPanel is another panel that could be reusable if we'd passed a callbeck instead of calling the ``BookActions.search``
action directly. The promise behavior has been explained in the previous posts and is needed to buffer the queries to the
server when a user types his search query.

.. code::

    var React = require('react');
    var BookActions = require('../actions/BookActions').BookActions;

    var SearchPanel = React.createClass({
        getInitialState: function() {
            return {
                search: this.props.query,
            }
        },
        componentWillReceiveProps: function(nextProps) {
          this.setState({
                search: nextProps.query
          });
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
            }.bind(this), 400);
        },
        onClearSearch: function() {
            this.setState({
                search: ''
            });
            BookActions.search('');
        }
    });

    module.exports.SearchPanel = SearchPanel;

As we can see, this panel is a little different than the previous ones because it actually handles its
own local state: When the component should get properties from its parent compoent, its state will
be updated to the ``query`` attribute - so the current value of the search query gets updated through
properties. However, when the value of the search input is changed, we see that the local state is
changed immediately but the ``BookActions.search`` (or the corresponding callback) gets called *only*
when the timeout has passed!

The above means that we can type whatever we want on the search input, but it at first it will be used
only locally to immediately update the value of the input and, only after the timeout has fired the
search action will be called. If we hadn't used the local state it would be much more difficult to have
this consistent behavior (we'd need to add two actions, one to handle the search query value change
and another to handle the timeout firing -- making everythimg much more complicated).

MessagePanel
============

The MessagePanel is really interesting because it is a reusable component that actually has its own action and store module! This
component can be reused in *different* applications that need to display message but *not* on the same application (because a single state
is kept for all messages). If we wanted to use a different MessagePanel for Books or Authors then we'd need to keep both in the
state *and* also it to the action to differentiate between messages for author and for book. Instead, by keeping a single Messages
state for both Books and Authors we have a much more simple version.

MessagePanel.react.js
~~~~~~~~~~~~~~~~~~~~~

The MessagePanel component has a local state which responds to changes on MessageStore. When the
state of MessageStore is changed the MessagePanel will be re-rendered with the new message.

.. code::

    var React = require('react');
    var MessageStore = require('../stores/MessageStore').MessageStore;

    var MessagePanel = React.createClass({
        getInitialState: function() {
            return {

            };
        },
        render: function() {
            return(
                <div className="row">
                    {this.state.message?<div className={this.state.message.color}>{this.state.message.text}</div>:""}
                </div>
            );
        },
        _onChange: function() {
            this.setState(MessageStore.getState());
        },
        componentWillUnmount: function() {
            MessageStore.removeChangeListener(this._onChange);
        },
        componentDidMount: function() {
            MessageStore.addChangeListener(this._onChange);
        }
    })

    module.exports.MessagePanel = MessagePanel;


MessageStore.js
~~~~~~~~~~~~~~~

The MessageStore has a (private) state containing a ``message`` that gets updated
only when the ccorresponding action is dispached. The store has a single state
for all messages - it doesn't care if the messages are for books or authors.

.. code::

    var $ = require('jquery');
    var EventEmitter = require('events').EventEmitter;
    var AppDispatcher = require('../dispatcher/AppDispatcher').AppDispatcher;
    var BookConstants = require('../constants/BookConstants')

    var _state = {
        message: {}
    };

    var MessageStore = $.extend({}, EventEmitter.prototype, {
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

    MessageStore.dispatchToken = AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case BookConstants.MESSAGE_ADD:
                _state.message = action.message;
                MessageStore.emitChange();
            break;
        }
        return true;
    });

    module.exports.MessageStore = MessageStore;

MessageActions
~~~~~~~~~~~~~~

Finally, there are two actions that are defined for the MessageStore: One for adding
an ok message and one for adding an error message - both of which have the same
message type (but pass a different color parameter).

.. code::

    var AppDispatcher = require('../dispatcher/AppDispatcher').AppDispatcher;
    var BookConstants = require('../constants/BookConstants')

    var MessageActions = {
        add_message_ok: function(msg) {
            AppDispatcher.dispatch({
                actionType: BookConstants.MESSAGE_ADD,
                message: {
                    color: 'green',
                    text: msg
                }
            });
        },
        add_message_error: function(msg) {
            AppDispatcher.dispatch({
                actionType: BookConstants.MESSAGE_ADD,
                message: {
                    color: 'green',
                    text: msg
                }
            });
        }
    };

    module.exports.MessageActions = MessageActions;

Non-reusable application components
-----------------------------------

I don't want to discuss the source code for all the non-reusable components since some of them
are more or less the same with the previous version and are easy to understand just by
checking the source code (BookTableRow and ButtonPanel). However, I'll
discuss the other, more complex components starting from the inside of the react-onion:

BookTable.react.js
==================

I want to display this component to discuss how sorting is implemented: Each column has a key which,
when passed to django-rest-framework will sort the results based on that key (the ``__`` does a
join so by ``author__last_name`` we mean that we want to sort by the last_name field of the author
of each book. Also, you can pass the key as it is to sort ascending or with a minus (-) in front
(for example ``-author__last_name``).

.. code::

    var React = require('react');
    var BookTableRow = require('./BookTableRow.react').BookTableRow;
    var BookActions = require('../actions/BookActions').BookActions;

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
                            <th><a href='#' onClick={this.onClick.bind(this, 'id')}>{this.showOrdering('id')} Id</a></th>
                            <th><a href='#' onClick={this.onClick.bind(this, 'title')}>{this.showOrdering('title')} Title</a></th>
                            <th><a href='#' onClick={this.onClick.bind(this, 'subcategory__name')}>{this.showOrdering('subcategory__name')} Category</a></th>
                            <th><a href='#' onClick={this.onClick.bind(this, 'publish_date')}>{this.showOrdering('publish_date')} Publish date</a></th>
                            <th><a href='#' onClick={this.onClick.bind(this, 'author__last_name')}>{this.showOrdering('author__last_name')} Author</a></th>
                            <th>Edit</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            );
        },
        onClick: function(v, e) {
            e.preventDefault();
            BookActions.sort_books(v);
        },
        showOrdering: function(v) {
            if (v==this.props.ordering) {
                return '+'
            } else if ('-'+v==this.props.ordering) {
                return '-'
            }
        }
    });

    module.exports.BookTable = BookTable ;


The only thing that needs explaining in this module is the line of the form

.. code::

    <th><a href='#' onClick={this.onClick.bind(this, 'id')}>{this.showOrdering('id')} Id</a></th>

that creates the title of each column and triggers ascending or descending sorting on this column by
clicking on it. So, we can see that we've create an onClick function that actually expects a value - the key
to that column. To allow passing that value, we use the bind method of the function object which will
create new a function that has this key as its first parameter. If we didn't want to use bind, we'd need to
creatre 5 different function (onIdClick, onTitleClick etc)! The most common usage of ``bind`` is to actually *bind*
a function to an object (that's what the first parameter to this function does)
so that calling this inside that function will refer to that object - here we leave the binding
of the function to the same object and only do the parameter passing.

Also, the showOrdering checks if the current ordering is the same as that column's key and displays
either a + (for ascending) or - (for descending) in front of the column title.

AuthorDialog.react.js
=====================

This is a handmade pop-up dialog that gets displayed when a new author is added (the + button is clicked)
using only css to center it on the screen when it is displayed.
We can see that it is either visible on invisible based on the ``showDialog`` input property which actually
is the only input this component requires. When it is visible and the ok or cancel button are pressed
the corresponding action will be dispatched (which will actually close this popup by setting the ``showDialog``
to false):

.. code::

    var React = require('react');
    var AuthorActions = require('../actions/AuthorActions').AuthorActions;

    var AuthorDialog = React.createClass({

        render: function() {
            if (!this.props.showDialog) {
                return (
                    <div />
                )
            } else {
                return(
                    <div className='modal-dialog' id="dialog-form"  >
                        <label htmlFor="first_name">First name:</label> <input type='text' ref='first_name' name='first_name' /> <br />
                        <label htmlFor="last_name">Last name:</label> <input type='text' ref='last_name' name='last_name' /> <br />
                        <button onClick={this.onOk}>Ok</button>
                        <button onClick={this.onCancel} >Cancel</button>
                    </div>

                );
            }
        },
        onCancel: function(e) {
            e.preventDefault();
            AuthorActions.hide_add_author();
        },
        onOk: function(e) {
            e.preventDefault();
            first_name = React.findDOMNode(this.refs.first_name).value;
            last_name = React.findDOMNode(this.refs.last_name).value;
            AuthorActions.add_author_ok({
                first_name: first_name,
                last_name: last_name
            });
        }
    });

    module.exports.AuthorDialog = AuthorDialog ;


AuthorPanel.react.js
====================

The AuthorPanel displays the author select DropDown along with the + (add author) and
- (delete author) buttons. It also contains the AuthorDialog which will be displayed
or not depending on the value of the ``showDialog`` property.

.. code::

    var React = require('react');
    var DropDown = require('./DropDown.react').DropDown;
    var AuthorDialog = require('./AuthorDialog.react').AuthorDialog;
    var AuthorActions = require('../actions/AuthorActions').AuthorActions;

    var AuthorPanel = React.createClass({
        getInitialState: function() {
            return {};
        },
        render: function() {
            var authorExists = false ;
            if(this.props.authors) {
                var ids = this.props.authors.map(function(x) {
                    return x.id*1;
                });

                if(ids.indexOf(1*this.props.author)>=0 ) {
                    authorExists = true;
                }
            }

            return(
                <div className='one-half column'>
                    <AuthorDialog showDialog={this.props.showDialog} />
                    <label forHtml='date'>Author</label>
                    <DropDown options={this.props.authors} dropDownValueChanged={this.props.onAuthorChanged} value={authorExists?this.props.author:''} />
                    <button onClick={this.addAuthor} >+</button>
                    {authorExists?<button onClick={this.deleteAuthor}>-</button>:""}
                </div>
            );
        },
        addAuthor: function(e) {
            e.preventDefault();
            console.log("ADD AUTHOR");
            AuthorActions.show_add_author();
        },
        deleteAuthor: function(e) {
            e.preventDefault();
            AuthorActions.delete_author(this.props.author);
            console.log("DELETE AUTHOR");
            console.log(this.props.author);
        },
    });

    module.exports.AuthorPanel = AuthorPanel;

As we can see, there are three properties that are passed to this component:

- ``props.author``: The currently selected author
- ``props.authors``: The list of all authors
- ``props.onAuthorChanged``: A callback that is called when the author is changed. Here, we could have used an action (just like for add/delete author) instead of a callback, however its not actually required. When the author is changed, it means that the currently edited book's author is changed. So we could propagate the change to the parent (form) component that handles the book change along with the other changes (i.e title, publish date etc).


StatPanel.react.js
==================

The StatPanel is an interesting, read-only component that displays the number of
authors and books. This component requests updates from both the ``BookStore`` and
``AuthorStore`` - when their state is updated the component will be re-rendered
with the number of books and authors:

.. code::

    var React = require('react');
    var BookStore = require('../stores/BookStore').BookStore;
    var AuthorStore = require('../stores/AuthorStore').AuthorStore;

    var StatPanel = React.createClass({
        getInitialState: function() {
            return {};
        },
        render: function() {
            var book_len = '-';
            var author_len = '-';
            if(this.state.books) {
                book_len = this.state.books.length
            }
            if(this.state.authors) {
                author_len = this.state.authors.length
            }
            return(
                <div className="row">
                    <div className="one-half column">
                        Books number: {book_len}
                    </div>
                    <div className="one-half column">
                        Authors number: {author_len}
                    </div>
                    <br />
                </div>
            );
        },
        _onBookChange: function() {
            this.setState({
                books:BookStore.getState().books
            });
        },
        _onAuthorChange: function() {
            this.setState({
                authors: AuthorStore.getState().authors
            });
        },
        componentWillUnmount: function() {
            AuthorStore.removeChangeListener(this._onAuthorChange);
            BookStore.removeChangeListener(this._onBookChange);
        },
        componentDidMount: function() {
            AuthorStore.addChangeListener(this._onAuthorChange);
            BookStore.addChangeListener(this._onBookChange);
        }
    });

    module.exports.StatPanel = StatPanel ;

We've added different change listeners in case we wanted to do
some more computations for book or author change (instead of just
getting their books / authors property). Of course the same behavior
could be achieved with just a single change listener that would
get both the books and authors.

BookForm.react.js
=================

The BookForm is one of the most complex panels of this application (along with BookPanel) because
it actually contains a bunch of other panels and has some callbacks for them to use.

We can see that, as explained before, when the current book form values are changed (through callbacks) the change_book action will be called.

.. code::

    var React = require('react');
    var BookActions = require('../actions/BookActions').BookActions;
    var DropDown = require('./DropDown.react.js').DropDown;
    var StatPanel = require('./StatPanel.react.js').StatPanel;
    var MessagePanel = require('./MessagePanel.react.js').MessagePanel;
    var DatePicker = require('./DatePicker.react.js').DatePicker;
    var ButtonPanel = require('./ButtonPanel.react.js').ButtonPanel;
    var AuthorPanel = require('./AuthorPanel.react.js').AuthorPanel;
    var CategoryStore = require('../stores/CategoryStore').CategoryStore;
    var AuthorStore = require('../stores/AuthorStore').AuthorStore;
    var loadCategories = require('../stores/CategoryStore').loadCategories;
    var loadAuthors = require('../stores/AuthorStore').loadAuthors;

    var BookForm = React.createClass({
        getInitialState: function() {
            return {};
        },
        render: function() {
            return(
                <form onSubmit={this.onSubmit}>
                    <div className='row'>
                        <div className='one-half column'>
                            <label forHtml='title'>Title</label>
                            <input ref='title' name='title' type='text' value={this.props.book.title} onChange={this.onTitleChange} />
                        </div>
                        <div className='one-half column'>
                            <label forHtml='date'>Publish date</label>
                            <DatePicker ref='date' onChange={this.onDateChange} value={this.props.book.publish_date} />
                        </div>
                    </div>
                    <div className='row'>
                        <div className='one-half column'>
                            <label forHtml='category'>Category</label>
                            <DropDown options={this.state.categories} dropDownValueChanged={this.onCategoryChanged} value={this.props.book.category} />
                            <DropDown options={this.state.subcategories} dropDownValueChanged={this.onSubCategoryChanged} value={this.props.book.subcategory} />
                        </div>
                        <AuthorPanel authors={this.state.authors} author={this.props.book.author} onAuthorChanged={this.onAuthorChanged} showDialog={this.state.showDialog} />
                    </div>

                    <ButtonPanel book={this.props.book}  />
                    <MessagePanel />
                    <StatPanel  />
                </form>
            );
        },
        onSubmit: function(e) {
            e.preventDefault();
            BookActions.save(this.props.book)
        },
        onTitleChange: function() {
            this.props.book.title = React.findDOMNode(this.refs.title).value;
            BookActions.change_book(this.props.book);
        },
        onDateChange: function(date) {
            this.props.book.publish_date = date;
            BookActions.change_book(this.props.book);
        },
        onCategoryChanged: function(cat) {
            this.props.book.category = cat;
            this.props.book.subcategory = '';
            BookActions.change_book(this.props.book);
        },
        onSubCategoryChanged: function(cat) {
            this.props.book.subcategory = cat;
            BookActions.change_book(this.props.book);
        },
        onAuthorChanged: function(author) {
            this.props.book.author = author;
            BookActions.change_book(this.props.book);
        },
        _onChangeCategories: function() {
            this.setState(CategoryStore.getState());
        },
        _onChangeAuthors: function() {
            this.setState(AuthorStore.getState());
        },
        componentWillUnmount: function() {
            CategoryStore.removeChangeListener(this._onChangeCategories);
            AuthorStore.removeChangeListener(this._onChangeAuthors);
        },
        componentDidMount: function() {
            CategoryStore.addChangeListener(this._onChangeCategories);
            AuthorStore.addChangeListener(this._onChangeAuthors);
            loadCategories();
            loadAuthors();
        }
    });

    module.exports.BookForm = BookForm;

The above component listens for updates on both Category and Author store to update
when the authors (when an author is added or deleted) and the categories are changed (for example to implement the cascading dropdown
functionality), so the list of authors and the list of categories and subcategoreis are all stored in
the local state. The book that is edited is just passed as a property - actually, this is the only
property that this component needs to work.

BookPanel.react.js
==================

Finally, BookPanel is the last component we'll talk about. This is the central component
of the application - however we'll see that it is not very complex (since most user interaction
is performed in other components). This component just listens on changes in the BookStore state
and depending on the parameters either displays the "Loading" message or the table of books
(depending on the state of ajax calls that load the books). The other parameters like the
list of books, the ordering of the books etc are passed to the child components.

.. code::


    var React = require('react');
    var BookStore = require('../stores/BookStore').BookStore;
    var BookActions = require('../actions/BookActions').BookActions;
    var SearchPanel = require('./SearchPanel.react').SearchPanel;
    var BookTable = require('./BookTable.react').BookTable;
    var PagingPanel = require('./PagingPanel.react').PagingPanel;
    var BookForm = require('./BookForm.react').BookForm;

    var reloadBooks = require('../stores/BookStore').reloadBooks;

    var BookPanel = React.createClass({
        getInitialState: function() {
            return BookStore.getState();
        },
        render: function() {
            return(
                <div className="row">
                    <div className="one-half column">
                        {
                            this.state.loading?
                            <div class='loading' >Loading...</div>:
                            <div>
                                <SearchPanel query={this.state.query} ></SearchPanel>
                                <BookTable books={this.state.books} ordering={this.state.ordering} />
                                <PagingPanel page_size='5' total={this.state.total} page={this.state.page} />
                            </div>
                        }
                    </div>
                    <div className="one-half column">
                        <BookForm
                            book={this.state.editingBook}
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
            reloadBooks();
        }
    });

    module.exports.BookPanel = BookPanel ;


The Actions
-----------

All actions are rather simple components without other dependencies as we've already discussed. They
just define "actions" (which are simple functions) that create the correct parameter object type and pass it
to the dispatcher. The only attribute that is required for this object is the ``actionType`` that
should get a value from the constants. I won't go into any more detail about the actions -- please check
the source code and all your questions will be resolved.

The Stores
----------

First of all, all stores are defined through the following code that is already discussed in the previous
part:

.. code::

    var MessageStore = $.extend({}, EventEmitter.prototype, {
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

When the state of a store is changed its ``emitChange`` function will be called (I mean
called manually from the code that actually changes the state and knows that it has
actually been changed - nothing will be called automatically). When ``emitChange`` is called,
all the components that listen for changes for this component (that have called ``addChangeListener``
of the store with a callback)
will be notified (their callback will be called) and will use
``getState`` of the store to get its current state - after that, these components will set their own state
to re-render and display the changes to the store.

Let's now discuss the four stores defined -- I will include only the parts of each file that are
actually interesting, for everything else *use the source Luke*!


MessageStore.js
===============

A very simple store that goes together with MessagePanel and MessageActions. It just keeps a state with
the current message object and just changes this message when the MESSAGE_ADD message
type is dispatched. After changing the message, the listeners (only one in this case) will be notified to
update the displayed message:

.. code::

    var _state = {
        message: {}
    };

    MessageStore.dispatchToken = AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case BookConstants.MESSAGE_ADD:
                _state.message = action.message;
                MessageStore.emitChange();
            break;
        }
        return true;
    });


AuthorStore.js
==============
Here we see that the local state has an array of the authors and a ``showDialog`` flag that
controls the state of the add author popup. For the ``AUTHOR_ADD`` and ``HIDE_ADD_AUTHOR``
cases of the dispatch we just change the state of this flag and emit the change; the ``BookForm``
listens for changes to the ``AuthorStore`` and will pass the ``showDialog`` to the ``AuthorPanel``
as a property which in turn will pass it to ``AuthorDialog`` and it will display the panel (or not)
depending on the value of that flag. This flag will also take a false value when the add author
ajax call returns. 

The ``showDialog`` flag is not related to the actual data but is UI-related. This
is something that we should keep in mind when creating stores: Stores don't only contain the actual
data (like models in an MVC application) but they should also contain UI (controller/view in an MVC 
architecture) related information since that is *also* part of the state!

We can see that the ajax calls just issue the corresponding HTTP method to the ``authors_url`` and
when they return the ``add_message_ok`` or ``add_message_error`` methods of
``MessageActions`` will be called. These calls are in a different call stack so everything will work fine
(please remember the discussion about dispatches in different call stacks before).

Finally, on the success of ``_load_authors`` the map array method is called to transform the returned data
as we want it:

.. code::

    var $ = require('jquery');

    var _state = {
        authors: [],
        showDialog: false
    }

    var _load_authors = function() {
        $.ajax({
            url: _props.authors_url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                _state.authors = data.map(function(a){
                    return {
                        id: a.id,
                        name: a.last_name+' '+a.first_name
                    }
                });
                AuthorStore.emitChange();
            },
            error: function(xhr, status, err) {
                MessageActions.add_message_error(err.toString());
            }
        });
    };

    var _deleteAuthor = function(authorId) {
        $.ajax({
            url: _props.authors_url+authorId,
            method: 'DELETE',
            cache: false,
            success: function(data) {
                _load_authors();
                MessageActions.add_message_ok("Author delete ok");
                AuthorActions.delete_author_ok();
            },
            error: function(xhr, status, err) {
                MessageActions.add_message_error(err.toString());
            }
        });
    };

    var _addAuthor = function(author) {
        $.ajax({
            url: _props.authors_url,
            dataType: 'json',
            method: 'POST',
            data:author,
            cache: false,
            success: function(data) {
                MessageActions.add_message_ok("Author add  ok");
                _state.showDialog = false;
                _load_authors();
            },
            error: function(xhr, status, err) {
                MessageActions.add_message_error(err.toString());
            }
        });

    };

    AuthorStore.dispatchToken = AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case BookConstants.SHOW_ADD_AUTHOR:
                _state.showDialog = true;
                AuthorStore.emitChange();
            break;
            case BookConstants.HIDE_ADD_AUTHOR:
                _state.showDialog = false;
                AuthorStore.emitChange();
            break;
            case BookConstants.AUTHOR_ADD:
                _addAuthor(action.author);
            break;
            case BookConstants.AUTHOR_DELETE:
                _deleteAuthor(action.authorId);
            break;
        }
        return true;
    });


CategoryStore.js
================
The CategoryStore has an interesting functionality concerning the load_subcategory
function. This function is called whenever a book is changed (so its category form field
may be changed and the subcategories may be reloaded based on this category) or is edited 
(so the category is that of the new book and once again the subcategories may need to because
rerendered). It is important that we *actually* pass the current category to the book to the
action. If for example we wanted to retrieve that from the state of the BookStore then we'd
need to use the ``waitFor`` functionality of the dispatcher so that the category of the
current book would be changed first then the load_category (that would read that value to
read the subcategoreis) would be called after that.

Also, another thing to notice here is that there's a simple subcat_cache that for each category
contains the subcategories of that category so that we won't do repeated ajax calls to reload
the subcategories each time the category is changed.

.. code::

    var _state = {
        categories: [],
        subcategories: []
    }

    var _current_cat = ''
    var _subcat_cache = []

    var _load_categories = function() {
        $.ajax({
            url: _props.categories_url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                _state.categories = data;
                CategoryStore.emitChange();
            },
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }
        });
    };

    var _load_subcategories = function(cat) {
        
        if(!cat) {
            _state.subcategories = [];
            CategoryStore.emitChange();
            return ;
        }
        if(_subcat_cache[cat]) {
            _state.subcategories = _subcat_cache[cat] ;
            CategoryStore.emitChange();
        }
        $.ajax({
            url: _props.subcategories_url+'?category='+cat,
            dataType: 'json',
            cache: false,
            success: function(data) {
                _state.subcategories = data;
                _subcat_cache[cat] = data;
                CategoryStore.emitChange();
            },
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }
        });
    };

    CategoryStore.dispatchToken = AppDispatcher.register(function(action) {
        switch(action.actionType) {
            case BookConstants.BOOK_EDIT:
            case BookConstants.BOOK_CHANGE:
                _load_subcategories(action.book.category);
            break;
            case BookConstants.BOOK_EDIT_CANCEL:
                _state.subcategories = [];
                CategoryStore.emitChange();
            break;
        }
        return true;
    });

BookStore.js
============

Here, beyond the book-related functionality we have also implemented the
URL updating. The getUrlParameter that returns the value of a URL parameter has been taken from 
http://stackoverflow.com/questions/19491336/get-url-parameter-jquery. Depending on the url parameters, we set some initial properties of
the local state and, on the other hand, when the search query, ordering or page are changed,
the ``_update_href`` function is called to update the url parameters. This is not really related
to the flux architecture beyond the initialization of state.

Another thing to notice is that the when the ``_search`` is executed whenever there's
a change in the list of books (query is updated, sorting is changed, page is changed or
when an author is deleted since the books that have that author should now display an
empty field). The setTimeout in the _search ajax return is to simulate a 400ms delay (in order for the "Loading" text to 
be visible).

.. code::

    function getUrlParameter(sParam) {
        var sPageURL = $(location).attr('hash');
        sPageURL = sPageURL.substr(1)
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++)  {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == sParam)  {
                return sParameterName[1];
            }
        }
    }

    var _page_init = 1*getUrlParameter('page');
    if(!_page_init) _page_init = 1 ;
    var _ordering_init = getUrlParameter('ordering');
    if(!_ordering_init) _ordering_init = '' ;
    var _query_init = getUrlParameter('query');
    if(!_query_init) _query_init = ''

    var _state = {
        loading: false,
        books: [],
        message:{},
        page: _page_init,
        total: 0,
        editingBook: {},
        query: _query_init,
        ordering: _ordering_init
    }


    var _search = function() {
        _state.loading = true;
        BookStore.emitChange();
        
        $.ajax({
            url: _props.url+'?search='+_state.query+"&ordering="+_state.ordering+"&page="+_state.page,
            dataType: 'json',
            cache: false,
            success: function(data) {
                // Simulate a small delay in server response
                setTimeout(function() {
                    _state.books = data.results;
                    _state.total = data.count;
                    _state.loading = false;
                    BookStore.emitChange();
                }, 400);
            },
            error: function(xhr, status, err) {
                _state.loading = false;
                MessageActions.add_message_error(err.toString());
                BookStore.emitChange();
            }
        });
    };

    var _reloadBooks = function() {
        _search('');
    };


    var _clearEditingBook = function() {
        _state.editingBook = {};
    };

    var _editBook = function(book) {
        _state.editingBook = book;
        BookStore.emitChange();
    };

    var _cancelEditBook = function() {
        _clearEditingBook();
        BookStore.emitChange();
    };

    var _update_href = function() {
        var hash = 'page='+_state.page;
        hash += '&ordering='+_state.ordering;
        hash += '&query='+_state.query;
        $(location).attr('hash', hash);
    }

    BookStore.dispatchToken = AppDispatcher.register(function(action) {
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
                _state.query = action.query
                _state.page = 1;
                _update_href();
                _search();
            break;
            case BookConstants.BOOK_DELETE:
                _deleteBook(action.bookId);
            break;
            case BookConstants.BOOK_CHANGE:
                _state.editingBook = action.book;
                BookStore.emitChange();
            break;
            case BookConstants.BOOK_PAGE:
                _state.page = action.page;
                _update_href();
                _search();
            break;
            case BookConstants.AUTHOR_DELETE_OK:
                _search();
            break;
            case BookConstants.BOOK_SORT:
                _state.page = 1;
                if(_state.ordering == action.field) {
                    _state.ordering = '-'+_state.ordering
                } else {
                    _state.ordering = action.field;
                }
                _update_href();
                _search();
            break;
        }
        return true;
    });


Conclusion
----------

The application presented here has a number of techniques that will help
you when you actually try to create a more complex react flux application.
I hope that in the whole three part series I've thoroughly explained the 
flux architecture and how each
part of (actions, stores, components) it works. Also, I tried to cover 
almost anything that somebody creating react/flux application
will need to use -- if you feel that something is not covered and
could be integrated to the authors/book application I'd be happy
to research and implement it!



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