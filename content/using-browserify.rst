Using browserify and watchify to improve your client-side-javascript workflow
#############################################################################

:date: 2015-05-27 14:20
:tags: javascript, browserify, node, npm, watchify, generic
:category: javascript
:slug: using-browserify-watchify
:author: Serafeim Papastefanos
:summary: Using browserify and watchify you can greatly improve the workflow of your client-side javascript.


The problem
-----------

Once upon a time, when people started using client-side code to their projects they (mainly
due to the lack of decent client-side libraries but also because of the `NIH syndrome`_)
were just adding their own code in script nodes or .js files using ``document.getElementById`` to manipulate
the DOM (good luck checking for all possible browser-edge cases)
and ``window.XMLHttpRequest`` to try doing AJAX.

After these dark-times, the
age of javascript-framework came: prototype, jquery, dojo. These were (and still are)
some great libraries (even NIH-sick people used them to handle browser incompatibilities):
You just downloaded the .js file with the framework, put it inside your project
static files and added it to your page with a script tag and then filled your client-side
code with funny $('#id') symbols!

Coming to the modern age in client-side development, the number of decent libraries has greatly increased
and instead of monolithic frameworks there are different libraries for different needs. So instead of
just downloading a single file and adding the script node for that file to your HTML, you need to
download the required javascript files, put them all in your static files directory and then micro-manage
the script nodes for each of your pages depending on which libraries each page needs! So if you want
to use (for example) moment.js to your client-side code you need to go to *all* HTML pages that use that
specific client-side code and add a moment.js-script element!

As can be understood this leads to really ugly situations like people avoiding refactoring their code to use
external libraries, using a single-global module  with all their client side code, using CDN to avoid
downloading the javascript libraries and of course never upgrade their javascript libraries!

The solution
------------

browserify_ and watchify_ are two sister tools from the server-side-javascript (node.js and friends)
world that greatly improve your javascript workflow: Using them, you no longer need to micro-manage
your script tags but instead you just declare the libraries each of your client-side modules is
using - or you can even create your own reusable modules! Also, installing (or updating) javascript
libraries is as easy as running a single command!

How are they working? With browserify you create a single ``main.js`` for each of your HTML
pages and in it you declare its requirements using require_. You'll then pass your ``main.js``
through browserify and it will create a single file (e.g ``bundle.js``) that contains all the requirements
(of course each requirement could have other requirements - they'll be automatically also
included in the resulting .js file). That's the *only* file you need to put to the script tag of
your HTML! Using watchify, you can *watch* your ``main.js`` for changes (the changes may also
be in the files included from main.js) and automatically generate the resulting ``bundle.js`` so that
you'll just need to hit F5 to refresh and get the new version!

Below, I will propose a really simple and generic workflow that should cover most of your javascript needs.
I should mention that I mainly develop django apps and my development machine is running windows, however you
can easily use exactly the  same workflow from any kind of server-side technology (ruby, python, javascript,
java, php or even static HTML pages!) or development machine (windows, linux, osx) - it's exactly the same!

Installing required tools
-------------------------

As already mentioned, you need two node.js tools. Just install them globally using npm (installing
node.js and npm is really easy - there's even `a package for windows`_):

.. code::

  npm install -g browserify watchify

The ``-g`` switch installs the packages globally so you can use the browserify and watchify commands from
your command prompt - after that entering ``browserify`` or ``watchify`` from your command prompt should be working.

Starting your (node.js) project
-------------------------------

Although you may already have a project structure, in order to use browserify you'll need to 
create a node.js project (project from now on) that needs just two things:

- a ``package.json`` that lists various options for your project 
- a ``node_modules`` directory that contains the packages that your project uses

To create the ``package.json`` you can either copy paste a simple one or run ``npm init`` inside 
a folder of your project. After ``npm init`` you'll need to answer a bunch of questions and then
a ``package.json`` will be created to the same folder. If you don't want to answer these questions
(most probably you only want to use node.js for browserify - instead you wouldn't be reading
this) then just put an empty json string ``{}`` in ``package.json``.

I recommend adding ``package.json`` to the top-level folder of your version-controlled souce-code tree -
please put this file in your version control - the ``node_modules`` directory will be be created
to the same directory with ``package.json`` and should be ignored by your version control.

Running browserify for the first time
-------------------------------------

Not the time has come to create a ``main.js`` file. This could be put anywhere you like (based on your project structure) -
I'' suppose that ``main.js`` is inside the ``src/``  folder of your project.
Just put a ``console.log("Hello, world")`` to the ``main.js`` for now. To test that everything is working, 
run:

.. code::

  browserify src/main.js
  
You should see some minified-js gibberish to your console (something like ``(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof ...)``
) which means that everything works fine. Now, create a ``dist`` directory which would contain your bundle files and run

.. code::

  browserify src/main.js -o dist/bundle.js 
  
the -o switch will put the the same minified-js gibberish output to the  ``dist/bundle.js`` file instead of stdout. 
Finally, include a script element with that file to your HTML and you
should see "Hello, world" to your javascript console when opening the HTML file! 

Using external libraries
------------------------

To use a library from your main.js you need to install it and get a reference to it through require. Let's try to use moment.js_:
To install the library run

.. code::

  npm install moment --save
  
This will create a moment directory inside node_modules that will contain the moment.js library. It will also add a 
dependency to your ``package.json`` (that's what the ``--save`` switch does), something like this:

.. code::

  "dependencies": {
    "moment": "^2.10.3"
  }

Whenever you install more client-side libraries they'll be saved there. When you want to re-install everything (for instance
when you clone your project) you can just do a

.. code::
  npm install 

And all dependencies of ``package.json`` will be installed in ``node_modules`` (that's why ``node_modules`` should not be
tracked).

.. _browserify: http://browserify.org/
.. _watchify: https://github.com/substack/watchify
.. _`NIH syndrome`: http://en.wikipedia.org/wiki/Not_invented_here
.. _require: https://github.com/substack/browserify-handbook#require
.. _`a package for windows`: https://nodejs.org/download/
.. _moment.js: http://momentjs.com/