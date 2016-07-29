Django dynamic tables and filters for similar models
####################################################

:date: 2015-10-05 14:20
:tags: django, python, forms, tables
:category: django
:slug: django-dynamic-tables-similar-models
:author: Serafeim Papastefanos
:summary: Creating DRY and dynamic tables and forms for similar models in django

.. contents::

Introduction
------------

One of my favorite django apps is django-tables2_: It allows you to
easily create pagination and sorting enabled HTML tables to represent
your model data using the usual djangonic technique (similar to how
you `create ModelForms`_). I use it to almost all my projects to
represent the data, along with django-filter_ to create forms
to filter my model data. I've written `a nice SO answer`_ with
instructions on how to use django-filter along with django-tables2.
This article will describe a technique that allows you to generate
tables and filters for your models in the most DRY way! 

The problem we'll solve
-----------------------

The main tool django-tables2 offers is a template tag called ``render_table``
that gets an instance of a subclass of ``django_tables2.Table``
which contains a description of the table (columns, style etc) along
with a queryset with the table's data and outputs it to the page. A nice
extra feature of render_table is that you could pass it just a simple
django queryset and it will output it without the need to create the
custom Table class. So you can do something like {% render_table User.objects.all() %}
and get a quick output of your Users table.

In one of my projects I had three models that
were used for keeping a different type of business log in the database (for auditing reasons)
and was using the above feature to display these logs to the administrators, just by
creating a very simple ``ListView`` (a different one for each Log type) and using the
``render_table`` to display the data. So I'd created three views limilar to this:

.. code-block:: python

  class AuditLogListView(ListView):
    model = AuditLog
    context_object_name = 'logs'


which all used a single template that contained a line ``{% render_table logs %}`` to display
the table (the ``logs`` context variable contains the list/queryset of ``AuditLog`` s)
so ``render_table`` will just output that list in a page. Each view of course had a different
``model`` attribute. 

This was a nice DRY (but quick and dirty solution) that soon was not enough to fulfill the
needs of the administrators since they neeeded to have default sorting, filtering, hide
the primary key-id column etc. The obvious solution for that would be to just create three different
``Table`` subclasses that
would more or less have the same options with only their ``model`` attributte different. I didn't
like this solution that much since it seemed non-DRY to me and I would instead prefer to
create a generic ``Table`` (that wouldn't have a ``model`` attributte) and would just output
its data with the correct options -- so instead of three ``Table`` classes I'd like to create
just a single one with common options that would display its data (what ``render_table`` does).

Unfortunately, I couldn't find a solution to this, since when I ommited the ``model`` attribute
from the ``Table`` subclass nothing was outputed (there is no way to define fields to
display in a ``Table`` without also defining the model). An obvious (and DRY) resolution would be to create
a base ``Table`` subclass that would define the needed options and create three subclasses
that would inherit from this class and override only the ``model`` attribute. This unfortunately was not
possible becase `inheritance does not work well with django-tables2`_!

Furthermore, there's the extra hurdle of adding filtering to the above tables so that
the admin's would be able to quickly find a log message - if we wanted to use django-filter
we'd need again to create three different subclasses (one for each log model type)
of ``django_filter.FilterSet`` since
django-filter requires you to define the model for which the filter will be created!

One cool way to resolve such problems is to create your classes dynamically when
you need 'em. I've already described a way to `dynamically create forms in django
in a previous post <{filename}django-dynamic-forms.rst>`_. Below, I'll describe
a similar technique which can be used to create both dynamic tables and filters. Using
this methodology, you'll be able to add a new CBV that displays a table with
pagination, order and filtering for your model by just inheriting from a base class!


Adding the dynamic table
------------------------

To create the DRY CBV we'll use the SingleTableView_ (``django_tables2.SingleTableView``)
as a base and override its ``get_table_class`` method to dynamically create our table class
using ``type``.
Here's how it could be done using a mixin (notice that this mixin should be used in a
``SingleTableView`` to override its ``get_table_class`` method):

.. code-block:: python

  class AddTableMixin(object, ):
    table_pagination = {"per_page": 25}

    def get_table_class(self):
        def get_table_column(field):
            if isinstance(field, django.db.models.DateTimeField):
                return tables.DateColumn("d/m/Y H:i")
            else:
                return tables.Column()

        attrs = dict(
            (f.name, get_table_column(f)) for
            f in self.model._meta.fields if not f.name == 'id'
        )
        attrs['Meta'] = type('Meta', (), {'attrs':{"class":"table"}, "order_by": ("-created_on", ) } )
        klass = type('DTable', (tables.Table, ), attrs)

        return klass

Let's try to explain the ``get_table_class`` method: First of all, we've defined a local ``get_table_column``
function that will return a django-tables2 column depending on the field of the model. For example, in
our case I wanted to use a ``django_tables2.DateColumn`` with a specific format when a ``DateTimeField`` is
encountered and for all other model fields just use the stock ``Column``. You may add other overrides here,
for example add a ``TemplateColumn`` to properly render some data.

After that, we create a dictionary with all the attributes of the dynamic table model. 
The ``self.model`` field will contain
the model Class of this ``SingleTableView``, so using its ``_meta.fields`` will return 
the defined fields of that model. As we can see, I just use
a generator expression to create a tuple with the name of the field and its column type (using ``get_table_column``)
excluding the 'id' column. So, attrs will be a dictionary of field names and column types. Here you may
also exclude other columns you don't want to display.

The ``Meta`` class of this table is crated using ``type`` which creates a parentless class by 
defining all its attributes in a dictionary
and set it as the ``Meta`` key in the previously defined ``attrs`` dict. 
Finally, we create the actual ``django_tables2.Table`` subclass by
inheriting from it and passing the ``attrs`` dict. We'll see an example of what ``get_table_class`` returns later.

Creating a dynamic form for filtering
-------------------------------------

Let's create another mixin that could be used to create a dynamic ``django.Form`` subclass to the CBV:

.. code-block:: python

  class AddFormMixin(object, ):
    def define_form(self):
        def get_form_field_type(f):
            return forms.CharField(required=False)

        attrs = dict(
            (f, get_form_field_type(f)) for
            f in self.get_form_fields() )

        klass = type('DForm', (forms.Form, ), attrs)

        return klass

    def get_queryset(self):
        form_class = self.define_form()
        if self.request.GET:
            self.form = form_class(self.request.GET)
        else:
            self.form = form_class()

        qs = super(AddFormMixin, self).get_queryset()

        if self.form.data and self.form.is_valid():
            q_objects = Q()
            for f in self.get_form_fields():
                if self.form.cleaned_data.get(f):
                    q_objects &= Q(**{f+'__icontains':self.form.cleaned_data[f]})
                
            qs = qs.filter(q_objects)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(AddFormMixin, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx

The first method that will be called is the ``get_queryset`` method that will generate the dynamic form
using ``define_form``. This method has a ``get_form_field_type`` local function (similar to get_table_fields)
that can be used to override the types of the fields (or just fallback to a normal ``CharField``) and
then create the ``attrs`` dictionary and ``forms.Form`` subclass in a similar way as the ``Table`` subclass. Here,
we don't want to create a filter form from all fields of the model as we did on table, so instead
we'll use a ``get_form_fields`` (don't confuse it with the local ``get_form_field_type``)
method that returns the name of the fields that we want to
use in the filtering form and needs to be defined in each CBV -- the ``get_form_fields`` must
be defined in classes that use this mixin.

After defining the form, we need to check if there's anything to the ``GET`` dict -- since we are just filtering the
queryset we'd need to submit the form with a ``GET`` (and not a ``POST``). We see that if we have
data to our ``request.GET`` dictionary we'll instantiate the form using this data (or else we'll just
create an empty form). To do the actual filtering, we check if the form is valid and create a ``django.models.db.Q`` object
that is used to combine (by AND) the conditions. Each of the individual Q objects that will be combined
(``&=``)
to create the complete one will be created using the line ``Q(**{f+'__icontains':self.form.cleaned_data.get(f, '')})``
(where f will be the name of the field) which is a nice trick: It will create a 
dictionary of the form ``{'action__icontains': 'test text'}`` and then pass this as a keyword
argument to the Q (using the ``**`` mechanism), so ``Q`` will be called like 
``Q(action__icontains='test text')`` - this (using the ``**{key:val}`` trick) is 
the only way to pass dynamic kwargs to a function!

Finally, the queryset will be filtered using the combined ``Q`` object we just described.

Creating the dynamic CBV
------------------------

Using the above mixins, we can easily create a dynamic CBV with a table and a filter form only by inheriting 
from the mixins
and ``SingleTableView`` and defining the ``get_form_fields`` method:

.. code-block:: python

  class AuditLogListView(AddTableMixin, AddFormMixin, SingleTableView):
    model = AuditLog
    context_object_name = 'logs'

    def get_form_fields(self):
        return ('action','user__username', )

Let's suppose that the ``AuditLog`` is defined as following:

.. code-block:: python

  class AuditLog(models.Model):
    created_on = models.DateTimeField( auto_now_add=True, editable=False,)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False,)
    action = models.CharField(max_length=256, editable=False,)

Using the above ``AuditLogListView``, a dynamic table and a dynamic form will be automaticall created whenever the view is visited.
The ``Table`` class will be like this:

.. code-block:: python

  class DTable(tables.Table):
    created_on = tables.DateColumn("d/m/Y H:i")
    user = tables.Column()
    action = tables.Column()

    class Meta:
        attrs = {"class":"table"}
        order_by = ("-created_on", )

and the ``Form`` class like this:

.. code-block:: python

  class DForm(forms.Form):
    user__username = forms.CharField()
    action = forms.CharField()

An interesting thing to notice is that we can drill down to foreign keys (f.e. ``user__username``) to create more interesting filters. 
Also we could add some more
methods to be overriden by the implementing class beyond 
the ``get_form_fields``. For example, instead of using ``self.model._meta.fields``
to generate the fields of the table, we 
could instead use a ``get_table_fields`` (similar to the ``get_form_fields``) 
method that would be overriden in the implementing
classes (and even drill down on foreign keys to display more data on the table using accessors_).


Or, we could also define the form field types and lookups (instead of always using ``CharField`` and
``icontains`` ) in the ``get_form_fields`` -- similar to django-filter.

Please notice that instead of creating a django form instance for filtering, we could instead create a django-filter instance with
a similar methodology. However, I preferred to just use a normal django form because it makes the whole process more clear and removes
a level of abstraction (we just create a ``django.Form`` subclass while, if we used django-filter we'd need to create 
a django-filter subclass which would create a ``django.Form`` subclass)!

Conclusion
----------

Using the above technique we can quickly create a table and filter for a number of Models that all share
the same properties in the most DRY. This technique of course is useful only for quick CBVs that
are more or less the same and require little customization. Another interesting thing is that instead of
creating different ``SingleTableView`` s we could instead create a single CBV that will get the content type 
of the Model to be viewed as a parameter and retrieve the model (and queryset) from the content type - so
we could have a single CBV for all our table/filtering views !


.. _MUMPS: http://thedailywtf.com/Articles/A_Case_of_the_MUMPS.aspx
.. _django-tables2: https://github.com/bradleyayers/django-tables2
.. _`create ModelForms`: https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#modelform
.. _django-filter: https://github.com/alex/django-filter
.. _`a nice SO answer`: http://stackoverflow.com/questions/13611741/django-tables-column-filtering/15129259#15129259
.. _`inheritance does not work well with django-tables2`: http://stackoverflow.com/questions/16696066/django-tables2-dynamically-adding-columns-to-table-not-adding-attrs-to-table/16741665#16741665
.. _SingleTableView: http://django-tables2.readthedocs.org/en/latest/pages/generic-mixins.html?highlight=singletableview
.. _accessors: http://django-tables2.readthedocs.org/en/latest/pages/accessors.html