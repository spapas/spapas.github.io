My essential django package list
################################

:date: 2017-10-11 14:20
:tags: django, python
:category: django
:slug: essential-django-packages
:author: Serafeim Papastefanos
:summary: A list of packages (add-ons) that I use in most of my projects


In this article I'd like to present a list of django packages (add-ons) that I use
in most of my projects. I am using django for more than 5 years as my day to
day work tool to develop applications for the public sector organization I work for.
So please keep in mind that these packages are targeted to the "enterpripse"
audience and some things that target public (open access) web apps may be missing.

Some of these packages are included in
`a django cookiecutter`_ I am using to start new projects and also you can find
example usage of some of these packages in my `Mailer Server`_ project. 
I'll also be happy to answer any
questions about these, preferably in stackoverflow_ if the questions are fit for that site.

Finally, before going to the package list, notice that most of the following are django-related and I won't include any
generic python packages (with the exception of xhtml2pdf which I discuss later). There
are a bunch of python-generic packages that I usually use (xlrd, xlwt, requests, raven, unidecode,
database connectors etc) but these won't be discussed here.

.. contents:: :backlinks: none


Packages I use in all my projects
=================================

These packages are used more or less in all my projects - I just install them when I
create a new project (or create the project through the cookiecutter I mention above)/

django-tables2
--------------

django-tables2_, along with django-filter (following) are the two packages
I always use in my projets. You create a `tables.py` module inside your applications
where you define a bunch of tables using more or less the same methodology as with
django-forms: For a `Book` model, Create a `BookTable` class, relate it with the model
and, if needed override some of the columns it automatically generates. For example you
can configure a column that will behave as a link to a detail view of the book, a column
that will behave as a date (with the proper formatting) or even a column that will display 
a custom django template snippet.

You'll then be
able to configure the data (queryset) of this table and pass it your views context. Finally
use ``{% render_table table %}`` to actually display your table. What
you'll get? The actual html table (with a nice style that can be configured if needed),
free pagination and free column-header sorting. After you get the hang of it, you'll be
able to add tables for your models in a couple of minutes - this is DRY for me. It also 
offers some `class based views and mixins`_ for even more DRY adding tables to your views.

Finally, please notice that since version 1.8,
django-tables2 `supports exporting data`_ using tablib_, an old requirement of most users
of this library.


django-filter
-------------

django-filter_ is used to create filters for your data. It plays well with
django-tables2 but you can use it to create filters for any kind of listing you want. It
works similar to django-tables2: Create a ``filters.py`` module in your application and define
the a `BookFilter` class there by relating it with the `Book` model, specifying the fields
of the model you want to filter with and maybe override some of the default options. New versions
have some great built-in configuration functionality by customizing which method will be used for
filtering or even adding multiple filter methods - for example you could define your 
``BookFilter`` like this:

.. code::

    class BookFilter(django_filters.FilterSet):
        class Meta:
            model = Book  
            fields = { 
                'name': ['icontains'],
                'author__last_name': ['icontains', 'startswith'],
                'publication_date': ['year', 'month', ],
            }

which will give you the following filter form fields:

* an ilike '%value%' for the book name 
* an ilike '%value%' for the author name
* a like 'value%' for the author name
* a year(publication_date) = value for the publication_date
* a month(publication_date) = value for the publication_date

and their (AND) combinations!

  
The `BookFilter` can be used to create a filter form in your template and then in your views
pass to it the initial queryset along with `request.GET` (which will contain the filter values)
to return the filtered data (and usually pass it to the table). I've created a sample project that
uses both django-tables2 and django-filters for you to use: https://github.com/spapas/django_table_filtering.
Also, I've written an article which describes a technique for `automatically creating a filter-table view`_.

django-crispy-forms
-------------------

The forms that are created by default by django-forms are very basic and not styled properly.
To overcome this and have better styles for my forms, I always use django-crispy-forms_. It actually has two modes: Using the crispy template filter and using
the crispy template tag. Using the crispy template filter is very simple - just take a plain old django form and
render it in your template like this `{{ form|crispy }}`. If the django-crispy-forms has been configured correctly
(with the correct template pack) the form you'll get will be much nicer than the django-default one. This is completely
automatic, you don't need to do anything else!

Now, if you have some special requirements from a form, for example
multi-column rendering, adding tabs, accordions etc then you'll need to use the `{% crispy %}` template tag. To use this
you must create the layout of your form in the form's costructor using the FormHelper django-crispy-forms API. This may seem cumbersome
at first (why not just create the form's layout in the django template) but using a class to define your form's layout
has other advantages, for example all the form layout is in the actual form (not in the template) you can control
programatically the layout of the form (f.e display some fields only for administrators), you can use inheritance and
virtual methods to override how a form is rendered etc.

To help you understand how a ``FormHelper`` looks like, here's a form that is used to edit an access Card for visitors that
displays all fields horizontally inside a panel (I am using Bootstrap for all styling and layout purposes):

.. code:: 

    class CardForm(ModelForm):
        class Meta:
            model = Card
            fields = ['card_number', 'card_text', 'enabled']

        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.layout = Layout(
                Fieldset(
                    '',
                    HTML(u"""<div class="panel panel-primary">
                       <div class="panel-heading">
                           <h3 class="panel-title">Add card</h3>
                       </div>
                       <div class="panel-body">"""),
                    Div(
                       Div('card_number', css_class='col-md-4'),
                       Div('card_text', css_class='col-md-4'),
                       Div('enable',css_class='col-md-4'),
                       css_class='row'
                    ),
                ),

                FormActions(
                    Submit('submit', u'Save', css_class='btn btn-success'),
                    HTML(u"<a class='btn btn-primary' href='{% url \"card_list\" %}'>Return</a>" ),
                ),
                HTML(u"</div></div>"),
            )            
            
            super(CardForm, self).__init__(*args, **kwargs)
 
Notice that forms that will be rendered with a ``FormHelper`` actually contain their <form> tag (you don't need
to write it yourself like with plain django forms) so you have to define their method (post in this example) and submit button.



django-extensions
-----------------

django-extensions_ is a swiss-army-knife of django tools. I use it *always* in my projects because of the `runserver_plus`
and `shell_plus` commands. The first uses the `Werkzeug debugger with django`_ which makes django development an absolute joy 
(open a python shell wherever you want in your code and start writing commands)!
The second opens a *better* shell (your models and a bunch of django stuff are auto-imported, a better shall will be used if found etc). 

The
`runserver_plus` and `shell_plus` alone will be more than enough for me to use this however it adds some more usefull management
commands like: `admin_generator` to quickly create an admin.py for your app, `graph_models` to generate a graphviz dot file of your models,
`update_permissions` to synchronize the list of permissions if you have added one to an existing model and `many, many others`_. Take a look
at them and you'll probably find more useful things!

django-autocomplete-light
-------------------------

django-autocomplete-light_ is the best auto-complete library for django, especially after v3 was released (which greatly reduces the magic and
uses normal CBVs for configuring the querysets). You will create
an AutocompleteView for a model (similar to your other class based views) and then automatically use this view through a widget in the admin
or in your own forms. It is fully configurable (both the results and the selection templates), supports many to many fields, creating new instances
and even autocompleteing django-taggit tags! If for some reason it seems that it is not working please keep in mind that you need to includ
jquery *and* ``{{ form.media }}`` to your templates or else the required client side code won't be executed.

I think it is an essential for all cases because dropdowns with lots of choices have a very bad user experience - and the same is true with 
many to many fields (you could use the checkboxes widget to improve their behavior a little but you will have bad behavior when there are many
choices).

django-reversion
----------------

django-reversion_ is a really important package for my projects. When it is configured properly (by adding a a reversion-middleware), it offers full auditing
for all changes in the your model instances you select (and properly groups them in case of changes to multiple instances in a simple request).
It saves a JSON representation
of all the versions of an instance in your database. Keep in mind that this may increase your database size  but if you need full auditing
then is is probably the best way to do it. I have written an article about `django model auditing`_ that discusses this package and django-simple-history
(following) more.

django-compressor
-----------------

django-compressor_ is package that combines and minifies your css and javascript (both files and line snippets) into static files. There are
other tools for this but I have never used them since django-compressor satisfies my needs. Although I've 
`written about browserify`_ and friends from the node-js world I don't recommend using such tools in django to combine and minify your 
javascript and css *unless* you specifically require them. 

It has an online and an offline mode. For the online mode, when a request is done it will check if the compressed file exist and if not it will
create it. This may lead to problems with permissions if your application server user cannot write to your static folders and also
your users will see exceptions if for some reason you have included a file that cannot be found. For the
offline mode, you need to run a management command that will create the static files *while deploying* the applications - this mode is
recommended because any missing files problems etc will be resolved while deploying the app.


django-debug-toolbar
--------------------

django-debug-toolbar_: This is a well known package for debugging django apps that is always included in the development configuration of my projects.
It has various panels that help you debug your application but, at least for me, the most helpful is the one that displays you all SQL queries that
are executed for a page load. Because of how the django orm is working it will go on and follow all relations something that will lead to
hundreds of queries. For example, let's say that you have simple Book model with a foreign key to an Author model that has N instances in your
database. If you do a ``Book.objects.all()``
and want display the author name for each book in a template then you'll always do ``N+1`` queries to the database! This is really easy to miss because
in the django you'll just do ``{% for book in books %}{{ book.name}}, {{ book.author.name }}{% endif %}`` -- however the ``{{ book.author.name }}`` will go
on and do an extra SQL query!!! Such cases are easily resolved by using select_related_ (and prefetch_related_) but you must be sure to use select_related
for all your queries (and if you add some extra things to your template you must remember to also add them to your select_related clause for the query).

So, what I recommend before going to production is to visit all your pages using django-debug-toolbar and take a quick look at the number of SQL
queries. If you see something that does not make sense (for example you see more than 10 queries) then you'll need to think about the problem I just
mentioned. Please notice that this, at least for me, is not premature optimization - this is not actually optimization! This is about writing correct
code. Let's suppose that you could not use the django orm anymore and you had to use plain old SQL queries. Would you write ``SELECT * FROM books`` and
then for each row do another ``SELECT * FROM authors WHERE id=?`` passing the author of each book *or* do only ``select * from books b LEFT JOIN
authors a on b.author_id = a.id``?

Packages I use when I need their functionality
==============================================

The packages following are also essential to me but only when I need their functionality. I don't use them in all my projects
but, when I need the capabilities they offer then I will use these packages (and not some others). For example, if I need to
render PDFs in my applications then I will use the xhtml2pdf, if I need to login through LDAP I will use django-auth-ldap etc.

xhtml2pdf
---------

xhtml2pdf_ is the package I use for creating PDF's with django as I've alreadly discussed in the `PDFs in Django`_ article (this is not
a django-specific package like most others I discuss here but it plays really good with django). You create a
normal django template, add some styling to it and dump it to html. Notice that there's a django-xhtml2pdf_ project but has not been recently updated
and after all as you can see in my article it is easy to just call xhtml2pdf directly. The xhtml2pdf library is actually a wrapper around the
excellent `reportlab`_ library which does the low-level pdf output.

Notice that the xhtml2pdf library had some maintenance problems
(that's why some people are suggesting other PDF solutions like WeasyPrint) however they seem to have been fixed now. Also,
I have found out that, at least for my needs (using Windows as my development environment), other soltuons are much inferior to xhtml2pdf.
I urge you to try xhtml2pdf first and only if you find that it does not cover your needs (and have asked
me about your problem) try the other solutions.

django-auth-ldap
----------------

django-auth-ldap_ is the package you'll want to use if your organization uses LDAP (or Active Directory) and you want to use it for
logging in. Just configure your LDAP server settings,
add the ldap authenticator and you'll be ready to go. Please notice that this package is a django wrapper of the python-ldap package
which actually provides the LDAP connection.


django-localflavor
------------------

django-localflavor_ offers useful stuff for various countries, mainly form fields with the correct validation and lists of choices.
For example, for my country (Greece) you'll get a ``GRPhoneNumberField``, a ``GRPostalCodeField`` and a ``GRTaxNumberCodeField``. Use it instead of re-implementing
the behavior.

django-constance
----------------

django-constance_ is a simple package that enables you to add quick-configurable settings in your application. To change the settings.py file
you need to edit the source and restart the application - for most installations this is a full re-deployment of the application. Fully
re-deploying the app just to change a setting is not very good practice (depending on the setting of course but if it is a business setting
it usually should be done by business users and not by administrators). 

That's where django-constance comes to help you. You can define some
extra settings which can be changed through the django admin and their new value will be available immediately. Also you can configure where
these settings will be saved. One option is the database but this is not recommended - instead you can use redis so that the settings values will be
available much quicker!

django-rq
---------

django-rq_ is a django wrapper for the rq_ library. I use it when I need asynchronous tasks (which is on almost all of my projects). More
info can be found on the two articles I have writtten about django rq (`asynchronous tasks in django`_ and `django-rq redux`_).

django-rules-light
------------------

One of the least known packages from those I discuss here, django-rules-light_ is one of the most useful when is needed. This package
allows you to define complex rules for doing actions on model instances. Each rule is a function that gets the user that wants to do the action
and the object that the user wants to action on. The function returns True or False to allow or not allow the action. You can then use these in
both your code to programatically check if the user can do the the action and your templates to decide what buttons and options you will display.
There are also various helper methods for CBVs that make everything easier.

To properly understand the value of django-rules-light you need to have some more complex than usual action rules. For example if your actions
for an object are view / edit and all your users can view and edit their own objects then you don't really need this package. However, if your administrators
can view all objects and your object can be finalized so no changes are allowed unless an administrator tries to change it then you'll greatly benefit
from using it!

django-generic-scaffold
-----------------------

django-generic-scaffold_ is a package I have created that can be used to quickly (and DRYly) create CRUD CBVs for your models. I usually don't want to
give access to the django-admin to non-technical users however sometimes I want to quickly create the required CBVs for them (list, detail, create, edit
delete). Using django-generic-scaffold you can just create a scaffold which is related with a Model and all the views will be automagically created -
you only need to link them to your urls.py. The created CBVs are fully configurable by adding extra mixins or even changing the parent class of each CBV.

Notice that this package does not create any source files - instead all CBVs are created on-the-fly using ``type``. For example, to create CRUD CBVs for
a Book model you'll do this in scaffolding.py:

.. code::
    
    class BookCrudManager(CrudManager):
        model = models.Book
        prefix = 'books'
        
and then in your urls.py you'll just append the generated urls to your url list:

.. code::

    book_crud = BookCrudManager()
    urlpatterns += book_crud.get_url_patterns()
    
Now you can visit the corresponding views (for example /books or /bookscreate - depends on the prefix) to add/view/edit etc your books!


django-taggit
-------------

django-taggit_ is the library you'll want to use if you have to use tags with your models. A tag is a synonym for keyword, i.e adding some
words/phrases to your instances that are used to categorise and desribe em. The relation between your to-be-tagged-model and your tags is
many to many. To use it, you just add `tags = TaggableManager()` to your
model and you are ready to go! Of course it will need some more configuration to be included in django admin and django forms but thankfully,
autocomplete-lights can be `integrated with django-taggit`_!

django-sendfile
---------------

django-sendfile_ is a very important - at least to - me library. Sometimes, user uploaded files (media in django) should not be visible to all users
so you'll need to implement some access control through your django app. However, it is important to *not* serve these media files through your application
server (uwsi, gunicorn etc) but use a web server (nginx, apache ect) for serving them. This is needed because your application server's purpose is
not serving files from the disk - keep in mind that the application server usually has a specified amount of workers (usually analogous to the number
of CPUs of your server, for example 4 workers ) - think what will happen if some large media files are server through these workers to users with 
a slow connection! With 4 such concurrent connections your application won't be able to serve any other content!

So this package (along with the support of X-Sendfile from the web servers) helps you fulfill the above requirements:
It allowes you to check permissions to your media through your django application *but* then offload the serving of your media files to the web server. 
More info about
`django-sendfile can be found on this SO answer`_ but with a few words, with django-sendfile you create a view that checks if a file is allowed to be served
and, if yes, instruct the web server to actually serve that file by appending a specific header to the response.

django-reversion-compare
------------------------

django-reversion-compare_ is an addon to django-reversion. It allows you to compare two different versions of a model instance
and highlights their differences using various smart algorithms (so if you have a long text field you won't only see that these are different but
you'll also see where exactly they differ, with output similar to the one you get when using diff).

django-simple-history
---------------------

django-simple-history_ has similar capabilities with django-reversion - (auditing and keeping versions of models) with a very important
difference: While django-reversion keeps a JSON representation of each version in the database (making querying very difficult), django-simple-history
creates an extra, history table for each model instance you want to track and adds each change as a new row to that table. As can be understood this
will make the history table really huge but has the advantage that you can easily query for old values. I usually use django-reversion unless I know
that I will need the history querying.

django-import-export
--------------------

django-import-export_ can be used to enchance your models with mass import and export capabilities (from example from/to CSV).
You will add an ModelResource class that describes (and configures) how your Model should be imported/exported. The ModelResource class can
then be easily used in your views and, more importantly, it is integrated to the django-admin. I have to confess that I have not used django-import-export
for *importing* data because I prefer implementing my own views for that (to have better control over the whole process and because the data
I usually need to import does not usually map 1 to 1 with a model but I need to create more model instances etc). However I am using the export
capabilities of django-import-export in various projects with great success, especially the admin integration which easily fulfills the exporting
data capabilities of most users.

django-extra-views
------------------

Beyond django-forms, django supports a feature called Formsets_ which allows you to add/edit multiple object instances in
a single view (by displaying all instances one after the other). The classic request/response cycle of django is preserved in Formsets, so
your form instances will be submitted all together when you submit the form. The logic extension to the Formset is the ModelFormset_ i.e each form
in a Formset is a ModelForm and InlineFormSet_ where you have a Parent model that has a bunch of children and you are editing the Parent *and*
its children in a single Form. For example, you have a School and a Student model where each Student has a ForeignKey to School. The usual case
would be to edit the Student model and select her school (through a drop down or even-better if you use django-autocomplete-light through a proper
autocompelte widget). However, you may for some reason want to edit the School and display (and edit) the list of its Students -- that's where you'll
use an InlineFormSet!

The above features (Formsets, Modelformsets and Inlineformsets) are not supported natively by django CBVs -- that's where django-extra-views_ comes
to the foreground. You can use the corresponding CBVs of django-extra-views to support the multiple-form workflows described above. Using these CBVs
are more or less similar to using the good-old django FormView.

easy-thumbnails
---------------

easy-thumbnails_ is a great library if you want to support thumbnails. Actually, thumbnails is not 100% correct - this package can be used to
generate and manage various versions of your original images, for example you may have a small version of the image that will be used as a thumbnail,
a larger version that will be used in a gallery-carousel view and an even larger version (but not the original one which could be huge) that will be used when
the user clicks on the gallery to view a larger version of the image. To do that you define the image configurations you support in your settings.py and then 
you have access
to your thumbnails both in your templates and in your views. Notice that a specific thumbnail congfiguration for an image will be created only once since
the generated images are saved so each thumbnail will be generated on the first request it contains it and will be reused in the following such requests.


django-rest-framework
---------------------

django-rest-framework_ is definitely the best package for creating web APIs with django. I don't recommend using it if you want to create a quick JSON search
API (take a look at `django non-HTML responses`_) but if you want to go the SPA way or if you want to create multiple APIs for various models then
this is the way to go. Integrating it to your project will need some effort (that's why I don't recommend it for quick and dirty APIs) because you'll
need to create a serializers.py which will define the serializers (more or less the fields) for the models you'll want to expose through your API and
then create the views (or the viewsets which are families of views for example list, detail, delete, update, create) and add them to your urls.py. You'll
also need to configure authentication, authorization and probably filtering and pagination. This may seem like a lot of work but the result are
excellent - you'll get a full REST API supporting create, list, detail, update, delete for any complex configuration of your models.
You can take a look at a sample application in my `React tutorial`_ repository (yes this is a repository that has a tutorial for React and
friends but the back-end is in django and django-rest-framework).

django-rest-framework integrates nicely with django-filter (mentioned above) to re-use the filters you have created for your model listings
in your REST APIs - DRY at its best!

django-waffle
-------------

django-waffle_ is described as a feature flipper. What does this mean? Let's say that you want to control at will when a specific view will be enabled
- this is the library you'll want to use. Or you have developed a new feature and you want to give access to it only on a subset of users for a pilot run of
the feature - once again you should use django flipper. It offers a nice admin interface where you can configure the flags that will be used for the various
feature enabling/disabling (and if they are active or not) and various template tags and functions that you can use to test if the features should be activated
or not.

django-allauth
--------------

django-allauth_ should be used in two cases: When you want a *better* user registration workflow than the default (non-existant) one or you want
to integrate your application with an external OAuth provider (i.e allow your users to login through their facebook, google, twitter, github etc accounts). I
have mainly used this package for the first case and I can confirm that it works great and you can create as complex flows as you want (for example, in
one of my projects I have the following user registration-activation flow: A user registers using a custom form and using his email as username, he receives
an email with a confirmation link,
after he has confirmed his email he receivs a custom message to wait for his account activation and the administrators of the application are notified,
the administrators enable the new user's account after checking some things and only then he'll be able to log-in). One thing that must be noticed about
django-allauth is that it (in my opition) does not have very good documentation but there are lots of answers about `django-allauth in stackoverflow`_ and the source code
is very clear so you can always use the source as documentation for this package.


django-modeltranslation
-----------------------

The django-modeltranslation_ library is the library I recommend for when you want to have translations to your models. To use it
you add a translation.py file where you declare the models and their fields that should be translated. The, depending on which languages you have configured
in your settings.py after you run makemigrations and migrate you'll see that django-modeltranslation will have included extra fields to the database, each one
with the corresponding language name (for example if you have added a field ``name`` to the translations and have english and greek as language,
django-modeltranslation will add the fields ``name_en`` and ``name_el`` to your table). You can the edit the i18n fields (using forms or the django admin) and
depending on the current language of your site when you use ``name`` you'll get either ``name_el`` or ``name_en``.

django-widget-tweaks
--------------------

If for some reason you don't want to do django-crispy-forms, or you have a form in which you want to do a specific layout change but without
fully implementing the FormHelper then you can actually render the form in HTML and output the fields one by one. One thing that cannot
be done though is passing custom options to the rendered form field. When you do a ``{{ form.field }}`` to your template django will render
the form field using its default options - yes this can be overriden using `custom widgets`_ but I don't recommend it for example if you only
want to add a class to the rendered ``<input>``!

Instead, you can use django-widget-tweaks_ to pass some specific class names or attributes to
the rendered form fields - so if you use ``{{ form.field|add_class:"myclass" }}`` the rendered ``<input>`` will have a ``myclass`` css class.

django-simple-captcha
---------------------

Use django-simple-captcha_ to add (configurable) captchas to your django forms. This is a very simple package that does not have any requirements
beyond the Pillow library for the captcha image generator. The generated captchas are simple images with some added noise so it won't integrate
reCAPTCHA_ with which you may be more familiar. I deliberatly propose this package for captchas so you won't need to integrate with Google services. 

wagtail
-------

wagtail_ is a great django CMS. I use it when I need to create a CMS or I need to add CMS like capabilities to a project. It has many
capabilities, too many to be listed here. I urge you to try it if you need a CMS!


Conclusion
==========

The above packages should cover most of your django needs. I have listed only packages with good documentation, 
that have been recently updated
and work with new django versions and should be fairly easy to integrate with your projects. If you need anything more or want to take a general
look at some of the packages that have are availablie I recommend starting 
with the `django packages`_ site.

One important thing to notice here is that some of the above packages are not really complex and their functionality can be re-implemented
by you in a couple of hours. For example, you could replicate the functionality of django-constance by adding a config dict and
a couple of methods (and template tags) of storing and retrieving the keys of that dict with redis. Or add some custom clean methods to your 
forms instead of using the form fields from django-localflavor. Also, some of these packages have similar functionality and can be used (along
with a little custom code) to replicate the functionality of other packages, for exmaple instead of using django-waffle you could use 
django-constance to configure if the features should be enabled or disabled and django-rules-light to control if the users have access to the feature.
Also, you could probably use django-waffle for access control, i.e allow only admins to access a specific views. 

Please don't do this. This violates DRY and violates being disciplined. 
Each package has its purpose and being DRY means that you use it for its purpose, *not* re-implementing it and *not* re-using it for other purposes.
When somebody (or you after some months) sees that package in requirements or INSTALLED_APPS he will conclude that you are using it for
its intented purpose and thank you because you have saved him some time - please don't make him waste his time by needing to read your source code to understand 
any smart tricks or reinventing the wheel.




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
.. _django-taggit: https://github.com/alex/django-taggit
.. _django-sendfile: https://github.com/johnsensible/django-sendfile
.. _django-debug-toolbar: https://github.com/jazzband/django-debug-toolbar
.. _django-allauth: https://github.com/pennersr/django-allauth
.. _django-rest-framework: https://github.com/encode/django-rest-framework
.. _django-modeltranslation: https://github.com/deschler/django-modeltranslation
.. _django-waffle: https://github.com/jsocol/django-waffle
.. _django-import-export: https://github.com/django-import-export/django-import-export
.. _django-extra-views: https://github.com/AndrewIngram/django-extra-views
.. _django-reversion-compare: https://github.com/jedie/django-reversion-compare
.. _django-widget-tweaks: https://github.com/jazzband/django-widget-tweaks
.. _django-simple-captcha: https://github.com/mbi/django-simple-captcha
.. _wagtail: https://github.com/wagtail/wagtail

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
.. _`integrated with django-taggit`: https://django-autocomplete-light.readthedocs.io/en/master/taggit.html
.. _select_related: https://docs.djangoproject.com/en/1.11/ref/models/querysets/#select-related
.. _prefetch_related: https://docs.djangoproject.com/en/1.11/ref/models/querysets/#prefetch-related

.. _`django-sendfile can be found on this SO answer`: https://stackoverflow.com/q/7296642/119071
.. _`easy-thumbnails`: https://github.com/SmileyChris/easy-thumbnails
.. _`asynchronous tasks in django`: https://spapas.github.io/2015/01/27/async-tasks-with-django-rq/
.. _`django-rq redux`: https://spapas.github.io/2015/09/01/django-rq-redux/
.. _`django-allauth in stackoverflow`: https://stackoverflow.com/questions/tagged/django-allauth
.. _`django non-HTML responses`: https://spapas.github.io/2014/09/15/django-non-html-responses/
.. _`React tutorial`: https://github.com/spapas/react-tutorial
.. _Formsets: https://docs.djangoproject.com/en/1.11/topics/forms/formsets/
.. _InlineFormSet: https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/#inline-formsets
.. _ModelFormset: https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/#model-formsets
.. _tablib: https://github.com/kennethreitz/tablib
.. _`supports exporting data`: https://django-tables2.readthedocs.io/en/latest/pages/export.html
.. _`custom widgets`: https://docs.djangoproject.com/en/1.11/ref/forms/widgets/#base-widget-classes
.. _stackoverflow: https://stackoverflow.com
.. _reCAPTCHA: https://www.google.com/recaptcha/intro/
.. _`django packages`: https://djangopackages.org
.. _`class based views and mixins`: http://django-tables2.readthedocs.io/en/latest/pages/generic-mixins.html
.. _`written about browserify`: https://spapas.github.io/2015/05/27/using-browserify-watchify/