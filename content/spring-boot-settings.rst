How to configure your Spring Boot applications
##############################################

:date: 2016-03-28 08:55
:tags: spring, spring-boot, java, ldap, profiles, settings, properties
:category: spring
:slug: spring-boot-settings
:author: Serafeim Papastefanos
:summary: An opinionated methodology for configuring your Spring Boot applications using application properties, profiles, locan  settings and command line arguments!

.. contents::

Introduction
------------

The spring-boot_ project is great way of building Java applications using
Spring. Instead of trying to integrate everything by hand (configuration
hell) you use spring-boot to help you to bootstrap your: Just include your 
dependencies in your pom.xml and spring-boot will try its 
best to auto-configure all the components. 

Of course, no matter how hard spring-boot try, you'll still need to pass
some configuration to configure your databases, caches, ldap connections,
email sending, authentication, authorization etc. Thankfully, spring boot
can be configured without *any* xml (actually, its a bad practice to
use xml-based configuration with spring-boot), using plain Java .properties
or (if you prefer the more compact syntax) .yml files! 

In this guide, along with a simple introduction to the way spring-boot configuration
works, I'll propose an opinionated methodology for configuring your spring-boot
applications and stucturing your configuration files. In the end, you'll have
the following:

* A global configuration file that will contain all your settings
* Different settings for each of your environments (development, UAT, staging, production and test)
* A way to configure your passwords and other sensitive data (that you don't want to put to your VCS)
* Being able to override any setting in any environment


A basic spring security setup
-----------------------------

We'll use four different options for keeping our settings. Starting from the most global to the most
specific ones (i.e the latter ones will override the previous ones):

Main application settings
=========================

These are kept in ``application.properties`` (or ``yml``): This file should be inside the ``resources`` folder
of your project an ideally contain *all* the settings your spring-boot application users. Some
of these settings will be overriden by settings kept in the next source so they may have a
default valur or even be empty if they will be alwas overriden, however I still prefer to list
them all in this file even as placeholders to have a central source of all the application settings.

Profiles
========

A profile is a set of settings that can be configured to override settings from ``application.properties``.
Each profile is contained in a file named ``application-profilename.properties`` where ``profilename`` is
the name of the profile. Now, a profile could configure anything you want, however I propose to 
have the following profile names (depending of course on what are your requirements): 
* ``dev`` for your local development settings
* ``uat`` for your UAT server settings
* ``staging`` for your staging server settings
* ``prod`` for your production settings
* ``test`` for running your tests

These need to be different because, for example when developing you may want
to use a local database, when running tests an ephemeral, in memory database
etc. These profile files will be stored inside your ``resources`` folder,
right next to the ``application.properties`` (or ``yml``), i.e you'll have
``application-dev.properties``, ``application-prod.properties``, 
``application-test.properties`` etc - and all these files will be kept
in your VCS.

How do you select which profile is active each time (i.e correlate its
with the corresponding environment)? For tests, since they use a 
different executable you can use the ``@ActiveProfiles`` annotation
(for example ``@ActiveProfiles("test")``) to make sure that the tests
will run with the correct settings.

To activate a different profile when running your spring boot applications
you should use the ``spring.active.profiles`` setting, so if you set
``spring.active.profiles==prod`` in your ``application.properties`` and
create the packaged jar (or war) then you'll have the production settings  
when you run your application. To deploy it to UAT, you'll need to change
``spring.active.profiles`` to ``uat`` and re-create the packaged artifact --
see something nasty here? Definitely you don't want to do re-create 4
different artifacts for each of the environments you may want to deploy! 
We'll see in the next sections how to improve this flow!

Some more advanced profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may have noticed in the previous section that the name of the 
annotation is ``@ActiveProfiles`` and the name of the setting 
``spring.active.profiles`` - both in plural. This of course is 
on purpose: You may have *more than one* active profiles! 

Conclusion
----------

In the previous a complete example of configuring a custom authorities populator was represented. Using this configuration we can login through the LDAP server of our organization but use application specific roles for our logged-in users.

.. font-size: 0.5em;
   vertical-align: top;



.. _spring-boot: http://projects.spring.io/spring-boot/
.. _spring-security: http://projects.spring.io/spring-security/
