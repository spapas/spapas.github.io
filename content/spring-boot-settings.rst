Configuring Spring Boot
#######################

:date: 2016-03-31 19:20
:tags: spring, spring-boot, java, ldap, profiles, settings, properties, yaml, configuration, deploy, init.d
:category: spring
:slug: spring-boot-settings
:author: Serafeim Papastefanos
:summary: Configuring your Spring Boot applications using application properties, profiles, locan  settings and command line arguments and deploying them using init.d!

.. contents::

Introduction
------------

The `Spring Boot`_ project is great way of building Java applications using
Spring. Instead of trying to integrate everything by hand (and usually
end up with a configuration hell) you use spring-boot to help you to 
bootstrap your application: Just include its
dependencies in your pom.xml and Spring Boot will try its 
best to auto-configure all these components!

Of course, no matter how hard Spring Boot tries to auto-configure everything, 
you'll still need to pass some configuration to configure your databases, 
caches, email sending, security etc. Thankfully, Spring Boot
can be configured without *any* xml (actually, its a bad practice to
use xml-based configuration with it), using plain Java .properties
files or (if you prefer the more compact syntax) YAML_ .yml files! 

In this guide, along with a simple introduction to the way Spring Boot configuration
works, we'll talk about a specific way of stucturing your settings configuration files in 
order to have: 

* A global configuration file that will contain all your settings
* Different settings for each of your environments (development, UAT, staging, production and test)
* A way to configure your passwords and other sensitive data (that you don't want to put to your VCS)
* Being able to override any setting in any environment
* Deploying your Spring Boot app in Linux using ``init.d``

To quickly test the proposed settings configuration I've created a simple
Spring Boot project @ https://github.com/spapas/spring-boot-config. Just clone
it, optionally change the packaged settings (more on this later), package it (``mvn package``), optionally change 
the ``config`` settings (more on this also later) and run it 
(using something like ``java -jar spring-boot-config-0.0.1-SNAPSHOT.jar``) optionally passing it command line settings (more on this
also later). You'll then be able to visit ``http://127.0.0.1:8080`` and check the current settings!

properties vs yml files
-----------------------

You can use two kinds of files to configure your settings: Normal Java .properties files
or YAML_ .yml files. The .properties files have the form:

.. code::

    config.value.a=1
    config.value.b=2
    config.value.c=3
    
while the .yml files are like:

.. code::

    config:
        value:
            a: 1
            b: 2
            c: 3

You may use whatever you wish - in the examples I'll use normal Java .properties
files because they are more compact (you don't need to use multiple lines to represent
a single setting like in YAML).

Structuring your configuration files
------------------------------------

Spring Boot reads its configuration from `various places`_, however in this article we'll talk
about four of them which should be enough for most cases. Starting from the most global to the most
specific ones (i.e the latter ones will override the previous ones) these are:

- Main (global) application settings
- Profile settings
- Local (/config) settings
- Command line arguments

The first two are setting files that will be contained inside the artifact (jar or war) that will be
created and should be commited to your version control system. I'll call them jar-packaged
settings. The other two won't be commited to the version control but will be created directly
on the server to-deploy. Let's see a little more about them: 

Main application settings
=========================

These are kept in a file named ``application.properties`` (or ``yml`` -- from now on I'll just use
`.properties`` but keep in mind that you may use ``.yml``): This file should reside 
inside the ``src\main\resources`` folder
of your project and ideally contain all the settings your spring-boot application users. Some
of these settings will be overriden by settings kept in the next source so they may have a
default value or even be empty if they will be always overriden (or contain sensitive data
like passwords), however I still prefer to list
them all in this file even as placeholders to have a central source of all the settings that
your Spring Boot application uses.

Profiles
========

A profile is a set of settings that can be configured to override settings from ``application.properties``.
Each profile is contained in a file named ``application-profilename.properties`` where ``profilename`` is
the name of the profile. Now, a profile could configure anything you want, however 
for most projects I propose to 
have the following profiles: 

* ``dev`` for your local development settings
* ``uat`` for your UAT server settings
* ``staging`` for your staging server settings
* ``prod`` for your production settings
* ``test`` for running your tests

(depending of course on what are your requirements, some projects may not
need ``uat`` or ``staging`` but all projects should have a ``dev``, a ``prod`` and a ``test`` profile).
The configuration for these environemnts needs to be different for obvious reasons. 
For example when developing you may want
to use a local database, when running tests an ephemeral in memory database
and your production database when deploying to production.
These profile configuration files will be stored inside your ``src\main\resources`` folder,
right next to the ``application.properties``, i.e you'll have
``application-dev.properties``, ``application-prod.properties``, 
``application-test.properties`` etc - and all these files will be kept
in your VCS (and will also be jar-packaged since they will be
contained in the resulting artifact).

How do you select which profile is active each time (i.e pick it
when running the Spring Boot application under 
its corresponding environment)? 

For tests, since they can be run by a different ``Main`` than
the normal application, you should use the ``@ActiveProfiles`` annotation
(for example ``@ActiveProfiles("test")``) to make sure that the tests
will run with the correct settings. So if the contents of your ``application-test.properties``
are ``config.value=Hello test!`` running this test should produce no errors:

.. code-block:: java

    @RunWith(SpringJUnit4ClassRunner.class)
    @SpringApplicationConfiguration(classes = SpringBootConfigApplication.class)
    @ActiveProfiles("test")
    public class SpringBootConfigApplicationTests {

        @Value("${config.value}")
        private String value;
        
        @Value("${spring.profiles.active}")
        private String profile;

        @Test
        public void contextLoads() {
            assertThat(value, is("Hello test!"));
            assertThat(profile, is("test"));
        }
    }
    


To activate a different profile when running your Spring Boot applications
you'll need to use the ``spring.profiles.active`` setting, so if you set
``spring.profiles.active=prod`` in your ``application.properties`` and
create the packaged jar (or war) then you'll have the production settings  
when you run your application (i.e the contents of ``application-prod.properties``
will be used to override your ``application.properties``). Of course, to deploy it 
to UAT, you'll need to change
``spring.profiles.active`` to ``uat`` and re-create the packaged artifact --
see some repetition and penal labour here? Definitely you don't want to do re-create
your artifacts for each of the environments you may want to deploy -- 
we'll see in the next sections how to improve this flow by overriding 
jar-packaged settings!

Some more advanced profile usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
saved to VCS and overriden by "local" settings. 

Also, all the previous are jar-packaged
and we definitely need a way to override them without messing
with the artifacts (for example, we need to select the
correct profile for running the application by overriding
``spring.profiles.active``). 

There two methods of overriding settings, and these are the last
two methods of the four we discussed above:

Using a config/application.properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can put files in a directory named ``config`` that is at the same level
as the location from which you try to run your jar. These file should be
named either ``application.properties`` or ``application-profilename.properties``
and will be used to override your jar-packaged
settings. 

What happens is that Spring will at first try to load a file named ``config/application.properties`` that will
override your jar-packaged ``application.properties`` (so here you can set your current profile). Then, it will also try to load
a file named ``config/application-profilename.properties`` that will override
your jar-packaged ``application-profilename.properties`` (so here you may
override any profile related properties). 

The priority of the files from lowest to highest:

- jar-packaged ``application.properties``
- local ``config/application.properties``
- jar-packaged ``application-profilename.properties``
- local ``config/application-profilename.properties``

So (repeating for emphasis) the settings in your jar-packaged ``application-profilename.properties`` will *only*
be overriden by ``config/application-profilename.properties`` (and not by the ``config/application.properties``
which will only override settings on the jar-packaged ``application.properties``).

Also, to make everything clear about where the ``config`` directory should be kept:
 
If the current directory from which you'll run your jar is ``/home/serafeim`` and
you want to execute ``/opt/spring/my-spring-app.jar`` (so you'll run something like
``/home/serafeim$ java -jar /opt/spring/my-spring-app.jar``) then 
the ``config`` directory should
be at ``/home/serafeim/config`` (i.e at the same directory from where you execute
jar). Normally however and to avoid confusion, the best approach would
be to just put it at ``/opt/spring/config`` and ``cd /opt/spring`` before running
your jar (so ``config`` will be right next to your jar and run the jar from the directory).

Finally, my recommendation is to keep these ``config/*properties`` files off version control
(after all they should be different for each of your environments - common settings should
go to the jar-packaged files)
and to put only the profile selection setting and sensitive settings there. That means that 
the ``config/application.properties`` file should *only* contain a ``spring.profiles.active=profilename`` 
setting to set the correct profile for this instance of your app and the ``config/application-profilename.properties``
will contain all sensitive information that you'll need to run that profile.

For example in your UAT server you'll have ``spring.profiles.active=uat`` in your ``application.properties``
and your uat server passwords in your ``application-uat.properties``

Passing command line arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most specific way of overriding parameters (including the active profile of course) is by
directly passing these parameters as arguments when running your jar. For example,
if you run ``java -Dconfig.value=foo -jar my-spring-app.jar`` then the ``config.value``
will always have a value of ``foo`` no matter what you have in your other config files.

That's a different way to set your active profile (by passing ``-Dspring.profiles.active=profilename``) 
or to quickly set sensitive settings however
I prefer to keep the settings in properties files (and not to put them in scripts where they will definitely
be missed and will be more difficult to be managed)
so I'll recommend the previous way of using a non-commited to version control local config/application.properties.
Use command line arguments only for quick tests (run something with a specific setting to test how it works).


Deploying Spring Boot applications
----------------------------------

If you check
the deployment documentation of Spring Boot you'll see that it has various hints on 
`on deploying Spring Boot applications`_. I won't go into much detail about these however I'll
represent my recommendation on deploying Spring Boot apps on Linux as an init.d script:

What is really interesting about Spring boot is that it allows you to make your jar-packaged jars `executable as an init.d script`_ so that you will
be able to manage it using something like ``service springbootapp start/stop/restart`` etc. To do that,
you'll just need to add the ``<executable>true</executable>`` ``configuration`` for your pom's
``spring-boot-maven-plugin``. This will add some things in the start of your resulting jar file
that will make it behave as a unix init.d script. If you take a look at your package artifact
you'll see something like this:

.. code-block:: bash

    #!/bin/bash
    #
    #    .   ____          _            __ _ _
    #   /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
    #  ( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
    #   \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
    #    '  |____| .__|_| |_|_| |_\__, | / / / /
    #   =========|_|==============|___/=/_/_/_/
    #   :: Spring Boot Startup Script ::
    #

    ### BEGIN INIT INFO
    # Provides:          spring-boot-config
    # Required-Start:    $remote_fs $syslog $network
    # Required-Stop:     $remote_fs $syslog $network
    # Default-Start:     2 3 4 5
    # Default-Stop:      0 1 6
    # Short-Description: spring-boot-config
    # Description:       Demo project for Spring Boot configuration
    # chkconfig:         2345 99 01
    ### END INIT INFO

    [[ -n "$DEBUG" ]] && set -x

    # Initialize variables that cannot be provided by a .conf file
    WORKING_DIR="$(pwd)"
    # shellcheck disable=SC2153
    [[ -n "$JARFILE" ]] && jarfile="$JARFILE"
    [[ -n "$APP_NAME" ]] && identity="$APP_NAME"

    ...
    
One thing that may seem puzzling at first is that if make this jar executable
and try to run it you'll see that, instead of offering you the well known 
options of the init scripts (Usage ... start/stop/restart etc)  it will immediatelly 
run the application! This is because the embedded script is smart enough to
check that it will be executed as an init script only when it is executed
as a link from ``/etc/init.d`` - else it will immediately run the application. 

If
you want to quickly test that behavior, you may override the ``MODE`` parameter
which forces the mode of operation of the jar. If you want to run it as a
script (without using a links from /etc/ini.d) then just set ``MODE=service``.
So, try runnin:

.. code::

    > MODE=service ./springapplication.jar
    Usage: ./hsk9eea.jar {start|stop|restart|force-reload|status|run}

Success! Of course, this is just for testing purposes, to actually deploy
your application then please create a link to it from ``/etc/init.d`` as
proposed by the Spring Boot docs.

If you want to `customize the init.d script`_  you can use a file named
``sprinbootapp.conf`` in the same directory as your ``springbootapp.jar``
(i.e it should have the same name as your jar with an extension of .conf). The
options from it will be sourced before running your application -- for example
you could set the active profile using ``RUN_ARGS``, however as I already
recommended, explicitly setting it to a file named ``config/applications.properties``
is preferrable.



Conclusion
----------

Using the described file structure you should be able to fully configure Spring Boot and have all the
goodies you'd expect from a modern framework: global settings, profiles, non-version control settings! Also, using the
advanced profiles techniques (multiple profiles, profile enabled 
@Components and @Configurations) you'll be able to implement 
some really complex configurations! Finally, you'll be able to really
quickly deploy the resulting jar as an init.d system service!


.. _`Spring boot`: http://projects.spring.io/spring-boot/
.. _YAML: https://en.wikipedia.org/wiki/YAML
.. _`various places`: https://docs.spring.io/spring-boot/docs/current/reference/html/boot-features-external-config.html
.. _`on deploying Spring Boot applications`: http://docs.spring.io/spring-boot/docs/current-SNAPSHOT/reference/htmlsingle/#deployment
.. _`executable as an init.d script`: https://docs.spring.io/spring-boot/docs/current/reference/html/deployment-install.html
.. _`customize the init.d script`: http://docs.spring.io/spring-boot/docs/current-SNAPSHOT/reference/htmlsingle/#deployment-script-customization