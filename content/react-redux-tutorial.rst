A comprehensive react-redux tutorial
####################################

:date: 2016-02-03 15:20
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

All client side code is written in ES6 javascript using the latest trends -- I will
try to explain anything I feel that is not very clear.

Before continuing, I have to mention that I won't go into detail on how redux and
react-redux work but I will concentrate on the correct integration between them and
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
- One (and only one) **reducer**: It is a function that retrieves the current state and an action and creates the resulting state. One very important thing to keep in mind is that the reducer *must not* mutate the state but return *a new object when something changes*.
- One (and only one) **store**: It is an object that is created by redux and is used as a glue between the state, the reducer and the components

The general idea/flow is:

- Something (let's call it event) happens (i.e a user clicks a button, a timeout is fired, an ajax request responds)
- An action describing that event is created and dispatched (i.e passed to the reducer along with the current state) through the store
- The reducer is called with the current state object and the action as parameters
- The reducer checks the type of the action and, depending on the action type and any other properties this action has, creates a new state object
- The store applies the new state to all components

One thing we can see from the above is that redux is not react-only (although its general architecture fits perfectly with react) but
could be also used with different view frameworks, or even with *no view framework*!

A simple example
================

I've implemented a very simple redux example @ jsfiddle_ that increases and decreases
a number using two buttons to support the above: 

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

The flow of the data when the increase button is clicked is the following:

- button.onClick
- increase()
- store.dispatch({type: 'INCREASE' })
- reducer(current_state, {type: 'INCREASE'})
- callback()
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
returns the new state which is the result of applying this action to the state!


What about react-redux?
=======================

React-redux is a rather simple framework that offers two helpful utilities for integrating
redux with React:

- A ``connect`` function that "connects" React components to the redux store. This function (among others) retrieves a callback parameter that defines properties that will be passed (magically) to that component and each one will be mapped to state properties.
- A ``Provider`` component. This is a parent component that can be used to (magically) pass the store to its children components.

This will be made more clear with `another jsfiddle`_ that will convert the previous example to React and
react-redux! The html is just ``<div id='container'></div>`` while the es6/jsx code is:

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
be enclosed in a ``<Provider>`` parent component that will (magically) pass them to this component. Notice
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

Let's see an example of what we'll build:

.. image:: /images/ajax_fixed_data_tables.gif
  :alt: Our project
  :width: 600 px


Other libraries used
--------------------

React (and redux) have a big ecosystem of great libraries. Some of these have been used
for this project and will also be discussed:
  
- redux-thunk_: This is a *really* important add-on for redux that creates actions that can call other actions, or actions that can be called (dispatched) asynchronosuly. *Do not* use redux without it, especially if you want to use Ajax!
- redux-form_: A better way to use forms with react and redux. Always use it if you have non-trivial forms.
- react-router_: A library to create routes for single page applications with React
- react-router-redux_ (ex redux-simple-router): This library will help integrating react-router with redux
- history_: This is used bt react-router to crete the page history (so that back forward etc work)
- react-notification_: A simple react component to display notifications
  
  
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
.. _jsfiddle: https://jsfiddle.net/8aba3sp6/
.. _`another jsfiddle`: https://jsfiddle.net/8aba3sp6/2/
.. _`react-redux documentation`: https://github.com/rackt/react-redux/blob/master/docs/api.md#connectmapstatetoprops-mapdispatchtoprops-mergeprops-options