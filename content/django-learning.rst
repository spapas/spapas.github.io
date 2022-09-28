A path to learn Django
######################
:status: draft
:date: 2022-09-28 11:10
:tags: python, django
:category: django
:slug: django-guidelines
:author: Serafeim Papastefanos
:summary: A path to follow for people that are interested in learning the Django web framework

In this small post I'd like to present a path to follow for people that would like to learn the Django web framework.
I'm not sure if there's something better but this should 

Prerequisites
-------------

Python
======

In order to start learning Django you need to have good knowledge of Python. Having basic knowledge of Python isn't enough.
Specifically, you need to properly understand how python implements the OOP concepts like inheritance and polymorphism because
Django makes heavy use of them. You may be able to write some copy-paste code but you will not be able to understand how Django 
works and write your own stuff unless you properly understand the OOP concepts Django uses.

If you don't have a good knowledge of Python you should start with the `official Python tutorial`_. It's a good place to start.

HTML
====

It is expected to have a good knowledge of HTML. You should know the basic tags, understand what's a form, an input, 
a submit, a div and table are and how to use them. You must know why we want to add a `name` attribute to an `input` and 
what's the different than the `id` or `class` attribute. 

HTTP
====

I recommend to also know how the HTTP protocol works. Understand what's a request, a response, a header, a redirect, a cookie and a session.
Make sure that you know the difference between a GET and a POST HTTP method and where we'd use each method. This is very important. Don't
continue with Django until you know that you know the difference between a GET and a POST and you have actually seen how these work.

Database design
===============

It is vital that you know and understand Database design. You need to know how to design a normalized database schema.
What's a foreign key and when to use it. When to use one to many, one to one and many to many relation. What are indeces
and when to use them. What's a primary key and what's the difference between a primary key and a foreign key. What's a
composite key and when to use it. What's a unique key and when to use it. What's a check constraint and when to use it.

SQL
===

Django has an ORM that abstracts the SQL database from the developer. The Django ORM is very good and you should rarely (or even never)
need to write raw SQL. However, it's very important to know at least *some* SQL or else you won't be able to understand how to do some
complex SQL queries. Also you won't be able to understand how the Django fields are mapped to the database and what are the limitations.




CSS / Javascript
================

Both CSS and Javascript are useful for learning django but are not required. You can be a Django expert without any knowledge of CSS or Javascript.
However these are going to be needed if you want to create some production application so it's a good idea to start learning them.

Learning Django
---------------

The Django tutorial
===================

The first step I always recommend is to read the `official Django tutorial`_. This is the best tutorial you are gonna find, nothing will
ever be better than that. If there are things you don't understand when reading this tutorial then you should stop and go to the 
prerequisites: Something is lacking in your knowledge of Python or HTTP or HTML. Don't try to find other tutorials or youtube videos.
I repeat that this is the best tutorial you are gonna find. Trust me on that.

Read it, understand it and follow it thoroughly by implementing all the steps it describes.

Do not continue until you've finished the tutorial aned



.. _`official Python tutorial`: https://docs.python.org/3/tutorial/
.. _`official Django tutorial`: https://docs.djangoproject.com/en/stable/intro/tutorial01/