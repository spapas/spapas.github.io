Django dynamic forms
####################

:date: 2013-12-24 14:20
:tags: django, python, forms
:category: django
:slug: django-dynamic-forms
:author: Serafeim Papastefanos
:summary: Creating dynamic (user generated) forms in django

.. contents::

Introduction
------------

To define a form in django, a developer has to create a class which extends 
``django.forms.Form``
and has  a number of attributes extending from ``django.forms.Field``. This makes 
it very easy for the developer to create static forms, but creating
dynamic forms whose fields can be changed depending on the data contributed by the
users of the application is not so obvious. 

Of course, some people may argue that they can do whatever
they want just by spitting html input tags to their templates, however this totally violates
DRY and any serious django developer would prefer to write MUMPS_ than creating
html dynamically.

The implementation I will present here had been developed for an old project: In that
project there was a number of services which could be edited dynamically by the
moderators. For each service, the moderators would generate a questionnaire to
get input from the users which would be defined  using JSON. When the users needed
to submit information for each service, a dynamic django form would be generated  
from this JSON and the answers would be saved to no-SQL database like MongoDB.

Describing a django form in JSON
--------------------------------

A JSON described django form is just an array of field JSON objects. Each field
object  has three required attributes: name which is the keyword of the field, label which is
how the label of the field and type which is the type of the input of that field. The
supported types are text, textarea, integer, radio, select, checkbox. Now, depending
on the type of the field, there could be also some more required attributes, for instace
text has a max_length attribute and select has a choices attribute (which is an array
of name/value objects). Also there are two optional attributes,
required with a default value of False and help_text with a default value of ''.

As you can understand these map one by one to the corresponding attributes of the
actual django form fields. An example containing a complete JSON described form 
is the following:


.. code:: 

    [
        {
            "name": "firstname",
            "label": "First Name",
            "type": "text",
            "max_length": 25,
            "required": 1
        },
        {
            "name": "lastname",
            "label": "Last Name",
            "type": "text",
            "max_length": 25,
            "required": 1
        },
        {
            "name": "smallcv",
            "label": "Small CV",
            "type": "textarea",
            "help_text": "Please insert a small CV"
        },
        {
            "name": "age",
            "label": "Age",
            "type": "integer",
            "max_value": 200,
            "min_value": 0
        },
        {
            "name": "marital_status",
            "label": "Marital Status",
            "type": "radio",
            "choices": [
                {"name": "Single", "value":"single"},
                {"name": "Married", "value":"married"},
                {"name": "Divorced", "value":"divorced"},
                {"name": "Widower", "value":"widower"}
            ]
        },
        {
            "name": "occupation",
            "label": "Occupation",
            "type": "select",
            "choices": [
                {"name": "Farmer", "value":"farmer"},
                {"name": "Engineer", "value":"engineer"},
                {"name": "Teacher", "value":"teacher"},
                {"name": "Office Clerk", "value":"office_clerk"},
                {"name": "Merchant", "value":"merchant"},
                {"name": "Unemployed", "value":"unemployed"},
                {"name": "Retired", "value":"retired"},
                {"name": "Other", "value":"other"}
            ]
        },
        {
            "name": "internet",
            "label": "Internet Access",
            "type": "checkbox"
        }
    ]


The above JSON string can be easily converted to an array of dictionaries with the following code:

.. code::

  import json
  fields=json.loads(json_fields)
  

Creating the form fields
------------------------

The most import part in the django dynamic form creation is to convert the above array
of field-describing dictionaries to actual objects of type ``django.forms.Field``.

To help with that I implemented a class named ``FieldHandler`` which gets an 
array of field dictionaries and after initialization will have an attribute named ``formfields`` which 
will be a dictionary with keys the names of each field an values the corresponding ``django.forms.Field`` objects. The implementation is as follows:

.. code::

    import django.forms
    
    class FieldHandler():
        formfields = {}
        def __init__(self, fields):
            for field in fields:
                options = self.get_options(field)
                f = getattr(self, "create_field_for_"+field['type'] )(field, options)
                self.formfields[field['name']] = f

        def get_options(self, field):
            options = {}
            options['label'] = field['label']
            options['help_text'] = field.get("help_text", None) 
            options['required'] = bool(field.get("required", 0) )
            return options

        def create_field_for_text(self, field, options):
            options['max_length'] = int(field.get("max_length", "20") )
            return django.forms.CharField(**options)

        def create_field_for_textarea(self, field, options):
            options['max_length'] = int(field.get("max_value", "9999") )
            return django.forms.CharField(widget=django.forms.Textarea, **options)

        def create_field_for_integer(self, field, options):
            options['max_value'] = int(field.get("max_value", "999999999") )
            options['min_value'] = int(field.get("min_value", "-999999999") )
            return django.forms.IntegerField(**options)

        def create_field_for_radio(self, field, options):
            options['choices'] = [ (c['value'], c['name'] ) for c in field['choices'] ]
            return django.forms.ChoiceField(widget=django.forms.RadioSelect,   **options)
        
        def create_field_for_select(self, field, options):
            options['choices']  = [ (c['value'], c['name'] ) for c in field['choices'] ]
            return django.forms.ChoiceField(  **options)

        def create_field_for_checkbox(self, field, options):
            return django.forms.BooleanField(widget=django.forms.CheckboxInput, **options)
            
As can be seen, in the ``__init__`` method, the ``get_options`` method is called first which
returns a dictionary with the common options (label, help_text, required). After that,
depending on the type of each field the correct method will be generated with
``getattr(self, "create_field_for_"+field['type'] )`` (so if type is text this
will return a reference to the create_field_for_text method) and then called passing
the field dictinary and the options returned from ``get_options``. Each one of
the ``create_field_for_xxx`` methods will extract the required (or optional)
attributes for the specific field type, update options and initialize the correct Field passing
the options as kwargs. Finally the formfields attribute will be updated with the name 
and Field object.


Creating the actual form
------------------------

To create the actual dynamic ``django.forms.Form`` I used the function ``get_form``
which receives a string with the json description, parses it to a python array,
creates the array of fields with the help of ``FieldHandler`` and then generates
the ``Form`` class with ``type`` passing it ``django.forms.Form`` as a parent
and the array of ``django.forms.Field`` from ``FieldHandler`` as attributes:

.. code::

  def get_form(jstr):
      fields=json.loads(jstr)
      fh = FieldHandler(fields)
      return type('DynaForm', (django.forms.Form,), fh.formfields )
    
    
Using the dynamic form
----------------------

The result of ``get_form`` can be used as a normal form class. As an example:

.. code::

    import dynaform 

    def dform(request):
        json_form = get_json_form_from_somewhere()
        form_class = dynaform.get_form(json_form)
        data = {}
        if request.method == 'POST':
            form = form_class(request.POST)  
            if form.is_valid():
                data = form.cleaned_data
        else:
            form = form_class()

        return render_to_response( "dform.html", {
            'form': form,  'data': data, 
        }, RequestContext(request) )

So, we have to get our JSON form description from somewhere (for instance
a field in a model) and then generate the form class with ``get_form``.
After that we follow the normal procedure of checking if the ``request.method``
is POST so we pass the POST data to the form and check if it is value or
we just create an empty form. As a result we just pass the data that was
read from the form to the view for presentation.




.. _MUMPS: http://thedailywtf.com/Articles/A_Case_of_the_MUMPS.aspx
