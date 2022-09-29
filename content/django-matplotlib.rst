Using matplotlib to generate graphs in Django
#############################################

:date: 2021-02-08 14:55
:tags: django, matplotlib, python
:category: django
:slug: django-matplotlib
:author: Serafeim Papastefanos
:summary: How to use the matplotlib library to generate server-side graphs with Django 

Nowadays the most common way to generate graphs in your Django apps (or web apps in general) is to 
pass the data as json to the page and use a javascript lib. The big advantage these javascript libs
offer is interactivity: You can hover over points to see their values making studying the graph much
easier.

Yet, there are times where you need some simple (or not so simple) graphs and don't care about 
offering interactivity through javascript nor you want to mess with javascript at all. For these cases
you can generate the graphs server-side using django and the `matplotlib`_ plot library.

matplotlib is a very popular library in the scientific cycles. It can be used to create more or less
any kind of graph and has unlimited capabilities! I won't go into much detail about matplotlib here 
because the subject is huge but I recommend you to take a look at the `comprehensive tutorials`_ on its
homepage.

To install matplotlib on unix you need to do a ``pip install matplotlib`` while, for windows,
you can download the proper ready-made binaries from the `Unofficial Windows Binaries for Python Extension Packages`_ 
site that offers pre-compiled versions of almost all python packages! Just make sure to download the correct version 
for your python version and architecture (32bit or 64bit). After you've downloaded the file you can install it 
for your project using something like ``pip install matplotlib-3.3.4-cp38-cp38-win32`` from inside your virtual environment.

Before actually creating a graph I recommend playing a bit with matplotlib to understand the basic concepts. Start a django shell
and do the following:

.. code::

  >>> import matplotlib.pyplot as plt
  >>> fig, ax = plt.subplots()
  >>> ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
  [<matplotlib.lines.Line2D object at 0x0FBF5F58>]
  >>> fig.show()

The above should open a window and display the graph. This works fine on Window 10 with python 3.8 and matplotlib 3.3.4 but I 
can't guarantee other versions. If however ``fig.show()`` shows an error or does not display the graph, you can just do something like:

.. code::

  >>> fig.savefig('test')

that will output the figure in a file named ``test.png`` which you can the view. Please notice that the above are with the default
options; there are various ways that matplotlib can be configured. 

In any case, after you've played a bit with the shell and generate a nice figure (take a look at the `matplotlib examples`_ for 
inspiration) you are ready to integrate matplotlib with Django!

I can think of two ways which you can integrate matplotlib with Django:

* Use a special view that would render the graph and just return a PNG object. Use a normal ``<img>`` element pointing to that view in your template.
* Put the graph in the context of a normal django view encoded as a base64 object and use a special ``<img>`` with an ``src`` attribute of ``data:image/png;base64,{{ graph }}`` to actually embed the image in the template!

I prefer the second approach because it's much more flexible since you don't need to create a different Django view for each graph you
want to generate. For this reason I will explain this approach right now and give you some hints if you need to follow the dedicated 
graph view approach.

Our view should:

* Generate the graph
* Save it in a BytesIO object
* Convert that BytesIO to base64
* Put the string value of the base64 encoded graph to the template

Then the template will just output that base64 value using the special img we mentioned above.

Here's a snippet of a view that does exactly this:

.. code::

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import io, base64
    from django.db.models.functions import TruncDay
    from matplotlib.ticker import LinearLocator

    class SampleListView(ListView):
      model = Sample

      def get_context_data(self, **kwargs):
        
        by_days = get_queryset().annotate(day=TruncDay('created_on')).values('day').annotate(c=Count('id')).order_by('day')
        days = [x['day'] for x in by_days]
        counts = [x['c'] for x in by_days]

        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(days, counts, '--bo')
        
        fig.autofmt_xdate()
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.set_title('By date')
        ax.set_ylabel("Count")
        ax.set_xlabel("Date")
        ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
        ax.yaxis.set_minor_locator(LinearLocator(25))

        flike = io.BytesIO()
        fig.savefig(flike)
        b64 = base64.b64encode(flike.getvalue()).decode()
        context['chart'] = b64
        return context

Please notice that after importing ``matplotlib`` I'm using the ``matplotlib.use('Agg')`` command to use
the ``Agg`` backend. You can `learn more about backends here`_, but it should be sufficient for now to 
know that using the ``Agg`` you'll be able to save your graphs in png.

The above code uses some Django ORM trickery to group values by their created_on day value and then 
assings the days and counts to two arrays (``days``, ``counts``). It then creates a new empty graph
with a specific size using ``fig, ax = plt.subplots(figsize=(10,4))`` and plots the data with some
fancy styles with ``ax.plot(days, counts, '--bo')``. After that it sets various options in the graph
like the labels, grid etc. 

The save and convert to base64 part follows: A new file like object is created using ``io.BytesIO()`` and
the figure is saved there (``fig.savefig(flike)``). Then it is converted to a base64 string using the 
``b64 = base64.b64encode(flike.getvalue()).decode()``. Finally it is just passed to the context of 
the template as ``chart``.

Now, inside the template I've got the following line:

.. code::

  <img src='data:image/png;base64,{{ chart }}'>

This will include the data of the chart inline and display it as a png image. If you've followed along 
you should be able to see the graph when you load that view!

If instead of including the graphs in your normal django template views you want to use a dedicated 
graph-generating view, you can follow my 
`Django non-HTML responses tutorial <{filename}django-non-html-responses.rst>`_. You could then 
modify the ``render_to_response`` method of your view like this:

.. code:: 

  def render_to_response(self, generator, **response_kwargs):
      response = HttpResponse(content_type='image/png')
      
      fig, ax = plt.subplots(figsize=(10,4))
      # fill the report here

      fig.savefig(response)
      return response

Since ``response`` is a file-like object you can save your graph directly there!

.. _`comprehensive tutorials`: https://matplotlib.org/tutorials/index.html
.. _matplotlib: https://matplotlib.org/
.. _`Unofficial Windows Binaries for Python Extension Packages`: https://www.lfd.uci.edu/~gohlke/pythonlibs/
.. _`matplotlib examples`: https://matplotlib.org/3.1.1/gallery/index.html
.. _`learn more about backends here`: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend