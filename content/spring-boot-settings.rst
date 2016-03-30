Configuring Spring Boot
#######################

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

To quickly test the proposed settings configuration I've created a simple
Spring Boot project @ https://github.com/spapas/spring-boot-config. Just clone
it, optionally change the packaged settings (more on this later), package it (``mvn package``), change 
the ``config`` settings (more on this also later) and run it 
(``java -jar target\spring-boot-config-0.0.1-SNAPSHOT.jar``) passing it command line settings (more on this
also later). You'll then be able to visit ``http://127.0.0.1:8080`` and check the current settings!

properties vs yml files
-----------------------



Different settings keeping options
----------------------------------

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
you should use the ``spring.profiles.active`` setting, so if you set
``spring.profiles.active=prod`` in your ``application.properties`` and
create the packaged jar (or war) then you'll have the production settings  
when you run your application. To deploy it to UAT, you'll need to change
``spring.profiles.active`` to ``uat`` and re-create the packaged artifact --
see something nasty here? Definitely you don't want to do re-create 4
different artifacts for each of the environments you may want to deploy! 
We'll see in the next sections how to improve this flow!

Some more advanced profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may have noticed in the previous section that the name of the 
annotation is ``@ActiveProfiles`` and the name of the setting 
``spring.profiles.active`` - both in plural. This of course is 
on purpose: You may have *more than one* active profiles! 

This, along with the fact that you can make ``@Components`` or ``@Configuration``
available *only* on certail profiles is a really powerful tool!

Here are some examples: 

- Configure two spring-security ``@Configuration`` s: Use in memory security for your dev environment, while using LDAP for your production. 
- If you want to support more than one database you can configure multiple profiles -- and use them along with the dev/uat/prod I mentioned before.
- Create verbose and non-verbose logging profiles and quickly change between them


Overriding settings
===================

All the above settings we've defined should be safely kept inside
your VCS - however we wouldn't like storing passwords or other
sensitive data to a VCS! Sensitive settings should be empty 
(or have a default value) when
saved to VCS and overriden by "local" settings. Overriding settings
is also useful in selecting the correct profile for running
your application, since you can just override the ``spring.profiles.active``
setting and change your active profile, without the need to
re-package your application. There are two ways to override
settings:

Using a config/application.properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can put files in a directory named ``config`` that is at the same level
as the location from which you try to run your jar to override your jar-packaged
settings. What happens is that Spring will try to load a file named config/application.properties that will
override your jar-packaged application.properties. It will also try to load
a file named ``config/application-profilename.properties`` that will override
your jar-packaged ``application-profilename.properties``. So, repeating for
emphasis: The settings in your jar-packed application-profilename.properties will *only*
be overriden by ``config/application-profilename.properties``.

To make everything clear about where ``config`` should reside: If the current directory is ``/home/serafeim`` and
you want to execute ``/opt/spring/my-spring-app.jar`` the ``config`` directory should
be at ``/home/serafeim/config`` -- however probably the best approach wouldn
be to put it at ``/opt/spring/config`` and ``cd /opt/spring`` before running
your jar.

Now, my recommendation is to keep these ``config/*properties`` files off version control
and to put only the profile selection setting and sensitive information there. That means that 
the ``config/application.properties`` file should only contain a ``spring.profiles.active=profilename`` 
setting to set the correct profile for this instance of your app and the ``config/application-profilename.properties``
will contain all sensitive information that you'll need.

So for example in your UAT server you'll have ``spring.profiles.active=uat`` in your ``application.properties``
and your uat server passwords in your ``application-uat.properties``

Passing command line arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most specific way of overriding parameters (including the active profile of course) is by
directly passing these parameters as arguments when running your jar. For example,
if you run ``java -Dconfig.value=foo -jar my-spring-app.jar`` then the ``config.value``
will always have a value of ``foo`` no matter what you have in your other config files.

That's a different way to set your active profile or to set sensitive settings however
I prefer to keep the settings in properties files (and not to put them in scripts etc)
so I'll recommend the previous way of using a non-commited to version control local config/application.properties.


Conclusion
----------

Using the previous 


.. _spring-boot: http://projects.spring.io/spring-boot/
.. _spring-security: http://projects.spring.io/spring-security/
