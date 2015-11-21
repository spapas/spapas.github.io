PDFs in Django: The essential guide
###################################

:date: 2015-11-23 14:20
:tags: pdf, django, reportlab, python, 
:category: django
:slug: pdf-in-django
:author: Serafeim Papastefanos
:summary: An essential guide to creating, editing and serving PDF files in django

.. contents::


Introduction
------------

I've noticed that although it is easy to create PDFs with 
Python, I've noticed there's no complete guide on how to 
integrate these tools with Django and resolve the problems
that you'll encounter when trying to actually create PDFs
from your Django web application. 

In this article I will present the solution I use for 
creating PDFs with Django, along with various tips on how to
solve most of your common requirements. Specifically, here
are some things that we'll cover:

* Learn how to create PDFs "by hand"
* Create PDFs with Django using a normal Djang Template (similar to an HTML page)
* Create layouts
* Use styling in your output
* Embed images to your PDFs
* Change the fonts of your PDFs
* Add page numbers
* Merge (concatenate) PDFs


The players
-----------

We are going to use the following main tools:

* ReportLab_ is an open source python library for creating PDFs. It uses a low-level API that allows "drawing" strings on specific coordinates 
on the PDF - for people familiar with creating PDFs in Java it is more or less *iText_ for python*. 

* xhtml2pdf_ (formerly named *pisa*) is an open source library that can convert HTML/CSS pages to PDF using ReportLab.

* django-xhtml2pdf_ is a wrapper around xhtml2pdf that makes integration with Django easier.

* PyPDF2_ is an open source tool of that can split, merge and transform pages of PDF files.

I've created a `django project`_ https://github.com/spapas/django-pdf-guide with everything covered here. Please clone it,
install its requirements and play with it to see how everything works !

Before integrating the above tools to a Django project, I'd like to describe them individually a bit more. Any files
I mention below will be included in this project.

ReportLab
=========

ReportLab offers a really low API for creating PDFs. It is something like having a ``canvas.drawString()`` method (for
people familiar with drawing APIs) for your PDF page. Let's take a look at an example, creating a PDF with a simple
string:

.. code::

  # -*- coding: utf-8 -*-
  from reportlab.pdfgen import canvas
  import reportlab.rl_config


  if __name__ == '__main__':
      reportlab.rl_config.warnOnMissingFontGlyphs = 0
      c = canvas.Canvas("./hello1.pdf",)
      c.drawString(100, 100, "Hello World")
      c.showPage()
      c.save()

Save the above in a file named testreportlab1.py. If you run python testreportlab1.py (in an environment that has
reportlab of cours) you should see no errors and a pdf named ``hello1.pdf`` created. If you open it in your PDF
reader you'll see a blank page with "Hello World" written in its lower right corner. 

If you try to add a unicode text, for example "Καλημέρα κόσμε", you should see something like the following:

.. image:: /images/hellopdf2.png
  :alt: Our project
  :width: 280 px

It seems that the default font that ReportLab uses does not have a good support for accented greek characters 
since they are missing  (and probably for various other characters). 

To resolve this, we could try changing the font to one that contains the missing symbols. You can find free
fonts on the internet (for example the `DejaVu` font), or even grab one from your system fonts (in windows,
check out ``c:\windows\fonts\``). In any case, just copy the ttf file of your font inside the folder of
your project and crate a file named testreportlab2.py with the following (I am using the DejaVuSans font):

.. code::

  import reportlab.rl_config
  from reportlab.pdfbase import pdfmetrics
  from reportlab.pdfbase.ttfonts import TTFont


  if __name__ == '__main__':
      c = canvas.Canvas("./hello2.pdf",)
      reportlab.rl_config.warnOnMissingFontGlyphs = 0
      pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

      c.setFont('DejaVuSans', 22)
      c.drawString(100, 100, u"Καλημέρα ελλάδα.")

      c.showPage()
      c.save()
      
The above was just a scratch on the surface of ReportLab, mainly to be confident that
everything *will* work fine for non-english speaking people! To find out more, you should check the  `ReportLab open-source User Guide`_.

I also have to mention that 
`the company behind ReportLab`_ offers some great commercial solutions based on ReportLab for creating PDFs (similar to JasperReports_) - check it out
if you need support or advanced capabilities.


NPM, --save, --save-dev and avoiding global deps
------------------------------------------------

In the previous article, I had recommended to install the needed tools 
(needed to create the output bundle browserify, watchify, uglify) globally
using npm install -g package (of course the normal dependencies like moment.js
would be installed locally).
This has one advantage and two disadvantages: It
puts these tools to the path so they can be called immediately (i.e browserify)
but you will need root access to install a package globally and nothing is
saved on ``package.json`` so you don't know which packages must be installed 
in order to start developing the project!

This could be ok for the introductionary article, however for this one I
will propose another alternative: Install all the tools *locally* using just
``npm install package --save``. These tools will be put to the ``node_modules`` folder. They
*will not* be put to the path, but if you want to execute a binary by yourself
to debug the output, you can find it in ``node_modules/bin``, for example,
for browserify you can run ``node_modules/bin/browserify``. Another intersting
thing is that if you create executable scripts in your ``package.json`` you
don't actually need to include the full path but the binaries will be found.

Another thing I'd like to discuss here is the difference between ``--save``
and ``--save-dev`` options that can be passed to npm install. If you take
a look at other guides you'll see that people are using ``--save-dev`` for
development dependencies (i.e testing) and ``--save`` for normal dependencies.
The difference is that these dependencies are saved in different places in
``package.json`` and if you run ``npm install --production`` you'll get only
the normal dependencies (while, if you run ``npm install`` all dependencies
will be installed). In these articles, I chose to just use ``--save`` everywhere,
after all the only thing that would be needed for production would be the
``bundle.js`` output file.


Using babel
-----------

The babel_ library "is a JavaScript compiler". It gets input files in a variant
of javascript (for example, ES6) and produces normal javascript files -- something
like what browserify transforms do. However, what babel does (and I think its
the only tool that does this) is that it allows you to use ES6 features *now* by
transpiling them to normal (ES5) javascript. Also, babel has `various other transforms`_,
including a react transform 
(so you can use this instead of the reactify browserify-transform)!

In any case, to be able to use ES6, we'll need to install babel and its es6 presets:

.. code::

  npm install  babel babel-preset-es2015 --save
  
If we wanted to also use babel for react we'd need to install babel-preset-react. 

To configure babel we can either add a ``babel``
section in our ``package.json`` or create a new file named .babelrc and put the configuration there.

I prefer the first one since we are already using the ``package.json``. So add the following attribute
to your ``package.json``:

.. code::

  "babel": {
    "presets": [
      "es2015"
    ]
  }

If you wanted to configure it through ``.babelrc`` then you'd just copy to it the contents of ``"babel"``.

To do some tests with babel, you can install its cli (it's not included in the babel package) through
``npm install babel-cli``. Now, you can run ``node_modules/.bin/babel``. For example, create a 
file named ``testbabel.js`` with the following contents (thick arrow):

.. code::

  [1,2,3].forEach(x => console.log(x) );
  
when you pass it to babel you'll see the following output:

.. code::

    >node_modules\.bin\babel testbabel.js
    "use strict";

    [1, 2, 3].forEach(function (x) {
      return console.log(x);
    });



Integrate babel with browserify
-------------------------------

To call babel from browserify we're going to use the babelify_ browserify transform which
actually uses babel to transpile the browserify input. After installing it with

.. code::
  
  npm install babelify --save
  
you need to tell browserify to use it. To do this, you'll just pass a -t babelify parameter to
browserify. So if you run it with the ``testbabel.js`` file as input you'll see the following output:

.. code::

    >node_modules\.bin\browserify -t babelify testbabel.js
    [...] browserify gibberish 
    "use strict";

    [1, 2, 3].forEach(function (x) {
      return console.log(x);
    });

    [...] more browserify gibberish 

yey -- the code is transpiled to ES5! 

To create a complete project, let's add a normal requirement (moment.js): 

.. code::
  
  npm install moment --save

and a file named ``src\main.js`` that uses it with ES6 syntax: 

.. code::

  import moment from 'moment';

  const arr = [1,2,3,4,5];
  arr.forEach(x => setTimeout(() => console.log(`Now: ${moment().format("HH:mm:ss")}, Later: ${moment().add(x, "days").format("L")}...`), x*1000));

To create the output javascript file, we'll use the browserify and watchify commands with the
addition of the -t babelify switch. Here's the complete ``package.json`` for this project:

.. code::

    {
      "dependencies": {
        "babel": "^6.1.18",
        "babel-preset-es2015": "^6.1.18",
        "babelify": "^7.2.0",
        "browserify": "^12.0.1",
        "moment": "^2.10.6",
        "uglify-js": "^2.6.0",
        "watchify": "^3.6.1"
      },
      "scripts": {
        "watch": "watchify src/main.js -o dist/bundle.js -v -t babelify",
        "build": "browserify src/main.js -t babelify | uglifyjs -mc warnings=false > dist/bundle.js"
      },
      "babel": {
        "presets": [
          "es2015"
        ]
      }
    }

Running ``npm run build`` should create a ``dist/bundle.js`` file. If you include this in an html,
you should see something like this in the console: 

.. code::

    Now: 13:52:09, Later: 11/17/2015...
    Now: 13:52:10, Later: 11/18/2015...


Conclusion
----------

Using the combination of babel and javascript we can easily write ES6 code in our modules! This,
along with the modularization of our code and the management of client-side dependencies should
make client side development a breeze! 

Please notice that to keep the presented workflow simple and easy to
replicate and configure, we have not used any external
task runners (like gulp or grunt) -- all configuration is kept in a single file (package.json) and
the whole environment can be replicated just by doing a ``npm install``. Of course, the capabilities of 
browserify are not unlimited, so if you wanted to do something more complicated
(for instance, lint your code before passing it to browserify) you'd need to use the mentioned
task runners (or webpack which is the current trend in javascript bundlers and actually replaces
the task runners). 


.. _ReportLab: https://bitbucket.org/rptlab/reportlab
.. _xhtml2pdf: https://github.com/chrisglass/xhtml2pdf
.. _django-xhtml2pdf: https://github.com/chrisglass/django-xhtml2pdf
.. _PyPDF2: https://github.com/mstamy2/PyPDF2
.. _`the company behind ReportLab`: http://reportlab.com/
.. _`django project`: https://github.com/spapas/django-pdf-guide
.. _iText: http://itextpdf.com/
.. _JasperReports: http://community.jaspersoft.com/project/jasperreports-library
.. _DejaVu: http://dejavu-fonts.org/wiki/Main_Page

.. _`ReportLab open-source User Guide`: http://www.reportlab.com/docs/reportlab-userguide.pdf

.. _browserify: http://browserify.org/
.. _babelify: https://github.com/babel/babelify
.. _watchify: https://github.com/substack/watchify
.. _`NIH syndrome`: http://en.wikipedia.org/wiki/Not_invented_here
.. _require: https://github.com/substack/browserify-handbook#require
.. _`a package for windows`: https://nodejs.org/download/
.. _moment.js: http://momentjs.com/
.. _underscore.js: http://underscorejs.org/
.. _`a lot of transforms`: https://github.com/substack/node-browserify/wiki/list-of-transforms
.. _uglify-js: https://www.npmjs.com/package/uglify-js
.. _fabric: http://www.fabfile.org/
.. _es6features: https://github.com/lukehoban/es6features
.. _babel: https://babeljs.io/
.. _`various other transforms`: https://babeljs.io/docs/plugins/
