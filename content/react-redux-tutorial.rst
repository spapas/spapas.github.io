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

The general idea/flow is:

- Something (let's call it event) happens (i.e a user clicks a button, a timeout is fired, an ajax request responds)
- An action describing that event is created and dispatched (i.e passed to the reducer along with the current state)
- The reducer is called with the current state object and the action as parameters
- The reducer checks the type of the action and, depending on the action type and any other properties this action has, creates a new state object
- The new state is applied to all components

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