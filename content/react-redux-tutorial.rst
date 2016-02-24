A comprehensive react-redux tutorial
####################################

:date: 2016-02-19 15:20
:tags: javascript, react, redux, react-redux, django, redux-thunk, redux-form, react-router, react-router-redux, react-notification, history es6, babel, babelify, browserify, watchify, uglify, boilerplate
:category: javascript
:slug: react-redux-tutorial
:author: Serafeim Papastefanos
:summary: A comprehensive tutorial for using react with redux

.. contents::

Introduction
------------

Continuing the series of React-related articles, we'll try to make a comprehensive
introduction to the redux_ framework and its integrations with React, using the
react-redux_ library. Redux can be used as an alternative to Flux 
(which we discussed in `next part, <{filename}react-flux-tutorial.rst>`_)
to orchestrate the message passing between ui/components/data. 

This introduction will also serve as an opinionated (my opinion) boilerplate
project for creating react-redux Single Page Applications. I have used Django
as the back end however you could use any server-side framework you like,
the only thing Django does is offering a bunch of REST APIs from django-rest-framework.
I have also used ``browserify`` to pack the client-side code -- I prefer it
from webpack as I find it much easier, clear and less-magical, and, since it fills all my
needs I don't see any reason to take the webpack pill.

All client side code is written in ES6 javascript using the latest trends -- I will
try to explain anything I feel that is not very clear.

Before continuing, I have to mention that although I will provide an introduction to redux, 
I will concentrate on the correct integration between redux, react-redux and
React in a complex, production level application. So, before reading the rest of
this article please make sure that you've read the introduction and basics sections
of `redux documentation`_ and watch the `getting started with redux`_ from the 
creator of redux -- I can't recommend the videos enough, they are really great!

Introduction to redux
---------------------

Redux is a really great framework. It is simpler than the original Flux and more opinionated.
It has three basic concepts:

- One (and only one) **state**: It is an object that keeps the *global* state of your application. Everything has to be in that object, both data and ui.
- A bunch of **actions**: These are objects that are created/dispatched when something happens (ui interaction, server response etc) with a mandatory property (their type) and a number of optional properties that define the data that accompanies each action.
- A bunch of **action creators**: These are very simple functions that create action objects. Usually, there are as many action creators as actions (unless you use redux-thunk).
- One (and only one) **reducer**: It is a function that retrieves the current state and an action and creates the resulting state. One very important thing to keep in mind is that the reducer *must not* mutate the state but return *a new object when something changes*.
- One (and only one) **store**: It is an object that is created by redux and is used as a glue between the state, the reducer and the components

The general idea/flow is:

- Something (let's call it event) happens (i.e a user clicks a button, a timeout is fired, an ajax request responds)
- An action describing that event is created by its the corresponding action creator and dispatched (i.e passed to the reducer along with the current state) through the store
- The reducer is called with the current state object and the action as parameters
- The reducer checks the type of the action and, depending on the action type and any other properties this action has, creates a new state object
- The store applies the new state to all components

One thing we can see from the above is that redux is not react-only (although its general architecture fits perfectly with react) but
could be also used with different view frameworks, or even with *no view framework*!

A simple example
================

I've implemented a very simple redux example @ jsfiddle that increases and decreases
a number using two buttons to support the above: 

.. jsfiddle:: 8aba3sp6

Its html is: 

.. code::

  <div id='state_container'>0</div>
  <button onclick='increase()'>+</button>
  <button onclick='decrease()'>-</button>

while its javascript (es6) code is:

.. code:: 

  let reducer = (state=0, action) => {
    switch (action.type) {
      case 'INCREASE': return state+1
      case 'DECREASE': return state-1
      default: return state
    }
  }
  let store = Redux.createStore(reducer)
  let unsubscribe = store.subscribe(() => 
    document.getElementById('state_container').innerHTML = store.getState()
  )
  window.increase = e => store.dispatch({
    type: 'INCREASE'
  })

  window.decrease = e => store.dispatch({
    type: 'DECREASE'
  })

The HTML just displays a div which keeps the current number value
and two buttons that call the increase and decrease functions.

Now, for the javascript, we create a reducer function that
gets the previous state value (which initially is the number 0) and the
action that is dispatched. It checks if the action type is 'INCREASE'
or 'DECREASE' and correspondigly increases or decreases the state,
which is just the number.

We then create a store which gets the reducer as its only parameter
and call its subscribe method passing a callback. This callback will be
called whenever the state is changed - in our case, we'll just update
the div with the current number from the state. Finally, the increase
and decrease methods will just dispatch the corresponding action.

Please notice that in the above example I didn't use action creators for
simplicity. For completeness, the action creator for increase would be something like 

.. code::
  
  const increaseCreator = () => {
    type: 'INCREASE'
  }
  
i.e it would just return an ``INCREASE`` action and ``window.increase``
would be ``window.increase = e => store.dispatch(increaseCreator())``. Notice that
the ``increaseCreator`` *is* called so that ``dispatch`` will receive the resulting
action object as a parameter.

The flow of the data when the increase button is clicked is the following:

- ``button.onClick``
- ``increase()``
- ``increaseCreator()`` (if we used action creators - this a param to ``dispatch`` so it will be called first)
- ``store.dispatch({type: 'INCREASE' })``
- ``reducer(current_state, {type: 'INCREASE'})``
- ``callback()``
- value is updated

Having one and only one store/state makes the flow of the data crystal and
resolves some of the dillemas I had when using the original Flux architecture!
Some people may argue that although a single reducer function is nice for
the above simple demo, having a huge (spaghetti-like) switch statement in
your reducer is not a very good practice - thankfully redux has a bunch
of tools that will presented later and greatly help on this (seperating the
reducing logic, using different modules etc).

Interlude: So what's a reducer?
===============================

I'd like to talk a bit about the "reducer", mainly for people not familiar with
functional programming (although people writing Javascript *should* be familiar
with functional programming since Javascript has functional features). 

In any case, one basic concept of functional programming is the concept of
"map-reduce". Mapping means calling a function (let's call it mapper)
for all elements of a list and creating a new list with the output of each 
individual call. So, a mapper gets only one parameter, the current value of
the list. For example the "double" mapper, defined like
``let double = x => x*2`` would "map" the list ``[1,2,3]`` to ``[2,4,6]``.

Reducing means calling a function (let's call it *reducer*) for all elements
of a list and creating a single value that accumulates the result of each 
individual call. This can be done because the reducer gets *two* parameters,
the accumulated value of the list until now and the current value of the list.
Also, when doing a reduce we need to define a starting value for the accumulator.
For example, the "sum" reducer, defined like ``let sum = (s=0, x) => s+x``, 
(which as an initial value of 0), would "reduce" the list ``[1,2,3]`` to ``6`` by calling:

.. code::

  tmp1 = sum(0, 1); // tmp1 = 1
  tmp2 = sum(tmp1, 2); // tmp2 = 3
  result = sum(tmp2, 3); // result = 6

So, a redux reducer is *actually* a (rather complex) functional reducer, getting the current
state (as the accumulated value) and each individual action as the value and
returning the new state which is the result of applying this action to the state!

Three extra things to make sure about your redux reducers is that 

- they should have an initial value (with the initial state of the application) 
- they must not not mutate (change) the state object but instead create and return a new one
- always return a valid state as a result

What about react-redux?
=======================

React-redux is a rather simple framework that offers two helpful utilities for integrating
redux with React:

- A ``connect`` function that "connects" React components to the redux store. This function (among others) retrieves a callback parameter that defines properties that will be passed to that component and each one will be (magically) mapped to state properties.
- A ``Provider`` component. This is a parent component that can be used to (magically) pass the store properties to its children components.

Please notice that nothing actually magical happens when the store properties are passed to the children 
components through ``connect`` and ``Provider``, this is accomplished through the `react context`_ feature
that allows you to "pass data through the component tree without having to pass the props down manually 
at every level".

This will be made more clear with another jsfiddle that will convert the previous example to React and
react-redux:

.. jsfiddle:: 8aba3sp6/2

The html is just ``<div id='container'></div>`` while the es6/jsx code is:

.. code::

    let reducer = (state=0, action) => {
      switch (action.type) {
        case 'INCREASE': return state+1
        case 'DECREASE': return state-1
        default: return state
      }
    }

    let store = Redux.createStore(reducer)

    class RootComponent extends React.Component {
      render() {
        let {number, increase, decrease} = this.props
        return <div>
          <div>{number}</div>
          <button onClick={e=>increase()}>+</button>
          <button onClick={e=>decrease()}> - </button>
        </div>
      }
    }

    let mapStateToProps = state => ({
      number: state
    })

    let mapDispatchToProps = dispatch => ({
      increase: () => dispatch({type: 'INCREASE'}),
      decrease: () => dispatch({type: 'DECREASE'})
    })

    const ConnectedRootComponent = ReactRedux.connect(
        mapStateToProps, mapDispatchToProps
    )(RootComponent)

    ReactDOM.render(
      <ReactRedux.Provider store={store}>
        <ConnectedRootComponent />
      </ReactRedux.Provider>,
      document.getElementById('container')
    )


As we can see, the reducer and store are the same as the non-react version. What is new is 
that I've added a React ``RootComponent`` that has two properties, one named ``number``
and one named ``dispatch`` that can be used to dispatch an action through the store. But how this
component retrieves these properties?

Using react-redux's ``connect`` function we create a new component, ``ConnnectedRootComponent`` 
which is a new component with the redux-enabled functionality. The ``connect()`` function takes
a bunch of optional arguments. I won't go into much detail since its a little complex (the `react-redux documentation`_
is clear enough), however in our example we have defined two objects named ``mapStateToProps`` and ``mapDispatchToProps``
which are passed to ``connect``. 

The ``mapStateToProps`` is a function that will be called whenever the store's state 
changes and should return an object whose attributes will be passed to the connected component. In our example,
an object with a number attribute having the current state (which don't forget that is just a number) as its value - 
that's why we can extract the ``number`` attribute from ``this.props`` when rendering. 

The ``mapDispatchToProps`` as we use it, once again returns an object whose attributes will be passed to the connected component.
The difference between this object and the one returned from ``mapStateToProps`` is that the ``mapDispatchToProps`` attributes
call actions (using the provided dispatch) while the ``mapStateToProps`` are state values. 

Now, in order for
the ``ConnectedRootComponent`` to *actually* have these properties that we passed through connect, it must 
be enclosed in a ``<Provider>`` parent component. Notice
that this is recursive so if we had something

.. code::

  <Provider store={store}>
    <Component1>
      <Component2>
        <ConnectedComponent>
        </ConnectedComponent>
      </Component2>
    </Component1>
  </Provider>

the ``<ConnectedComponent>`` would still get the props (dispatch + state slice) we mentioned above.

Of course, in our example, we could avoid using react-redux altogether, by passing the store directly
to ``<RootComponent>`` and subscibing to the store changes from the ``RootComponent``'s ``componentWillMount`` method, 
however the added-value of react-redux is that using ``connect`` and ``Provider`` we could pass dispatch and
state slices deep inside our component hierarchy without the need to explicitly pass the store
to each individual component and also that react-redux will make optimizations so that the
each connected component will be re-rendered only when needed (depending on the state slice it uses)
and not for every state change. Please be warned that this does not mean that you should connect everything
so that everything will have access to the global state and be able to dispatch actions. You should be very
careful to connect only the components that really need to be connected (redux calls them container components) 
and use ``mapStateToProps`` to  and pass dispatch and state as
properties to their children (which are called presentational components). Also, each connected component should receive only 
the part of the global state it
needs and not everything (so that each particular component will update only when needed and not for
every state update). The above is absolutely necessary if you want to crate re-usable (DRY) and
easily testable components. I'll discuss this a little more when
describing the sample project. 

Finally, notice how easy it is to create reusable container components using ``mapStateToProps`` and ``mapDispatchToProps``:
Both the way the component gets its state and calls its actions are defined through these two objects so you can create
as many connected objects as you want by passing different ``mapStateToProps`` and ``mapDispatchToProps``. 


Our project
-----------

After this rather lengthy introduction to redux and react-redux we may move on to our
project. First of all, let's see an example of what we'll actually build here:

.. image:: /images/ajax_fixed_data_tables.gif
  :alt: Our project
  :width: 600 px


Other libraries used
====================

React (and redux) have a big ecosystem of great libraries. Some of these have been used
for this project and will also be discussed:
  
- redux-thunk_: This is a nice add-on for redux that generalizes action creators.
- redux-form_: A better way to use forms with react and redux. Always use it if you have non-trivial forms.
- react-router_: A library to create routes for single page applications with React
- react-router-redux_ (ex redux-simple-router): This library will help integrating react-router with redux
- history_: This is used bt react-router to crete the page history (so that back forward etc work)
- react-notification_: A simple react component to display notifications

The triplet react-router, react-router-redux and history needs to be used for projects that 
enable client side routing. The redux-form is really useful if you have non-trivial forms
in your projects - you may skip it if you don't use forms or for example you use a form for 
searching/filtering with a single input. react-notification just displays notifications,
you can easily exchange it with other similar components or create your own. 

redux-thunk?
============

Now, about redux-thunk. I won't go into much detail here, you can read more in this `great SO answer`_,
however I'd like to point out here that **everything that can be done with redux-thunk
can also be done without it**.

A thunk allows you to create action creators that don't only return 
action objects but are more general, something like this: 

.. code::

  const thunkAction = () => {
    return (dispatch, getState) => {
      // here you may 
      // dispatch other actions (more than one) using the provided dispatch() parameter
      // or
      // check the current state using the getState() parameter and do conditional dispatches
      // or 
      // call functions asynchronously so that these will use the provided 
      // dispatch function when they return
    }
  }
  
Let's say that we wanted to implement an asynchronous, ajax call. 
If we don't want to use redux thunk,
then we need to create a normal function that gets dispatch as an argument, something
like this:

.. code::

  import {showLoadingAction, hideLoadingAction, showDataAction } from './actions'

  const getData = (dispatch) => {
    dispatch(showLoadingAction())
    $.get(data_url, data => {
        dispatch(hideLoadingAction())
        dispatch(showDataAction(data))
    })
  }

The main problem with this approach is that the getData functions *is not*
a real action creator (like ``showLoadingAction``, ``hideLoadingAction`` and ``showDataAction``)
since it actually returns nothing so you'll need to remember to call it directly
and pass it dispatch *instead of* passing its return value to dispatch!

If however we used thunk, then we'd have something like this:

.. code::

  const getDataThunk = () => {
    return (dispatch, getState) => {
      dispatch(showLoadingAction())
      $.get(data_url, data => {
          dispatch(hideLoadingAction())
          dispatch(showDataAction(data))
      })
    }
  }
  
Now, this can be used like a normal action (i.e it can be called using ``dispatch(getDataThunk())``).
That's more or less the main advantage of redux-thunk: You are able to create thunk action creators that 
can be called like normal can do more complex things than just returning action objects. I have to repeat
again that everything that you be done with thunk action creators, can also be done with normal functions
that get ``dispatch`` as a paremeter - the advantage of thunk action creators is that you don't need to
remember if an action creator needs to be called through ``disaptch(actionCreator())`` 
or ``actionCreator(dispatch)``.
  
In this tutorial you'll see heavy use of redux-thunk. This is just my personal preference - you may
use it less or not at all (however, if you've configured your project to use redux-thunk then I propose
to go all the way and use it all the time for those more complex action creators).

Explaining the application
--------------------------

In the following paragraphs we'll see together the structure and source code of
this application. I'll try to go into as much detail as possible in order to solve
any questions you may have (I know I had many when I tried setting up everything for
the first time). I'll skip imports and non-interesting ccomponents - after all the
complete source code can be found @ https://github.com/spapas/react-tutorial/. 
We'll use a top down approach, starting from the main component where the routes
are defined and the application is mounted to the DOM:

main.js
=======

This module is used as an entry point for browserify (i.e we call browserify with
``browserify main.js -o bundle.js`` ) and uses components defined elsewhere to
create he basic structure of our application. Let's take a look at the important
part of it:
 
.. code::

    const About = () => {
        return <div>
            <h2>About</h2>
            <Link to="/">Home</Link>
        </div>
    }

    render((
        <Provider store={store}>
            <Router history={history}>
                <Route path="/" component={App}>
                    <IndexRoute component={BookPanel}/>
                    <Route path="/book_create/" component={BookForm} />
                    <Route path="/book_update/:id" component={BookForm} />
                    
                    <Route path="/authors/" component={AuthorPanel} />
                    <Route path="/author_create/" component={AuthorForm} />
                    <Route path="/author_update/:id" component={AuthorForm} />
                    
                    <Route path="/about" component={About}/>
                    <Route path="*" component={NoMatch}/>
                </Route>
            </Router>
        </Provider>
      ), document.getElementById('content')
    )

We can see the well-known ``render`` function from ReactDOM that gets a component
and a DOM element to mount it to. The domponent we provide to render is the ``Provider``
from react-redux we talked about before in order to enable all children components
to use ``connect`` to have access to the store properties and dispatch. This is the usual
approact with react-redux: The outer component should be the ``Provider``.

The ``Provider`` component gets one parameter which is the store that redux will use. We 
have initialized our store in a different module which I will present below.

Inside the ``Provider`` we are defining a ``Router`` from ``react-router``. This should
be the parent component inside which all client-side routes of our appliccation are defined.
The ``Router`` gets a ``history`` parameter which is initialized elsewhere.

Now, inside ``Router`` we are defining the actual routes of this application. As we see,
there's a parent ``Route`` that is connnected to the ``App`` component which actually
contains everything else. The parent route contains an ``IndexRoute`` whose corresponding
component (``BookPanel``) is called
when no route is defined and a bunch of normal ``Route`` components whose
components are called when the url matches their part. Notice how we pass parameters
to urls (e.g ``/book_update/:id``) and the match-all route 
(``<Route path="*" component={NoMatch}/>``). 

Finally as an example of a routed-to component, notice the ``About`` component
which is rendered when the route is ``/about``. This is just a normal react component that-
will be rendered *inside* the ``App`` component -
the ``Link`` is a ``react-router`` component that renders a link to a defined route.

store.js
========

The ``store.js`` module contains the definition of the global store of our application
(which is passed to the ``Provider``).
Here, we also define the ``history`` object we pass to the parent ``Router``.

.. code::

    import { reducer as formReducer } from 'redux-form';

    import createHistory from 'history/lib/createHashHistory'

    // Opt-out of persistent state, not recommended.
    // https://github.com/reactjs/history/blob/master/docs/HashHistoryCaveats.md
    export const history = createHistory({
        queryKey: false
    });

    
First of all, we see that our ``history`` object is of type HashHistory
(`more info about history types`_) and I've also opted out of using
``queryKey``. If I hadn't used the ``queryKey: false`` configuration
then there'd be a ``?_k=ckuvup`` query parameter in the URL. Now, this
parameter is actually useful (it stores location state *not* present
in the URL for example POST form data) but I don't need it for this
example (and generally I prefer clean URLS) - but if you don't like
the behavior of your history then go ahead and add it.

Also, notice that I've used ``HashHistory`` which will append a ``#``
to the URL and the client-side URL will come after that, so all
URLs will be under (for example) ``/index.html`` like ``/index.html#/authors``.
The react-router 
documentation recommends using ``BrowserHistory`` which uses normal (clean)
urls -- so instead of ``/index.html#/authors`` we'd see ``/authors`` if we'd
used ``BrowserHistory``. 
The problem with ``BrowserHistory`` is that you'll need to configure correctly
your HTTP server so that it will translate every URL (/foo) to the same
URL under ``/index.html`` (``/index.html#/foo``). In my case, I don't think
that configuring your HTTP server is worth the trouble and also I do really
prefer using ``#`` for client-side urls! This is a common patter, recognised
by everybody and even without the HTTP server-configuration part I'd still
prefer ``HashHistory`` - of course this is just my opinion, feel free to use
``BrowserHistory`` if you don't like the hash ``#``!

.. code::

    const reducer = combineReducers(Object.assign({}, { 
            books, 
            notification,
            ui,
            categories,
            authors,
        }, {
            routing: routeReducer
        }, {
            form: formReducer     
        })
    )

    const reduxRouterMiddleware = syncHistory(history)

    const store = createStore(reducer, applyMiddleware(
        thunk, reduxRouterMiddleware
    ));
    
    export default store

Please notice above that the ``Object.assign`` method is used - I'll talk about
it later --  however, another common ES6 idiom that I've used is that when you define
an object you can change  ``{ x: x }`` to ``{ x }``.
    
The next block of code from ``store.js`` generates the most important
part of our store, the reducer! The ``combineReducers`` function is provided
by redux and is a helper function that helps you in ... combining reducers!
As you see, I've combined the reducers defined in this application 
``(books, notification, ui, categories, authors)`` with the reducers 
of ``react-router-redux`` and ``redux-form``. I'll talk a bit in the next
interlude on what does combining reducers is.

The remaining of the code generates the ``store``: First of all, a middleware
(please see next interlude for more)
is created with ``syncHistory`` that allows actions to call history methods
(so that when the URL is changed through actions they will be reflected to the
history). Then, the ``createStoreWithMiddleware`` function is called to generate 
the store that will be passed to the ``Provider``. This functions takes the 
reducer as a parameter along with any store enchancers that we'd like to
apply. A store enchancer is a function that modifies the store. The only
store enchanccer that we use now is the output of the 
``applyMiddleware`` function that combines the two middlewares we've defined (one is for
redux thunk, the other is for ``syncHistory``).
            
Interlude: Combining reducers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

So, what does the ``combineReducers`` function do? As we've already seen,
the reducer is a simple function that gets the current state and an
action as parameters and returns the next state (which is the result of applying
the action to the state). The reducer will have a big switch statement that
checks the type of the action and returns the correct new state. Unfortunately,
this switch statement may get way too large and unmaintainable for large projects.

That's where combining reducers comes to the rescue: Instead of having one big,
monolithic reducer for all the parts of our application, we can break it to individual
reducers depending only on specific parts of the state object. What this means is
that if we have for example a state tree like this:

.. code::

  {
    'data': {},
    'ui': {}
  }
  
  
  
with actions that manipulate either data or ui, we could create two indivdual reducers,
one that would manipulate the data, and one for the ui. These reducers would get *only* 
the slice of the state that they are interested to, so the ``dataReducer`` will get 
only the ``data`` part of the state tree and the ``uiReducer`` will get only the ``ui``
part of the state tree. 

To *combine* these reducers the ``combineReducers`` function should be used. This function
gets an object with the name of the state part for each sub-reducer as keys and that sub-reducer
as values and returns returns a reducer function that passes the action along with 
the correct state slice to each of the sub-reducers and creates the global state object by
combining the output of each sub-reducer. 

For example, the combine reducers function could be something like this:

.. code::

  const combineReducers2 = o => {
    return (state={}, action) => {
        const mapped = Object.keys(o).map(k => (
            {
                key: k,
                slice: o[k](state[k], action) // call k sub-reducer and get result
            }
        ))
        const reduced = mapped.reduce((s, x)=>{
            s[x['key']]=x['slice']
            return s
        }, {})
        
        return reduced;
    }
  }

The above function gets an object (``o``) with state slices and sub-reducers 
as input and returns a function that:

* Creates an array (``mapped``) of objects with two attributes: ``key`` for each key of ``o`` and ``slice`` after applying the sub-reducer to the corresponding state slice
* Reduces and returns the above array (``reduced``) to a single object that has keys for each state slice and the resulting state slice as values

To show-off the ES6 code (and my most sadistic tendencies), 
the above code could be also writen like this:

.. code::

    const combineReducers3 = o => (state={}, action) => Object.keys(o).map(k => [
        k, o[k](state[k], action)
    ]).reduce((s, x) => Object.assign(s, {
        [x[0]]: x[1]
    }), {})


    
Interlude: Middlewares
~~~~~~~~~~~~~~~~~~~~~~

A redux middleware is `rather difficult to explain`_ technically but easier to explain
conceptually: What it does it that it can be used to extend the store's dispatch by providing
extra functionality. We've already seen such functionality, the ability to use
thunk action creators (for action creators that don't return the next state object).

If you take a look at the ``createStore`` function, you'll see that
its second parameter is called ``enhancer``. When ``enhancer`` 
is a function (like in our case where it is the 
result of ``applyMiddleware``) its return value
is ``enhancer(createStore(...))`` so it calls the result of ``applyMiddleware``
with the store as parameter. 

Now, what does ``applyMiddleware``? It gets a variable (using the spread ``...`` operator)
number of functions (let's call them middleware) as input and returns 
*another* function  (this is the ``enhancer``) that gets a store as an input and 
returns the same store with its ``dispatch`` method modified so that it
calls each middleware and passes the result to the next. So, in our case the
resulting store's dispatch function would be something like:

.. code::
    
    (action) => reduxRouterMiddleware(thunk(dispatch(action)))

Now, a middleware function looks should look like this:

.. code::

  const middleware = store => next => action => {
    // 
  }

it returns a function that gets the ``store`` as input
and returns another function. This returned function
gets ``next`` as an input. What is next? It's just the
next ``dispatch`` function to be called. So the first middleware will have the original
store's ``dispatch`` as its ``next`` parameter, the second middleware will have the
result of passing the store's ``dispatch`` from the first middleware, etc. Something like
this: ``middleware2Dispatch(next=middleware1Dispatch(next=storeDispatch))``. 

Another
explanation of the above is that a middleware: 

* is a function (that gets a store as input) that returns 
* another function (that gets the next dispatcher to be called as input) that returns
* another function (that gets an action as input) which is 
* the dispatcher modified by this middleware

Let's take a look at the thunk middleware to actually see what it looks like: 

.. code::

    function thunkMiddleware({ dispatch, getState }) {
      return next => action =>
        typeof action === 'function' ?
          action(dispatch, getState) :
          next(action);
    }
    
So, it gets the store as an input and returns a function that gets ``next`` (i.e
the next dispatcher to be called) as input. This function returns *another function*
(the modified ``dispatch``). Since this function is a dispatcher, it will get 
an ``action`` as an input and if that action 
is a function it calls this function passing it dispatch (remember how we
said if we didn't want to use thunk then we'd just create normal functions
to which we'd pass the dispatch as a parameter - that's what it does here!). 
If this action is not a function
(so it is a normal object) it just returns ``dispatch(action)`` to dispatch it.

Finally, we'll create a simple middleware that will output the action type and the 
state for every dispatch:

.. code::

  const logStateMiddleware = ({dispatch, getState}) => next => action => {
    console.log(action.type, getState())
    next(action)
  }
  
just put it in the applyMiddleware parameter list and observe all state changes!

reducers.js
===========

This module contains the definition for our own defined sub-reducers that we combined
in the previous paragraph (``books, notification, ui, categories, authors``) to create
the global reducer of the application. I've put everything in a single file, however
it is more common to create a ``reducers`` directory and put every sub-reducer inside it
as a different module. Let's start reviewing the code of the ``reducers.js`` module:

.. code::

    export const notification = (state={}, action) => {
        // ...
    }

    export const ui = (state={}, action) => {
        // ...
    }
    
The ``notification`` and `ui` are two sub-reducers that control the state of the notification popup and if 
the application is loading / is submitting. I won't go into much detal about
them, they are really simple.

Now we'll see the reducer that handles books. Before understanding the actual reducer, I will present
the initial value of the books state slice:

.. code::

    //http://stackoverflow.com/a/5158301/119071
    function getParameterByName(name) {
        var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.hash);
        return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
    }

    const BOOKS_INITIAL = {
        rows: [],
        count: 0,
        page: 1,
        sorting: getParameterByName('sorting'),
        search: getParameterByName('search'),
        book: {},
    }
    
As we see, the ``BOOK_INITIAL``
constant is used to setup an initial state for the books slice of the global state. The ``BOOKS_INITIAL`` 
attributs are:

* ``rows``: The rows of the book table
* ``count``: The number of rows that are displayed
* ``page``: The current page we are on
* ``sorting``: User-defined sorting
* ``search``: User-search / filtering
* ``book``: The data of the book to be edited/displayed

The ``BOOK_INITIAL`` constant
gets the ``sorting`` and the ``search`` initial values from the URL to allow these parameters
to be initialized from the URL (so that using a url like ``#?search=foo`` will show all books
containing ``foo``). To get the parameters from the URL I'm using the ``getParameterByName``
function. Now, the actual reducer is:

.. code::
    
    export const books = (state=BOOKS_INITIAL, action) => {
        let idx = 0;
        switch (action.type) {
            case 'SHOW_BOOKS':
                return Object.assign({}, state, {
                    rows: action.books.results,
                    count: action.books.count,
                });
                break;
            case 'SHOW_BOOK':
                return Object.assign({}, state, {
                    book: action.book
                });
                break;
            case 'CHANGE_PAGE':
                return Object.assign({}, state, {
                    page: action.page
                });
                break;
            case 'TOGGLE_SORTING':
                return Object.assign({}, state, {
                    sorting: (state.sorting==action.sorting)?('-'+action.sorting):action.sorting
                });
                break;
            case 'CHANGE_SEARCH':
                return Object.assign({}, state, {
                    search: action.search
                });
                break;
            case 'ADD_BOOK':
                return Object.assign({}, state, {
                    book: action.book,
                    count: state.count+1,
                    rows: [
                        ...state.rows,
                        action.book,
                    ]
                });
            case 'UPDATE_BOOK':
                idx = state.rows.findIndex( r => r.id === action.book.id)
                if(idx==-1) {
                    return Object.assign({}, state, {
                        book: action.book
                    });
                } else {
                    return Object.assign({}, state, {
                        book: action.book,
                        rows: [
                            ...state.rows.slice(0, idx),
                            action.book,
                            ...state.rows.slice(idx+1),
                        ]
                    });
                }
                break;
            case 'DELETE_BOOK':
                idx = state.rows.findIndex( r => r.id == action.id)
                if(idx==-1) {
                    return Object.assign({}, state, {
                        book: undefined
                    });
                } else {
                    return Object.assign({}, state, {
                        book: undefined, 
                        count: state.count-1,
                        rows: [
                            ...state.rows.slice(0, idx),
                            ...state.rows.slice(idx+1),
                        ]
                    });
                }
                break;

        }
        return state;
    }
    


The books subreducer handles the ``SHOW_BOOKS, SHOW_BOOK, CHANGE_PAGE, TOGGLE_SORTING`` and ``CHANGE_SEARCH``
actions by retrieving the paramaters of these actions and returning a new books-state-slice object with the correctl
parameters. To achieve this, the ``Object.assign()`` method is used. This method is defined like this
``Object.assign(target, ...sources)``. Its first parameter is an object (a new, empty object) while the rest
parameters (``sources``) are other objects whose properties will be assigned ``target``. The rightmost members of 
``sources`` overwrite the previous ones if they have the same names. So, for example the code

.. code::

    Object.assign({}, state, {
        rows: action.books.results,
        count: action.books.count,
    });

creates a new object which will have all the properties of the current ``state`` with the exception of the
``rows`` and ``count`` attributes which will get their values from the ``action``. This is a common idiom in 
redux and you are going to see it all the time so please make sure that you grok it before continuing. Also,
notice that the new state is a new, empty object in which all the attributes of the new state are copied - this is because
the old state cannot be mutated.

The ``ADD_BOOK`` action is a little more complicated: This action will be dispached when a new book is added with
the data of that new book as a parameter (``action.book``). In order to make everything easier, I just append the new
book to the end of the current page and increase the count number (I also set the new book to be the ``book`` attribute
of the state). This means that the newly created book will not go to its correct place (based on the ordering) and
that the visible items will be more than the ajax page coun (also notice that if you add another book then the visible
items will also be increased by one more). This is not a problem (for me) since if the user changes page or does a search
everything will fall back to its place. However, if you don't like it there are two solutions, one easier and one more
difficult:

* Easier solution: When adding a book just *invalidate* (make undefined) the ``books`` state attribute. This will result in an ajax call to reload the books and everything will be in place. However the user may not see the newly added book if it does not fall to the currently selected page (and there'd be an extra, unnecessary ajax call)
* Harder solution: Well, depending on the sorting you may check if the current books should be displayed or not on the current page and push it to its correct place (and remove the last item of ``rows`` so that count is not increased). Once again, the newly book may no be displayed at all if it does not belong to the correct page

The ``UPDATE_BOOK`` and ``DELETE_BOOK`` actions are even more complex. I'll explain update, delete is more or less
the same (with the difference that update has the updated book as an action parameter while delete has only its id
as an acton parameter): First of all we check if the updated book is currently displayed (if one of the books of
``rows`` has the same ``id`` as the updated book). If the book is not displayed then only the current edited book
is set to the new state. However, if it is displayed then it would need to be updated because the ``rows`` array
does not know anything about the updated values of the book! 

So, inside the ``else`` branch, the ``idx`` variable will hold its current index and the ``rows`` attribute of the new state will get the following value:

.. code::

    [
        ...state.rows.slice(0, idx),
        action.book,
        ...state.rows.slice(idx+1),
    ]

The ``...`` spread operator expands an array so, for example ``[ ...[1,2,3] ]`` would be like ``[1,2,3]``
and the ``slice`` method gets two parameters and returns a copy of the array elements between them. Using
this knowledge, we can understand that the above code returns an array (``[]``) that contains the books of
``rows`` from the first to the updated one (not including the updated one), the updated book (which we get
from ``action``) and the rest of the books of ``rows`` (after the updated one). 

The code for the ``authors`` and ``categories`` sub-reducers does not have any surprises so I won't go
into detail about it.

.. code::

    const AUTHORS_INITIAL = {
        // ... 
    }
    export const authors = (state=AUTHORS_INITIAL, action) => {
        // ... 
    }

    const CATEGORIES_INITIAL = {
        // ... 
    }

    export const categories = (state=CATEGORIES_INITIAL, action) => {
        // ... 
    }
    

The global state tree
~~~~~~~~~~~~~~~~~~~~~

As we've already seen, the global reducer is created through ``combineReducers``
which retrieves an object with our defined reducers and two reducers from
the react-router-redux and redux-form libraries. This means, that the global 
state object will be something like this:

.. code::

  {
    books: {},
    notification: {},
    ui: {},
    categories: {},
    authors: {},
    routing: {},
    form: {},
  }

We won't see this object anywhere because each sub-reducer will get its corresponding
slice of that object.
    

actions.js
==========

The ``actions.js`` module should probably have been named ``action_creators.s`` since
it actually contains redux action creators. Also, a common practice is create a folder
named ``actions`` and put there individual modules that contain action creators for
the sub-reducers (in our case, for example there would be ``books.js``, ``authors.s`` etc).

In any case, for simplicity I chose to just use a module named ``actions.js`` and put
everything there. One important thing to keep in mind is that ``actions.js`` contains both
normal action creators (i.e functions that return actions and should be "dispatched") *and* thunk action creators (i.e
functions that not necessarily return actions but can be "dispatcher") - please see the
discussion about redux-thunk on a previous paragraph.

First of all, there's a bunch of some simple action creators that just return
the corresponding action object with the correct parameters. Notice that
the action creators that end in ``*Result`` are called when an 
(async) ajax request returns, for example ``showBooksResult`` will be
called when the book loading has returned and pass its result data to
the reducer. The other action creators change various parts of the state
object, for example ``loadingChanged`` will create an action that when
dispatched it will set ``ui.isLoading`` attribute
to the action parameter.

.. code::

    showBooksResult(books) for "SHOW_BOOKS",
    showBookResult(book) for "SHOW_BOOK",
    addBookResult(book) for "ADD_BOOK",
    updateBookResult(book) for "UPDATE_BOOK",
    deleteBookResult(id) for "DELETE_BOOK",
    
    showAuthorsResult(authors) for "SHOW_AUTHORS",
    showAuthorResult(author) for "SHOW_AUTHOR",
    addAuthorResult(author) for "ADD_AUTHOR",
    updateAuthorResult(author) for "UPDATE_AUTHOR",
    deleteAuthorResult(id) "DELETE_AUTHOR",
        
    showCategoriesResult(categories) for "SHOW_CATEGORIES",
    showSubCategoriesResult(subcategories) for "SHOW_SUBCATEGORIES",
    loadingChanged(isLoading) for "IS_LOADING",
    submittingChanged(isSubmitting) for "IS_SUBMITTING",
    toggleSorting(sorting) for "TOGGLE_SORTING",
    changePage(page) for "CHANGE_PAGE",
    changeSearch(search) for 'CHANGE_SEARCH',
    showSuccessNotification(message) for 'SHOW_NOTIFICATION' (type: success),
    showErrorNotification(message) for 'SHOW_NOTIFICATION', (type: error)
    hideNotification() for 'CLEAR_NOTIFICATION'

The following two are thunk action creators that are called when either the
user sorting or the search/filtering parameters of the displayed books are changed:

.. code::

    export function changeSearchAndLoadBooks(search) {
        return (dispatch, getState) => {
            dispatch(changeSearch(search))
            history.push( {
                search: formatUrl(getState().books)
            } )
            dispatch(loadBooks())
        }
    }

    export function toggleSortingAndLoadBooks(sorting) {
        return (dispatch, getState) => {
            dispatch(toggleSorting(sorting))
            history.push( {
                search: formatUrl(getState().books)
            } )
            dispatch(loadBooks())
        }
    }

Notice that these are thunk action creators (they return a function) and
the important thing that they do is that they call two other action creators
(``toggleSorting`` or ``changeSearch`` and ``loadBooks``) and they update the
URL using ``history.push``. The ``history`` object is the one we created in
the ``store.js`` and its ``push`` method changes the displayed URL. This
method uses a location `uses a location descriptor`_ that contains
an attribute for the path name and an attribute for the query parameters
- in or case we just want to update the query parameters (i.e ``#/url/?search=query1&sorting=query2``),
so we pass an obect with only the ``search`` attribute. The ``formatUrl`` function, to
which the books state slice is passsed,
is a rather simple function
that checks if either the sorting or the search should exist in th URL and
returns the full URL. This function is contained in the ``util/formatters.s`` module.

The following thunk action creators are used for asynchronous, ajax queries:

.. code::
    
    export function loadBooks(page=1) {
        return (dispatch, getState) => {
            let state = getState();
            let { page, sorting, search } = state.books
            let url = `//127.0.0.1:8000/api/books/?format=json&page=${page}`;
            if(sorting) {
                url+=`&ordering=${sorting}`
            }
            if(search) {
                url+=`&search=${search}`
            }
            dispatch(loadingChanged(true));
            $.get(url, data => {
                setTimeout(() => {
                    dispatch(showBooksResult(data));
                    dispatch(loadingChanged(false));
                }, 1000);
            });
        }
    }


    export function loadBookAction(id) {
        return (dispatch, getState) => {
            let url = `//127.0.0.1:8000/api/books/${id}/?format=json`;
            dispatch(loadingChanged(true));
            $.get(url, function(data) {
                dispatch(showBookResult(data));
                dispatch(loadingChanged(false));
                dispatch(loadSubCategories(data.category));
            });
        }
    }

    export function loadAuthors(page=1) {
        // similar to loadBooks
    }


    export function loadAuthor(id) {
        // similar to loadBook
    }

    export function loadCategories() {
        // similar to loadBooks
    }

    export function loadSubCategories(category) {
        return (dispatch, getState) => {
            
            if(!category) {
                dispatch(showSubCategoriesResult([]));
                return 
            }
            let url = `//127.0.0.1:8000/api/subcategories/?format=json&category=${category}`;

            $.get(url, data => {
                dispatch(showSubCategoriesResult(data));
            });
        }
    }

The ``loadBooks`` thunk action creator creates the URL parameters that should
be passed to the REST API using the ``getState()`` method that returns the current state.
It then dispatches the ``loadingChanged`` action so that the ``ui.isLoading`` will be
changed to true. After that it asynchronously calls the load books REST API and returns.
Since this is a thunk action there's no problem that nothing is returned. When the 
ajax call returns it will dispatch the ``showBooksResult``, passing the book data to
change the state with the loaded book data and the ``loadingChanged`` to hide the loading
graph. Also, please notice that I've put the return of the ajax call inside a ``setTimeout``
to emulate a 1 second delay and be able to see the loading spinner. Also, I may have used
setTImeout in some other places to make sure to be able to emulate server-side delays. 

*Please don't forget to remove these ``setTimeout``s from your code!*

The ``loadBook`` is more or less the same - however here only a single book's data will
be loaded. When this book is loaded the ``loadSubCategories`` action will also be dispatched,
passing it the loaded book's category (so that the correct subcategories based on the category
will be displayed to the form).

I won't go into any detail about the other thunk action creators, they are simpler than those
we've already described, except ``loadSubCategories``: This one, checks if there's a category
and if not it will just set the displayed subcategories to and empty list (by dispatching
``showSubCategoriesResult([])``). If the category is not empty, it will retrieve asynchronously the
subcategories of the passed category.

components/app.js
=================

We'll now start explaining the actual react components (modified to be used through redux of course).
The parent of all other components is the ``App`` which, as we've already seen in ``main.js`` it
is connected with the parent route:

.. code::

    class App extends React.Component {

        render() {
            const { isLoading } = this.props.ui;
            return <div>

                {this.props.children}

                <NotificationContainer />
                <LoadingContainer isLoading={isLoading} />

                <br />

                <StatPanel bookLength={this.props.books.count} authorLength={this.props.authors.rows.length} />
                <Link className='button' to="/">Books</Link>
                <Link className='button' to="/authors/">Authors</Link>

            </div>
        }

        componentDidMount() {
            let { loadBooks, loadAuthors } = this.props;
            
            if(this.props.books.rows.length==0) {
                loadBooks();
            }
            if(this.props.authors.rows.length==0) {
                loadAuthors();
            }
        }
    }

    const mapStateToProps = state => ({
        books:state.books,
        authors:state.authors,
        ui:state.ui,
    })

    const mapDispatchToProps = dispatch => bindActionCreators({ 
        loadBooks, loadAuthors 
    }, dispatch)


    export default connect(mapStateToProps, mapDispatchToProps)(App);

As we can see, there's an internal component (named ``App``) but we export the ``connect``ed component. This
connected component uses mapStateToProps for defining the state attributes that should be passed as properties
to the componnt (``state.{books, authors, ui}``) and ``mapDispatchToProps`` for defining the ``props`` methods that will
dispatch actions. To make ``mapDispatchToProps`` more compact I've used the ``bindActionCreators`` method from redux.
This method gets an object whose values are action creators and the ``dispatch`` (from store) and returns an object
whose values are the dispatch-enabled corresponding action creators. So, in our case
the returned object would be something like:

.. code::
    
    {
        loadBooks: () => dispatch(loadBooks()),
        loadAuthors: () => dispatch(loadAuthors()),
    }

This object of course could be created by hand, however bindActionCreators would be really useful if we wanted
to dispatch lots of actions in a component (or if we had seperated our action creators to different modules) --
we could for example do something like this:

.. code::

    import * as actions from '../actions'
    
    const mapDispatchToProps = dispatch => bindActionCreators(actions, dispatch)
    
The ``import *`` statemenet will create an object named item that will have all the exported actions and then
``bindActionCreators`` will return an object that dispatches these actions -- passing this ``mapDispatchToProps``
to connect will allow your component to call every action and automatically dispatch it. 
    
The internal component returns a ``<div />`` containing, among others ``{this.props.children}`` - this
will be provided by rendering the child routes. It also renders a ``NotificationContainer`` to render the notifications, a 
``LoadingContainer`` to display a css "loading" spinner and a ``StatPanel`` to display some stats about books and
authors. It also renders two Links one for the books table and one for the authors table.

Beyond these, when the component is mounted it checks if the authors and books have been loaded and if not, it
dispatches the ``loadBooks`` and ``loadAuthors`` actions (remember, because we used ``mapDispatchToProps`` by
calling these methods from ``props`` they'll be automatically dspatched).

Let's take a quick look at the three small components that are contained in ``App``

components/notification.js
~~~~~~~~~~~~~~~~~~~~~~~~~~

This component is responsible for displaying a notification if there's an active one.
It also defines an internal component and exports a connected version of it, passing it the
``notification`` slice of the state tree and an ``onHide`` method that dispatches the
``hidNotification`` action. 

When the internal component is rendered, it checks to see if the notification should be
displayed (``isActive`` will be true if there's an actual message) and select the color
of the background. Finally, it passes this information along with some styling 
to the real ``Notification``  component from ``react-notification``.

.. code::

    const NotificationContainer = (props) => {
        let { message, notification_type } = props.notification;
        let { onHide } = props;
        let isActive = message?true:false;
        let color;

        switch(notification_type) {
            case 'SUCCESS':
                color = colors.success
                break;
            case 'ERROR':
                color = colors.danger
                break;
            case 'INFO':
                color = colors.info
                break;
        }
        
        return <Notification
            isActive={isActive}
            message={message?message:''}
            dismissAfter={5000}
            onDismiss={ ()=>onHide() }
            action='X'
            onClick={ ()=>onHide() }
            style={{
                bar: {
                    background: color,
                    color: 'black',
                    fontSize: '2rem',
                },
                active: {
                    left: '3rem',
                },
                action: {
                    color: '#FFCCBC',
                    fontSize: '3rem',
                    border: '1 pt solid black'
                }
            }}
        />
    }


    let mapStateToProps = state => ({
        notification: state.notification
    })

    let mapDispatchToProps = dispatch => ({
        onHide: () => {
            dispatch(hideNotification())
        }
    })	

    export default connect(mapStateToProps, mapDispatchToProps)(NotificationContainer);
    
Creating a re-usable notification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
Please notice that although I've implemented this as a connected component this is not the only
way to do it! Actually, probably my implementation is less-reusable from the others I will propose... 

In any case, instead of implementing ``NotificationContainer`` as a connected component we could
have implemented it as a normal, non connected component that would receive two properties: 
the ``notification`` slice of state and an ``onHide`` function that would dispatch 
``hideNotification``. Doing this would be very easy, just change 
``App`` so that its ``mapDispatchToProps`` would also return the ``notification`` slice of 
the state - and pass this slice as a property to the ``NotificationContainer``. Also, the 
``onHide`` method should have been also defined in the ``mapDispatchToProps`` of ``App`` and
passed as a property to ``NotificationContainer``. Notice that this makes ``NotificationContainer``
a reusable component since we could pass anything we wanted as the ``notification`` object and
``onHide`` method.

Also, if we needed to implement ``NotificationContainer`` as a connected object but we still
needed it to be reusable we'd then export the non-connected ``NotificationContainer`` 
and create a bunch of ``ConnectedNotificationContainer`` that would 
define ``mapStateToProps`` and ``mapDispatchToProps``
and export the connected component. This way, each ``ConnecteNotificationContainer`` would
receive a different state slice and a different ``onHide`` method, for example we may had
different notifications for books and different notifications for authors. Notice that this
approach, i.e create a reusable non-connected component and use it to create connected
components by defining their ``mapStateToProps`` and ``mapDispatchToProps`` is the 
approach proposed by react-redux to create components.

Finally, one last comment on this approach that will clarify 
the purpose of  ``mapStateToProps`` and
``mapDispatchToProps`` is that these two functions are dual (mirror): 

* Using ``mapStateToProps`` we define which parts of the state will actually be passed to the component (= read the state).
* Using ``mapDispatchToProps`` we define the actions which will be dispatched by the component (= change/write the state)

 
components/loading.js
~~~~~~~~~~~~~~~~~~~~~

This is a really simple component: If the ``isLoading`` parameter is true, display a ``div`` with the ``loading`` class:

.. code::

    export default ({isLoading}) => <div>
        {isLoading?<div className="loading">Loading&#8230;</div>:null}
    </div>
    
The important thing here is what the ``loading`` class does to display the spinner - I'm leaving it to you to check 
it at ``static/cssloader.css`` (this is not my css code - I've copied it from http://codepen.io/MattIn4D/pen/LiKFC ).


components/StatPanel.js
~~~~~~~~~~~~~~~~~~~~~~~

Another very simple component - just display the number of books and authors from the passed parameter.

components/BookPanel.js
=======================

Continuing our top-down approach on exploring the project, we'll now talk 
about the ``BookPanel`` component which is displayed by the ``IndexRoute``.
Before talking about the actual component, I'd like to present a 
the ``getCols`` function that is used to create an array of the columns
that will be displayed by the ``Table`` we render in this panel. 

As we can see, the ``getCols`` gets one parameter which is the sort method -- 
this method gets a string and uses it to toggle sorting by this string.
Each column, has up to four parameters: 

* A ``key`` which is the attribute  of the ``row`` object to display
* A ``title`` which is the column title
* A ``format`` which may be used to display the value of that column and
* A ``sorting`` which is a function that will be called when the column title is clicked (so that the sorting is changed ) - this attribute is created using the ``sort_method``

We'll see how these attributes are used by the ``Table`` in the corresponding section.

.. code::

    const getCols = sort_method => [
        {
            key: 'id',
            label: 'ID',
            format: x=><Link to={`/book_update/${x.id}/`}>{x.id}</Link>,
            sorting: sort_method('id')
        },
        {key: 'title', label: 'Title', sorting: sort_method('title')},
        {key: 'category_name', label: 'Category', sorting: sort_method('subcategory__name')},
        {key: 'publish_date', label: 'Publish date', sorting: sort_method('publish_date')},
        {key: 'author_name', label: 'Author', sorting: sort_method('author__last_name')},
    ]
    

The actual ``BookPanel`` is a connected component - we need to use connect because we can't
actually pass properties or ``dispatch`` to this component since it is
rendered through a route (and not as a child of another component), so it
must be connected to the store through ``connect``. We pass the ``books`` state
slice as a property using ``mapStateToProps`` and use the same techique as 
before in ``App``  with
``bindActionCreators`` to create auto-dispatchable actions.

As we can see, after retrieving the needed properties from the ``books`` state slice
and the actions to dispatch, we define an ``onSearchChanged`` function that will be 
passed to the ``BookSearchPanel`` to be called when the search query is changed.

After that, the ``sort_method`` is defined: Please notice the ``sort_method`` is
a function that gets a ``key`` parameter and returns another function that 
dispatches ``toggleSortingAndLoadBooks`` with that ``key``. This is the 
parameter that is passed to ``getCols``. So, for example for the ``id``,
the result of the ``sort_method`` would be the following function:
``() => toggleSortingAndLoadBooks('id')``.

Finally, we see that the ``BookPanel`` renders the following:

* A ``BookSearchPanel`` passing it the ``search`` property and the ``onSearchChanged`` action
* A ``Link`` to create a new book
* A ``Table`` passing it the ``sorting`` and ``rows`` parameters and the ``cols`` constant we just defined
* A ``PagingPanel`` passing it the total number of books (``count``), the current page (``page``) and two methods ``onNextPage`` and ``onPreviousPage`` that will be called when switch to the next or previous page.

As we can see, the ``onNextPage`` and ``onPreviousPage`` dispach the ``changePage`` action passing it
the page to change to and reload the books by dispatch ``loadBooks``. Instead of this we could create
a ``changePageAndLoadBooks`` thunk action creator that would call these two methods when dispatched
(similarly to how ``changeSearchAndLoadBooks`` and ``toggleSortingAndLoadBooks`` have been implemented).
    
.. code::

    class BookPanel extends React.Component {
        render() {
            const { rows, count, page, sorting, search } = this.props.books;
            const { loadBooks, changePage, toggleSortingAndLoadBooks, changeSearchAndLoadBooks  } = this.props;
            
            const onSearchChanged = query => changeSearchAndLoadBooks(query)
            const sort_method = key => () => toggleSortingAndLoadBooks(key)
            const cols = getCols(sort_method)

            return <div>
                <BookSearchPanel search={search} onSearchChanged={onSearchChanged} />
                <div className="row">
                    <div className="twelve columns">
                        <h3>Book list <Link className='button button-primary' style={{fontSize:'1em'}} to="/book_create/">+</Link></h3>
                        <Table sorting={sorting} cols={cols} rows={rows} />
                    </div>
                </div>
                <PagingPanel count={count} page={page} onNextPage={() => {
                    changePage(page+1);
                    loadBooks()
                }} onPreviousPage={ () => {
                    changePage(page-1);
                    loadBooks()
                }} />
            </div>
        }
    }

    const mapStateToProps = state => ({
        books:state.books,
    })

    const mapDispatchToProps = dispatch => bindActionCreators({ 
        loadBooks, changePage, toggleSortingAndLoadBooks, changeSearchAndLoadBooks 
    }, dispatch)

    export default connect(mapStateToProps, mapDispatchToProps)(BookPanel);

components/BookSearchPanel.js
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``BookSearchPanel`` is a component used for searching books. What
is interesting about this component is that it has internal state (i.e 
state that is not reflected to the global search tree). Notice that this
is an ES6 class component:

* It extends ``React.Component`` instead of using ``React.CreateClass``
* It has a constructor that initializes the local state instead of implementing ``getInitialState``
* It does not automatically bind the methods to ``this`` so we do it in the constructor (or else ``this`` would be undefined in ``onSearchChange`` and ``onClearSearch``)

So, what happens
here? We render an HTML ``input`` element and call ``this.onSearchChange``
method. This method retrieves the current value of te input (using ``this.refs``)
and, if the previous change was more than 400 ms ago, it sets the local
state and calls the provided
(through ``props``) ``onSearchChanged`` method that will dispatch the
``changeSearchAndLoadBooks`` action with the current value as a parameter. 
The whole thing with the ``ths.promise`` and ``clearInterval`` is to make
sure that the provided ``onSearchChanged`` will not be called too often.


.. code::

    export default class SearchPanel extends React.Component {
        constructor() {
            super()
            this.onSearchChange = this.onSearchChange.bind(this)
            this.onClearSearch = this.onClearSearch.bind(this)
            this.state = {}
        }
        
        render() {
            return (
                <div className="row">
                    <div className="one-fourth column">
                        Filter: &nbsp;
                        <input ref='search' name='search' type='text' defaultValue={this.props.search} value={this.state.search} onChange={this.onSearchChange } />
                        {(this.state.search||this.props.search)?<button onClick={this.onClearSearch} >x</button>:''}
                    </div>
                </div>
            )
        }
        
        onSearchChange() {
            let query = ReactDOM.findDOMNode(this.refs.search).value;
            if (this.promise) {
                clearInterval(this.promise)
            }
            this.setState({
                search: query
            });
            this.promise = setTimeout(() => this.props.onSearchChanged(query), 400);
        }
        
        onClearSearch() {
            this.setState({
                search: ''
            });
            this.props.onSearchChanged(undefined) 
            
        }
    }


Finally when there's a search query a  ``x`` button will be displayed which, when 
clicked the search local state will be cleared 
and the provided ``onSearchChanged`` will be called with an empty query.
    
Conslusion
----------

The above is a just a proof of concept of using FixedDataTable with asynchronously loaded server-side data. 
This of course could be used for small projects (I am already using it for an internal project) but I recommend
using the `flux architecture <{filename}react-flux-tutorial.rst>`_ for more complex projects. What this more or
less means is that a store component
should be developed that will actually keep the data for each row, and a ``fetchCompleted`` action should be 
dispatched when the ``fetch`` is finished instead of calling ``forceUpdate`` directly.

.. _redux: https://github.com/rackt/redux
.. _react-redux: https://github.com/rackt/react-redux
.. _`redux documentation`: http://rackt.org/redux/index.html
.. _`getting started with redux`: https://egghead.io/series/getting-started-with-redux
.. _history: https://github.com/rackt/history
.. _react-notification: https://github.com/pburtchaell/react-notification
.. _react-router: https://github.com/rackt/react-router
.. _react-router-redux: https://github.com/rackt/react-router-redux
.. _redux-form: https://github.com/erikras/redux-form
.. _redux-thunk: https://github.com/gaearon/redux-thunk
.. _`react-redux documentation`: https://github.com/rackt/react-redux/blob/master/docs/api.md#connectmapstatetoprops-mapdispatchtoprops-mergeprops-options
.. _`react context`: https://facebook.github.io/react/docs/context.html
.. _`great SO answer`: http://stackoverflow.com/a/35415559/119071
.. _`more info about history types`: https://github.com/reactjs/react-router/blob/latest/docs/guides/Histories.md#hashhistory
.. _`rather difficult to explain`: http://redux.js.org/docs/advanced/Middleware.html
.. _`uses a location descriptor`: https://github.com/reactjs/history/blob/master/docs/Location.md#location-descriptors