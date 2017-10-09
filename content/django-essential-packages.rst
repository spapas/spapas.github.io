My essential django package list 
################################

:date: 2017-10-09 10:20
:tags: django, python
:category: python
:slug: essential-django-packages
:author: Serafeim Papastefanos
:summary: A list of packages (add-ons) that I use in (almost) all my projects


In this article I'd like to present a list of django packages (add-ons) that I use
in almost all of my projects. I am using django for more than 5 years as my day to
day work tool to develop applications for the public sector organization I work for.
So please keep in mind that these packages are targeted to the "enterpripse" 
audience.

Most of these packages are included to 
`a django cookiecutter`_ I am using to start new projects and also you can find
some example usage in the `Mailer Server`_ project. I'll also be happy to answer any
questions about these, preferably in stackoverflow if the questions are fit for that.

So let's start with the list:

- django-tables2_: 
  This, along with django-filter (following) are the two packages
  I always use in my projets. You create a `tables.py` module inside your applications
  where you define a bunch of tables using more or less the same methodology as with
  django-forms: For a `Book` model, Create a `BookTable` class, relate it with the model
  and, if needed override some of the columns it automatically generates. 
  
  You'll then be
  able to configure the data (queryset) of this table and add it your views context. What
  you'll get? The actual html table (with a nice style that can be configured if needed),
  free pagination and free column-header sorting. 

- django-filter_: This package is used to create filters for your data. It plays well with
  django-tables2 but you can use it to create filters for any kind of listing you want. It
  works similar to django-tables2: Create a ``filters.py`` module in your application and define
  the a `BookFilter` class there by relating it with the `Book` model, specifying the fields
  of the model you want to filter with and maybe override some of the default options.
  
  The `BookFilter` can be used to create a filter form in your template and then in your views
  pass to it the initial queryset along with `request.GET` (which will contain the filter values) 
  to return the filtered data (and usually pass it to the table). I've created a sample project that
  uses both django-tables2 and django-filters for you to use: https://github.com/spapas/django_table_filtering.
  Also, I've written an article which describes a technique for `automatically creating a filter-table view`_.
  
  
- django-crispy-forms_: The forms that are created by default by django-forms are very basic and not styled properly. 
  To overcome this, I always use this package. It actually has two modes: Using the crispy template filter and using
  the crispy template tag. Using the crispy template filter is very simple - just take a plain old django form and
  render it in your template like this `{{ form|crispy }}`. If the django-crispy-forms has been configured correctly
  (with the correct template pack) the form you'll get will be much nicer than the django-default one. This is completely
  automatic, you don't need to do anything else! 
  
  Now, if you have some special requirements from a form, for example
  multi-column rendering, adding tabs, accordions etc then you'll need to use the `{% crispy %}` template tag. To use this
  you must create the layout of your form in the form's costructor using the django-crispy-forms API. This may seem cumbersome
  at first (why not just create the form's layout in the django template) but using a class to define your form's layout
  has other advantages, for example all the form layout is in the actual form (not in the template) you can control 
  programatically the layout of the form (f.e display some fields only for administrators), you can use inheritance and 
  virtual methods to override how a form is rendered etc.

- django-extensions_: This is as swiss-army-knife of django tools. I use it *always* in my projects because of the `runserver_plus`
  and `shell_plus` commands. The first uses the `Werkzeug debugger with django`_ which makes django development an absolute joy!
  The second opens a *better* shell (your models and a bunch of django stuff are auto-imported, a better shall will be used if found etc). The
  `runserver_plus` and `shell_plus` alone will be more than enough for me to use this however it adds some more usefull management
  commands like: `admin_generator` to quickly create an admin.py for your app, `graph_models` to generate a graphviz dot file of your models,
  `update_permissions` to synchronize the list of permissions if you have added one to an existing model and `many, many others`_.
  
- django-auth-ldap_: This is the package you'll want to use if your organization uses LDAP. Just configure your LDAP server settings, 
  add the ldap authenticator and you'll be ready to go. Please notice that this package is a django wrapper of the python-ldap package 
  which actually provides the LDAP connection.

- django-autocomplete-light_: The best auto-complete library for django, especially after v3 was released (which greatly reduces the magic and
  uses normal CBVs for configuring the querysets). You will create
  an AutocompleteView for a model (similar to your other class based views) and then automatically use this view through a widget in the admin 
  or in your own forms. It is fully configurable (both the results and the selection templates), supports many to many fields, creating new instances
  and even autocompleteing django-taggit tags! If for some reason it seems that it is not working please keep in mind that you need to included
  jquery *and* `{{ form.media }}` to your templates.
  
- django-reversion_: A really important package for my projects. When it is configured properly (by adding a a reversion-middleware), it offers full auditing
  for all changes in the your model instances (and properly groups them in case of changes to multiple instances in a simple request). 
  It also saves a JSON representation
  of all the versions of an instance in your database. Keep in mind that this may increase your database size too much but if you need full auditing 
  then is is probably the best way to do it. I have written an article about `django model auditing`_ that discusses this package and django-simple-history
  (following) more.
  
- django-simple-history_: This package has similar capabilities with django-reversion - (auditing and keeping versions of models) with a very important
  difference: While django-reversion keeps a JSON representation of each version in the database (making querying very difficult), django-simple-history
  creates an extra, history table for each model instance you want to track and adds each change as a new row to that table. As can be understood this 
  will make the history table really huge but has the advantage that you can easily query for old values. I usually use django-reversion unless I know
  that I will need the history querying.
  
- xhtml2pdf_: This is the package I use for creating PDF's with django as I've alreadly discussed in the `PDFs in Django`_ article. You create a
  normal django template, add some styling to it and dump it to html. Notice that there's a django-xhtml2pdf_ project but has not been recently updated
  and after all as you can see in my article it is easy to just call xhtml2pdf directly. The xhtml2pdf library is actually a wrapper around the 
  excellent `reportlab`_ library which does the low-level pdf output.
  
  Notice that the xhtml2pdf library had some maintenance problems
  (that's why some people are suggesting other PDF solutions like WeasyPrint) however they seem to have passed now. Also, 
  I have found out that, at least for my needs (using Windows as my dev env), other soltuons are much inferior to xhtml2pdf. 
  I urge you to try xhtml2pdf first and only if you find that it does not cover your needs (and have asked
  me about your problem) try the other solutions.
  
- django-localflavor_: This package offers useful stuff for various countries, mainly form fields with the correct validation and lists of choices.
  For example, for my country (Greece) you'll get a GRPhoneNumberField, a GRPostalCodeField and a GRTaxNumberCodeField. Use it instead of re-implementing
  the behavior.
  
- django-compressor_: A package that combines and minifies your css and javascript (both files and line snippets) into static files.
  It has an online and an offline mode. For the online mode, when a request is done it will check if the compressed file exist and if not it will
  create it. This may lead to problems with permissions if your application server user cannot write to your static folders and also
  your users will see exceptions if for some reason you have included a file that cannot be found. For the 
  offline mode, you need to run a management command that will create the static files *while deploying* the applications - this mode is
  recommended because any missing files problems etc will be resolved while deploying the app.
  
- django-constance_: A simple package that enables you to add quick-configurable settings in your application. To change the settings.py file
  you need to edit a source text file and restart the application - for most installations this is a full re-deployment of the application. Fully
  re-deploying the app just to change a setting is not very good practice. That's where django-constance comes to help you. You can define some
  extra settings which can be changed through the django admin and their new value will be available immediately. Also you can configure where
  these settings will be saved. One option is the database but this is not recommended - instead you can use redis so that the settings values will be
  available much quicker!
  
- django-rq_: This app is a django wrapper for the rq_ library. I use it when I need asynchronous tasks (which is on almost all of my projects). More
  info can be found on the two articles I have writtten about django rq (`asynchronous tasks in django`_ and `django-rq redux`_).

- django-rules-light_: This package is one of the least known of the others I discuss here, when I need it, it is one of the most useful. This app
  allows you to define complex rules for doing actions on model instances. Each rule is a function that gets the user that wants to do the action
  and the object that the user wants to action on. The function returns True or False to allow or not allow the action. You can then use these in
  both your code to programatically check if the user can do the the action and your templates to decide what buttons and options you will display. 
  There are also various helper methods for CBVs that make everything easier.
  
  To properly understand the value of django-rules-light you need to have some more complex than usual action rules. For example if your actions
  for an object are view / edit and all your users can view and edit their own objects then you don't really need this package. However, if your administrators 
  can view all objects and your object can be finalized so no changes are allowed unless an administrator tries to change it then you'll greatly benefit
  from using it!
  
- django-generic-scaffold_: This is a package I have created that can be used to quickly (and DRYly) create CBVs for your models. I don't want to
  give access to the django-admin to non-technical users however sometimes I want to quickly create the required CBVs for them (list, detail, create, edit
  delete). Using django-generic-scaffold you can just create a scaffold which is related with a Model and all the views will be automagically created - 
  you only need to link them to your urls.py. The created CBVs are fully configurable by adding extra mixins or even changing the parent class of each CBV.




- easy-thumbnails
- django-allauth
- django-modeltranslation
- djangorestframework
- xlrd / xlwt

- django-sendfile
- django-taggit
- django-debug-toolbar
- raven
- python-memcached

.. _django-compressor: https://github.com/django-compressor/django-compressor/
.. _django-tables2: https://github.com/bradleyayers/django-tables2
.. _django-filter: https://github.com/carltongibson/django-filter
.. _django-crispy-forms: https://github.com/django-crispy-forms/django-crispy-forms
.. _django-simple-history: https://github.com/treyhunner/django-simple-history
.. _django-extensions: https://github.com/django-extensions/django-extensions
.. _django-auth-ldap: https://bitbucket.org/psagers/django-auth-ldap/
.. _django-autocomplete-light: https://github.com/yourlabs/django-autocomplete-light
.. _django-localflavor: https://github.com/django/django-localflavor
.. _django-reversion: https://github.com/etianen/django-reversion
.. _xhtml2pdf: https://github.com/xhtml2pdf/xhtml2pdf
.. _django-xhtml2pdf: https://github.com/chrisglass/django-xhtml2pdf
.. _django-constance: https://github.com/jazzband/django-constance
.. _django-rq: https://github.com/ui/django-rq
.. _django-generic-scaffold: https://github.com/spapas/django-generic-scaffold

.. _`a django cookiecutter`: https://github.com/spapas/cookiecutter-django-starter
.. _`Mailer Server`: https://github.com/spapas/mailer_server
.. _`Werkzeug debugger with django`: https://spapas.github.io/2016/06/07/django-werkzeug-debugger/
.. _`many, many others`: http://django-extensions.readthedocs.io/en/latest/command_extensions.html
.. _`automatically creating a filter-table view`: https://spapas.github.io/2015/10/05/django-dynamic-tables-similar-models/
.. _`django model auditing`: https://spapas.github.io/2015/01/21/django-model-auditing/
.. _`PDFs in Django`: https://spapas.github.io/2015/11/27/pdf-in-django/
.. _`reportlab`: http://www.reportlab.com
.. _rq: https://github.com/nvie/rq
.. _django-rules-light: https://github.com/yourlabs/django-rules-light

.. _`asynchronous tasks in django`: https://spapas.github.io/2015/01/27/async-tasks-with-django-rq/
.. _`django-rq redux`: https://spapas.github.io/2015/09/01/django-rq-redux/