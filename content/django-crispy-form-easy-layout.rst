Quick and easy layout of django forms using django-crispy-forms and django-widget-tweaks
########################################################################################

:date: 2020-03-18 11:20
:tags: django, forms, django-crispy-forms, django-widget-tweaks
:category: django
:slug: django-crispy-form-quick-easy-layout
:author: Serafeim Papastefanos
:summary: How to easily layout your django-crispy-forms forms

One of the first problems you have when you want to create a traditional HTML django site (i.e
not an SPA one) is how to properly and beautifully layout your forms. In this small article I'll
talk about two very useful django packages that will help you have great layouts in your forms:
`django-crispy-forms`_  and `django-widget-tweaks`_.

django-crispy-forms
-------------------

The django-crispy-forms django package is a great way to properly format your forms. If you don't
already use it I totally recommend to check it out; it's very useful and you'll definitely love it 
if you are a heavy django forms user. It helps you properly layout your forms either implicitly or 
explicitly.

For explicitly laying out your forms you should add a ``FormHelper`` to your django form class and
use the ``{% crispy %}`` template tag. You can use this to explicitly define your form layout with
as much detail as you want since you have full control. I won't go into more details about this since it's 
`explained thoroughly in the docs`_.

For implicitly laying out your forms, you will just use the ``|crispy`` template filter. This gets a 
normal django form (without any modifications) and converts it to a crispy form based on the `template pack`_
you are using. This works great for many situations however sometimes you'll need to have more control 
over this without going to the extra effort to add a complete layout to each of your forms using 
the ``FormHelper``.

So how do you resolve this? Enter the ``|as_crispy_field`` template filter. To use that filter you'll need
to add the ``{% load crispy_forms_tags %}`` lines to your template and then you can pass any one of your
form's fields to it so it will be properly "crispified"! Let's see a quick example of adding the fields of
a form in a ``<div class='col-md-6'>`` so they will be in two columns (using bootstrap): 

.. code:: 

  <form class='form' method="POST">
      <div class='row'>
          {% for field in form %}
              <div class='col-md-6'>
                {{ field|as_crispy_field }}
              </div>
          {% endfor %}
          {% csrf_token %}
      </div>
      <input class='btn btn-primary' type='submit'>
  </form>

So the above code enumerates all form fields and uses the ``|as_crispy_field`` to properly add the
crispified information to it. If you want to re-use the above two column layout in multiple forms and
be more dry you can create a template snippet and ``{% include %}`` it in the part of your code you
want the form to be rendered.


django-widget-tweaks
--------------------

Using the ``as_crispy_field`` is excellent however sometimes you may need even more control
of your for fields, for example add an extra class (like ``form-control-lg``) to your form controls.
The answer to this is the django-widget-tweaks package: It enables you to easily modify form
fields by adding classes, attributes etc to them from within your django templates. 

To use it you need to add a ``{% load widget_tweaks %}`` to your templates. Then you'll be 
able to use the ``|add_class`` form field to add a class to your form field. For example the
previous example can be modified like this to have smaller controls:

.. code:: 

  <form class='form' method="POST">
      <div class='row'>
          {% for field in form %}
              <div class='col-md-6'>
                {{ field|add_class:"form-control-sm"|as_crispy_field }}
              </div>
          {% endfor %}
          {% csrf_token %}
      </div>
      <input class='btn btn-primary' type='submit'>
  </form>

Please notice that I use both ``add_class`` and ``as_crispy_fields`` together; notice the
order, the ``add_class`` needs to be *before* the ``as_crispy_field`` or you'll get an error. This 
way the django form field will have the ``form-control-sm`` class *and* then be rendered as a 
crispy field.

Let's now suppose that you need to more control over your fields. For example you need to add a class
only to your select fields or even only to a particular field (depending on its name). To do that
you can use the ``name`` and ``field.widget.input_type`` attributes of each for field. So, to make
select fields smaller and with a ``warning`` background and fields that have a name of ``name`` 
or ``year`` larger you can use something like this:

.. code:: 

  <form class='form' method="POST">
      <div class='row'>
          {% for field in form %}
            {% if field.name == 'name' or field.name == 'year' %}
                {{ field|add_class:"form-control-lg"|as_crispy_field }}
            {% elif field.field.widget.input_type == 'select' %}
                {{ field|add_class:"form-control-sm"|add_class:"bg-warning"|as_crispy_field }}
            {% else %}
                {{ field|as_crispy_field }}
            {% endif %}
          {% endfor %}
          {% csrf_token %}
      </div>
      <input class='btn btn-primary' type='submit'>
  </form>

Using the above techniques you should be able to quickly layout and format your form fields with
much control! If you need something more I recommend going the ``FormLayout`` route I mentioned 
in the beginning.

.. _`django-crispy-forms`: https://github.com/django-crispy-forms/django-crispy-forms
.. _`django-widget-tweaks`: https://github.com/jazzband/django-widget-tweaks
.. _`explained thoroughly in the docs`: https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html#crispy-tag-with-forms
.. _`template pack`: https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs