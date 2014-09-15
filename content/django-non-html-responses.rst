Django non-HTML responses
#########################

:date: 2014-09-15 14:20
:tags: django, python, cbv, class-based-views
:category: django
:slug: django-non-html-responses
:author: Serafeim Papastefanos
:summary: Implementing non-HTML (for instance CSV, XSL, etc) responses with Django and Class Based Views

.. contents::

Introduction
------------

I have already written about the many advantages (DRY!) of using `CBVs in a previous article. <|filename|django-generic-formview.rst>`_
In this article I will present the correct (pythonic) way to allow a normal CBV to return non-HTML responses, like PDF, CSV, XSL etc.


How are CBVs rendered
---------------------

Before proceeding, we need to understand how CBVs are rendered. By walking through the
class hierarchy in the `CBV inspector`_, we can see that
all the normal Django CBVs (DetailView, CreateView, TemplateView etc) are using a mixin
named TemplateResponseMixin_ which defines a method named ``render_to_response``. This
is the method that is used for rendering the output of the Views. Let's take a look at
`how it is defined`_ (I'll remove the comments):

.. code-block:: python

  class TemplateResponseMixin(object):
    template_name = None
    response_class = TemplateResponse
    content_type = None

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )

    def get_template_names(self):
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name]


This method will try to find out which html template should be used to render the View
(using the  ``get_template_names`` method and template_name attribute of the mixin) and
then render this view by instantiating an instance of the ``TemplateResponse`` class
(as defined in the ``response_class`` attribute)
and passing the request, template, context and other response_args to it.

The TemplateResponse_ class which is instantiated in the ``render_to_response`` method
inherits from a normal ``HttpResponse`` and is used to render
the template passed to it as a parameter.


Rendering to non-HTML
---------------------

From the previous discussion we can conclude that if your non-HTML response *needs*
a template then you just need to create a subclass of ``TemplateResponse`` and
assign it to the ``response_class`` attribute (and also change the ``content_type``
attribute). On the other hand, if your non-HTML respond does not need a template
to be rendered then you have to override ``render_to_response`` completely
(since the template parameter does not need to be passed now) and either define
a subclass of HttpResponse or do the rendering in the render_to_response.

Since almost always you won't need a template to create a non-HTML view and because
I believe that the solution is DRY-enough by implementing the rendering code to
the ``render_to_response`` method (*without* subclassing ``HttpResponse``) I will
implement a mixin that does exactly that.

Subclassing ``HttpResponse`` will not make our design more DRY because for every
subclass of ``HttpResponse`` the ``render_to_response`` method would also need to
be modified (by subclassing ``TemplateResponseMixin) to instantiate the subclass of ``HttpResponse`` with the correct parameters.
For instance, the existing ``TemplateResponseMixin`` cannot be used if the subclass
of ``HttpResponse`` does not take a template as a parameter (solutions like
passing None to the template parameter are signals of bad design).

In any case, changing just the ``render_to_response`` method using a Mixin is in my opinion the best solution
to the above problem.
A Mixin_ is a simple class that can be used to extend other classes either by overriding functionality of the base class or
by adding extra features. Django CBVs use various mixins_ to extend the base Views and add functionality.


A non-HTML mixin
----------------

So, a basic skeleton for our mixin would be something like this:

.. code-block:: python

  class NonHtmlResponseMixin(object):
      def render_to_response(self, context, **response_kwargs):
          response = HttpResponse(content_type='text/plain')
          response.write( "Hello, world" )
          return response


The previous mixin overrides the render_to_response method to just return the text "Hello, world". For instance
we could define the following class:

.. code-block:: python

  class DummyTextResponseView(NonHtmlResponseMixin, TemplateView,):
    pass

which can be added as a route to ``urls.py`` (using the ``as_view`` method) and will always return the "Hello, world" text.

Here's something more complicated: A Mixin that can be used along with a DetailView and will output the properties of the
object as text:

.. code-block:: python

  class TextPropertiesResponseMixin(object):
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        o = self.get_object()
        o._meta.fields
        for f in o._meta.fields:
            response.write (u'{0}: {1}\n'.format(f.name,  unicode(o.__dict__.get(f.name)) ) )
        return response

and can be used like this

.. code-block:: python

  class TextPropertiesDetailView(TextPropertiesResponseMixin, FooDetailView,):
    pass

The above mixin will use the get_object() method of the DetailView to get the object and then output
it as text. We can create similar mixins that will integrate with other types of CBVs, for instance
to export a ListView as an CSV or generate an png from a DetailView of an Image file.


A more complex example
----------------------
The previous examples all built upon an existing view (either a TemplateView, a DetailView or a ListView).
However, an existing view that will fit our requirements won't always be available. For instance,
sometimes I want to export data from my database using a raw SQL query. Also I'd like to be able to easily
export this data as csv or excel.

First of all, we need to define a view that will inherit from ``View`` and export the data as a CSV:

.. code-block:: python

  import unicodecsv
  from django.db import connection
  from django.views.generic import View

  class CsvRawSqlExportView(View, ):
    sql = 'select 1+1'
    headers = ['res']
    params = []

    def get(self, request):
        def generate_data(cursor):
            for row in cursor.fetchall():
                yield row

        cursor = connection.cursor()
        cursor.execute(self.sql, self.params)
        generator = generate_data(cursor)
        return self.render_to_response(generator)

    def render_to_response(self, generator, **response_kwargs):
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=export.csv'
        w = unicodecsv.writer(response, encoding='utf-8')
        w.writerow(self.headers)
        for row in generator:
            w.writerow(row)

        return response

The above View has three attributes:
* sql, which is a string with the raw sql that will be executed
* headers, which is an array with the names of each header of the resulting data
* params, which is an array with parameters that may need to be passed to the query

The ``get`` method executes the query and passes the result to ``render_to_response``
using a generator.  The ``render_to_response`` method instantiates an HttpResponse
object with the correct attributes and writes the CSV to the response object using unicodecsv.

We can now quickly create a route that will export data from the users table:

.. code-block:: python

    url(
        r'^raw_export_users/$',  
        views.CsvRawSqlExportView.as_view(
            sql='select id, username from auth_user', 
            headers=['id', 'username']
        ) , 
        name='raw_export_users' 
    ),


If instead of CSV we wanted to export to XLS (using xlwt), we'd just need to create a Mixin:

.. code-block:: python

  class XlsRawSqlResponseMixin(object):
    def render_to_response(self, generator, **response_kwargs):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=export.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("data")

        for j,c in enumerate(self.headers):
                ws.write(0,j,c)

        for i,row in enumerate(generator):
            for j,c in enumerate(row):
                ws.write(i+1,j,c)

        wb.save(response)
        return response

and create a View that inherits from ``CsvRawSqlExportView`` and uses the above mixin:

.. code-block:: python

  class XlsRawSqlExportView( XlsRawSqlResponseMixin, CsvRawSqlExportView ):
    pass

and route to that view to get the XLS:

.. code-block:: python

    url(
        r'^raw_export_users/$', 
        views.XlsRawSqlExportView.as_view(
            sql='select id, username from auth_user', 
            headers=['id', 'username']),
        name='raw_export_users' 
    ),


Conclusion
----------

Using the above techniques we can define CBVs that will output their content in various content types
beyond HTML. This will help us write write clean and DRY code.

.. _`django user profile`: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model
.. _mixins: https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
.. _Mixin: http://stackoverflow.com/questions/533631/what-is-a-mixin-and-why-are-they-useful
.. _TemplateResponse: https://github.com/django/django/blob/master/django/template/response.py
.. _TemplateResponseMixin: http://ccbv.co.uk/projects/Django/1.7/django.views.generic.base/TemplateResponseMixin/
.. _Template: https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.Template
.. _`CBV inspector`: http://ccbv.co.uk/
.. _`how it is defined`: http://ccbv.co.uk/projects/Django/1.7/django.views.generic.base/TemplateResponseMixin/