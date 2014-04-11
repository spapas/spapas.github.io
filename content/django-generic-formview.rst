Django generic FormViews for objects
####################################

:date: 2014-04-11 10:23
:tags: django, python, cbv
:category: django
:slug: django-generic-formviews-for-objects
:author: Serafeim Papastefanos
:summary: An implementation & discussion of generic FormViews for acting on model instances

.. contents::

Introduction
------------

We recently needed to create a number of views for changing the status of an Application model instance for our organization.
An Application model instance can be filled and then cancelled, submitted, acceptted etc - for each of these status changes a form should be
presented to the user. When the user submits the form the status of the Application will be changed.

To implement the above requirement we created a generic FormView that acts on the specific model instance. This
used two basic CBV components: The ``FormView`` for the form manipulation and the ``SingleObjectMixing`` for the
object handling.

Django `Class Based Views`_ (CBVs) can be used to create reusable Views using normal class inheritance. Most
people use the well-known ``CreateView``, ``UpdateView``, ``DetailView`` and ``ListView``, however, as we
will see below, the ``FormView`` will help us write DRY code.

I have to notice here that an invaluable tool to help you understanding CBVs is the `CBV inspector`_ which
has a nice web interface for browsing the CBV hierarchies, attributes and methods.

A quick introduction to the ``FormView``
----------------------------------------

A simple ``FormView`` can be defined like this (`CBV FormView`_):

.. code:: 

  class MyFormView(FormView):
    form_class = forms.MyFormView
    template_name = 'my_template.html'
    
The above can be used in urls.py like this:

.. code:: 
  
  urlpatterns = patterns('',
    url(r'^my_formview/$', views.MyFormView.as_view() , name='my_formview' ),

This will present a form to the user when he visits the ``my_formview``  url -- however this form won't do anything. To allow
the form to actually do something when it's been submitted we need to override the ``form_valid`` method.
    
.. code:: 
    
    def form_valid(self, form):
        value = form.cleaned_data['value']
        messages.info(self.request, "MyForm submitted with value {0}!".format(value) )
        return HttpResponseRedirect( reverse('my_formview') )
    

As you can see the submitted form is passed in the method and can be used to receive its ``cleaned_data``. The ``FormView``
has various other options for instance a ``form_invalid`` method, an ``initial`` attribute to set the initial values for the form etc.

A quick introduction to the ``SingleObjectMixin``
-------------------------------------------------
    
A ``SingleObjectMixin`` adds a number of attributes & methods to a view that can be used for object manipulation. The
most important ones is the ``model`` and ``queryset`` attributes and the ``get_queryset`` and ``get_object()``. To use
the ``SingleObjectMixin`` in your CBV just add it to the list of the classes to inherit from and define either the 
``model`` or the ``queryset`` attribute. After that you may pass a ``pk`` parameter to your view and you will get an
``object`` context variable in the template with the selected object!


Being generic and DRY
---------------------

We can more or less now understand how we should use ``FormView`` and ``SingleObjectMixin`` to generate our 
generic ``FormView`` for acting on objects: Our ``FormView`` should *get* the object using the ``SingleObjectMixin``
and change it when the form is submitted using the values from the form. A first implementation would be the following:

.. code:: 

  class GenericObjectFormView1(FormView, SingleObjectMixin):
        
      def form_valid(self, form):
          obj = self.get_object()
          obj.change_status(form)
          return HttpResponseRedirect( obj.get_absolute_url() )


So our ``GenericObjectFormView1`` class inherits from ``FormView`` and ``SingleObjectMixin``. The only thing that we have
to assure is that the Model we want to act on needs to implement a ``change_status`` method which gets the ``form`` and
changes the status of that object based on its value. For instance, two implementations can be the following:


.. code:: 

  class CancelObjectFormView(GenericObjectFormView1):
      template_name = 'cancel.html'
      form_class = forms.CancelForm
      model = models.Application

  class SubmitObjectFormView(GenericObjectFormView1):
      template_name = 'submit.html'
      form_class = forms.SubmitForm
      model = models.Application    


Being more generic and DRY
--------------------------

The previous implementation has two problems: 

* What happens if the status of the object should not be changed even if the form *is* valid?
* We shouldn't need to create a new template for every new ``GenericObjectFormView`` since all these templates will just output the object information, ask a question for the status change and output the form.

Let's write a new version of our GenericObjectFormView that actually resolves these:


.. code:: 

  class GenericObjectFormView2(FormView, SingleObjectMixin):
      template_name = 'generic_formview.html'
      ok_message = ''
      not_ok_message = ''
      title = ''
      question =''
    
      def form_valid(self, form):
          obj = self.get_object()
          r = obj.change_status(form)
          if r:
              messages.info(self.request, self.yes_message)
          else:
              messages.info(self.request, self.not_ok_message)
          return HttpResponseRedirect( obj.get_absolute_url() )

      def get_context_data(self, **kwargs):
          context = super(GenericYesNoFormView, self).get_context_data(**kwargs)
          context['title'] = self.title
          context['question'] = self.question
          return context    


The above adds an ok and not ok message which will be outputed if the status can or cannot be changed. To accomplish this,
the ``change_status`` method should now return a boolean value to mark if the action was ok or not. Also, a generic template
will now be used. This template has two placeholders: One for the title of the page (``title`` attribute) and one for the
question asked to the user (``question`` attribute). Now we can use it like this:

.. code:: 

  class CancelObjectFormView(GenericObjectFormView2):
      form_class = forms.CancelForm
      model = models.Application
      ok_message = 'Cancel success!'
      not_ok_message = 'Not able to cancel!'
      title = 'Cancel an object'
      question = 'Do you want to cancel this object?'

  class SubmitObjectFormView(GenericObjectFormView2):
      form_class = forms.SubmitForm
      model = models.Application   
      ok_message = 'Submit  ok'
      not_ok_message = 'Cannot submit!'
      title = 'Submit an object'
      question ='Do you want to submit this object?'    




Other options
-------------
We've just got a glimpse of how we can use CBVs to increase the DRYness of our Django applications. There are various
extra things that we can add to our ``GenericObjectFormView2`` as attributes which will be defined by inheriting
classes. Some ideas is to check if the current user actually has access to modify the object (hint: override the
``get_object`` method of ``SingleObjectMixin``) or render the form diffirently depending on the current user (hint:
override the ``get_form_kwargs`` method of ``FormView``).

    
.. _`Class Based Views`: https://docs.djangoproject.com/en/1.6/topics/class-based-views/
.. _mixins: https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
.. _`CBV inspector`: http://ccbv.co.uk/
.. _`CBV FormView`: http://ccbv.co.uk/projects/Django/1.6/django.views.generic.edit/FormView/