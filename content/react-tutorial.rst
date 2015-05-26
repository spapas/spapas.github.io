A comprehensive React and Flux tutorial
#######################################

:date: 2015-05-26 14:20
:tags: javascript, python, django, react, flux, browserify, node, npm, watchify
:category: javascript
:slug: comprehensive-react-flux-tutorial
:author: Serafeim Papastefanos
:summary: A multi-part React and Flux tutorial that tries to be as comprehensive as possible! 

.. contents::

Introduction
------------

React_ is a rather new library from Facebook for building dynamic components for web pages. 
It introduces a really simple, fresh approach to javascript user interface building. React
allows you to define composable and self-contained HTML components through Javascript (or a special syntax that compiles
to javascript named JSX) -- and nothing else. It's like writing HTML but you have the
advantage of using 

React usually is used with a specific application architecture, also proposed
by Facebook, named Flux_. It's important to keep in your mind that Flux is not a 
specific framework but a way to organize your source code.

In this three part tutorial we are going to build a simple single page CRUD application using
React. We will then improve this application so that it uses the browserify_ and watchify_
node.js utils to enchant the javascript compilation workflow. Finally, we'll integrate the
Flux architecture to our project and understand why it'll greatly improve the React experience.

Our project
-----------

Before starting, let's take a look at what we're going to build:

.. image:: /images/demo.gif 
  :alt: all ok!
  :width: 780 px
  
Our application will be seperated to two panels: In  the left one the user will be able to filter (search) for
a book and in the right panel she'll be able to add / edit / delete a book. Everything is supported by
a django-rest-framework_ implemented REST API. You can find the complete source code at 
https://github.com/spapas/react-tutorial. I've added a bunch of git tags to the source history in 
order to help us identify the differences between variou stages of the project (before and
after using Browserify and before and after integrating the Flux architecture).

Django-rest-framework is used in the server-side back-end to create a really simple REST API - I won't 
provide any tutorial details on that (unless somebody wants it !), however 
you may either use the source code as is or create it from scratch using a different language/framework
or even just a static json file (however you won't see any changes to the data this way). A little bit of styling is added using purecss_.


.. _React: https://facebook.github.io/react/
.. _Flux: https://facebook.github.io/flux/docs/overview.html
.. _django-rest-framework: http://www.django-rest-framework.org/
.. _browserify: http://browserify.org/
.. _watchify: https://github.com/substack/watchify
.. _purecss: http://purecss.io/