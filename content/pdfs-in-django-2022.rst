PDFs in Django like it's 2022!
##############################

:date: 2022-02-14 12:20
:tags: django, python, pdf, wkhtmltopdf
:category: django
:slug: django-pdfs-2022
:author: Serafeim Papastefanos
:summary: How to render PDFs in Django like it's 2022!

In a `previous article <{filename}django-pdf-essential-guide.rst>`_ I had written a very comprehensive
guide on how to render PDFs in Django using tools like reportlab and xhtml2pdf. Although these tools 
are still valid and work fine I have decided that usually it's way too much pain to set them up to work
properly. 

Another common way to generate PDFs in the Python world is using the weasyprint_ library. 
Unfortunately this library has way too many requirements and installing it on Windows 
is worse than `putting needles in your eyes`_. I don't like needles in my eyes, thank you very much.

There are various other ways to generate PDFs like using a report server like Japser or 
SQL Server Reporting Services but these are too "enterpris-y" for most people and require 
another server, a learning curve, etc.

I was actually so disappointed by the status of PDF generation today that in some recent projects
instead of the PDF file I generated an HTML page with a nice pdf-printing stylesheet and
instructed the users to print it as PDF (from the browser) so as to generate the PDF themselves! 

However, recently I found another way to generate PDFs in my Django projects which I'd like to share
with you: Using the wkhtmltopdf_ tool. The wkhtmltopdf is a command line program that has binaries 
for more or less every operating system. It's a single binary that you can download and put it in
a directory, you don't need to run another server or any fancy installation. Only an executable. To
use it? You call it like `wkhtmltopdf http://google.com google.pdf` and it will download the url 
and generate the pdf! It's as simple as that! This tool is old and heavily used but only recently I
researched its integration with Django. 

Please notice that there's actually a `django-wkhtmltopdf`_ library for integrating wkhtmltopdf with 
django. However I din't have good results while trying to use it (maybe because of my Windows dev
environment). Also, implementing the integration myself allowed my to more easily understand what's 
happening and better debug the wkhtmltopdf. However YMMV, after you read this small post to understand 
how the integration works you can try django-wkhtmltopdf to see if it works in your case.

In any way, the first thing you need to do is download and install wkhtmltopdf for your platform and save its
full path in your settings.py like this:

.. code-block:: python
  
  # For linux 
  WKHTMLTOPDF_CMD = '/usr/local/bin/wkhtmltopdf'
  
  # or for windows
  WKHTMLTOPDF_CMD = r'c:\util\wkhtmltopdf.exe'

Notice that I'm using the full path. I have observed that even if you put the binary to a directory 
in the system PATH it won't be picked (at least in my case) thus I recommend using the full path.

Now, let's suppose we've got a ``DetailView`` (let's call it ``SampleDetailView``) that we'd like to render as PDF. We can use the following 
CBV for that: 

.. code-block:: python

  from subprocess import check_output
  from django.template import Context, Template
  from django.template.loader import get_template 
  from tempfile import NamedTemporaryFile
  import os

  class SamplePdfDetailView(SampleDetailView):
    def get_resp_from_file(self, filename, context):
        template = get_template(filename)
        resp = template.render(context)
        return resp 
    
    def get_resp_from_string(self, template_str, context):
        template = Template(template_str)
        resp = template.render(Context(context))
        return resp 

    def render_to_response(self, context):
        context['pdf'] = True
        # We can use either 
        resp = self.get_resp_from_string("<h1>Hello, world! {{ object }}</h1>", context)
        # or 
        # resp = self.get_resp_from_file('test_pdf.html', context)
        
        tempfile = NamedTemporaryFile(mode='w+b', buffering=-1,
                                      suffix='.html', prefix='tmp',
                                      dir=None, delete=False)

        tempfile.write(resp.encode('utf-8'))
        tempfile.flush()
        tempfile.close()
        cmd = [
            settings.WKHTMLTOPDF_CMD, 
            '--page-size', 'A4', '--encoding', 'utf-8', 
            '--footer-center', '[page] / [topage]',
            '--enable-local-file-access',  tempfile.name, '-']
        # print(" ".join(cmd))
        out = check_output(cmd)
        
        os.remove(tempfile.name)
        return HttpResponse(out, content_type='application/pdf')

We can put the pdf view on our url patterns right next to our ``DetailView`` i.e:

.. code-block:: python

  [
    ...
    path(
        "detail/<int:pk>/",
        permission_required("core.user")(
            views.SampleDetailView.as_view()
        ),
        name="detail",
    ),
    path(
        "detail/<int:pk>/pdf/",
        permission_required("core.user")(
            views.SamplePdfDetailView.as_view()
        ),
        name="detail_pdf",
    ),
    ...
  ]


Let's try to understand how this works: First of all notice that we have two options, either 
create a PDF from an html string or from a normal template file. For the first option we pass
the full html string to the ``get_resp_from_string`` and the context and we'll get the rendered html
(i.e the context will be applied to the template). 
For the second option we pass the filename of a django template and the context. Notice that 
there's a small difference on how the ``template.render()`` method is called in the two methods.

After that we've got an html file saved in the ``resp`` string. We want to give this to wkhtmltopdf so 
as to be converted to PDF. To do that we first create a temporary file using the ``NamedTemporaryFile``
class and write the ``resp`` to it. Then we call wkhtmltopdf passing it this temporary file. Notice we 
use the ``subprocess.check_output`` function that will capture the output of the command and return it.

Finally we delete the temporary file and return the pdf as an ``HttpResponse``. 

We call the wkhtmltopdf like this:

.. code::

  c:\util\wkhtmltopdf.exe --page-size A4 --encoding utf-8 --footer-center [page] / [topage] --enable-local-file-access C:\Users\serafeim\AppData\Local\Temp\tmp_lh5r6f9.html -

The page-size can be changed to letter if you are in the US. The encoding should be utf-8. The --footer-center option adds a 
footer to the PDF page with the current page and the total number of pages. The --enable-local-file-access is very important 
since it allows ``wkhtmltopdf`` to access local files (in the filesystem) and not only remote ones. After that we've got the 
full path of our temporary file and following is the ``-`` which means that the pdf output will be on the stdout (so we'll capture it 
with ``check_output``). 

Notice that there's a commented out print command before the ``check_output`` call. If you have problems you can call this 
command from your command line to debug the wkhtmltopdf command (don't forget to comment out the ``os.remove`` line to keep 
the temporary file). Also, wkhtmltopdf will output some stuff while rendering the command, for example something like: 

.. code::

  Loading pages (1/6)
  Counting pages (2/6)
  Resolving links (4/6)
  Loading headers and footers (5/6)
  Printing pages (6/6)
  Done

You can pass the ``--quit`` option to hide this output. However the output is useful to see what wkhtmltopdf is doing in
case there are problems so I recommend leaving it on while developing. Let's take a look at a problematic output:

.. code::

  Loading pages (1/6)
  Error: Failed to load file:///static/bootstrap/css/bootstrap.min.css, with network status code 203 and http status code 0 - Error opening /static_edla/bootstrap/css/govgr_bootstrap.min.css: The system cannot find the path specified.
  [...]
  Counting pages (2/6)
  Resolving links (4/6)
  Loading headers and footers (5/6)
  Printing pages (6/6)
  Done

The above output means that our template tries to load a css file that wkhtmltopdf can't find and errors out! To understand this error, I had a line like this in my template:

.. code::

  <link href="{% static 'bootstrap/css/bootstrap.min.css' %}" rel="stylesheet">

which will be converted to a link like ```/static/bootstrap/css/bootstrap.min.css``. 
However notice that I tell wkhtmltopdf to render a file from my temporary directory, it doesn't 
know where that link points to! 
Following this thing you need to be extra careful to *include everything* in your HTML-pdf template and not 
use any external links. So all styles must be inlined in the template using ``<style>`` tags and all images must be 
converted to data images with base64, something like:

.. code:: 

  <img src='data:image/png;base64,...>

To do that in python for a dynamic image you can use something like:

.. code-block:: python

  import base64
  
  def convert_to_data(image): 
    return 'data:image/xyz;base64,{}'.format(base64.b64encode(image).decode('utf-8'))

and then use that as your image src (notice I'm using ``image/xyz`` here for an 
arbitrary image, please use the correct image type if you know it i.e ``image/png`` or ``image/jpg``).

If you've got a static image you want to include you can convert it to base64 using an online service `like this`_,
or read it with python and convert it: 

.. code-block:: python
  
  import base64 

  with open('static/images/image.png', 'rb') as image:
    print(base64.b64encode(image.read()).decode('utf-8'))

Instead of a ``DetailView`` we could use the same approach for any kind of CBV. If you are to use the PDF 
response to multiple CBVs I recommend exporting the functionality to a mixin and inheriting from that also
(see my `CBV guide <{filename}django-cbv-tutorial.rst>`_ for more).

Finally, the big question in the room is why should I convert my template to a file and pass that to 
wkhtmltopdf, can't I use the URL of my template, i.e pass wkhtmltopdf something like http://example.com/app/detail/321/?

By all means you can! This will also enable you to avoid using inline styles and media!! 
However keep in mind that the usual case is that this view will not be public but will need an authenticated user to 
access it; wkhtmltopdf is publicly trying to access it, it doesn't have any rights to it so you'll get a 404 or 403 error! 
Of course you can  
start an adventure on authenticating it somehow (and maybe doing something stupid) or you can just follow my lead 
and render it to a file :)

.. _weasyprint: https://weasyprint.org/
.. _`putting needles in your eyes`: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
.. _wkhtmltopdf: https://wkhtmltopdf.org/
.. _`django-wkhtmltopdf`: https://github.com/incuna/django-wkhtmltopdf
.. _`like this`: https://www.base64-image.de/