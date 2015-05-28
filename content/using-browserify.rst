Using browserify and watchify to improve your client-side-javascript workflow
#############################################################################

:date: 2015-05-27 14:20
:tags: javascript, browserify, node, npm, watchify, generic, uglify
:category: javascript
:slug: using-browserify-watchify
:author: Serafeim Papastefanos
:summary: Using browserify and watchify you can greatly improve the workflow of your client-side javascript.

.. contents::


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

browserify not only concatenates your javascript libraries to a single bundle but can also transform
your coffesscript, typescript, jsx etc files to javascrpt and *then* also add them to the bundle. This
is possible through a concept called transforms -- there are `a lot of transforms`_ that you can use.

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

and all dependencies of ``package.json`` will be installed in ``node_modules`` (that's why ``node_modules`` should not be
tracked).

After you've installed moment.js to your project change ``src/main.js`` to:

.. code::

  moment = require('moment')
  console.log(moment() );

and rerun ``browserify src/main.js -o dist/bundle.js``. When you reload your HTML you'll see the that you are able to use
moment - all this without changing your HTML!!!

As you can understand, in order to use a library with browserify, this library must support it by having an npm package. The nice thing is that
most libraries already support it -- let's try for another example to use underscore.js_ and (for some reason) we need version underscore 1.7 :

.. code::

  npm install underscore@1.7--save

you'll se that your package.json dependencies will also contain underscore.js 1.7:

.. code::

  {
    "dependencies": {
      "moment": "^2.10.3",
      "underscore": "^1.7.0"
    }
  }

If you want to upgrade underscore to the latest version run a:

.. code::

  npm install underscore --upgrade --save

and you'll see that your ``package.json`` will contan the latest version of underscore.js.

Finally, let's change our ``src/man.js`` to use underscore:

.. code::

  moment = require('moment')
  _ = require('underscore')

  _([1,2,3]).map(function(x) {
    console.log(x+1);
  });

After you create your bundle you should se 2 3 4 in your console!

Introducing watchify
--------------------

Running browserify *every* time you change your js files to create the ``bundle.js`` feels
like doing repetitive work - this is where wachify comes to the rescue; watchify is a
tool that watches your source code and dependencies and when a change is detected it will
recreate the bundle automagically!

To run it, you can use:

.. code::

  watchify src/main.js -o dist/bundle.js -v

and you'll see something like: ``155544 bytes written to dist/bundle.js (0.57 seconds)`` -- try
changing main.js and you'll see that bundle.js will also be re-written!

Some things to keep in mind with watchify usage:

- The -v flag outputs the verbose text (or else you won't se any postive messages) - I like using it to be sure that everything is ok.
- You need to use the -o flag with watchify -- you can't output to stdout(we'll see that this will change our workflow for production a bit later)
- watchify takes the same parameters with browserify -- so if you do any transformations with browserify you can also do them with watchify

In the following, I'll assume that you are running the ``watchify src/main.js -o dist/bundle.js -d`` so your bundles will
always be re-created when changes are found.

Creating your own modules
-------------------------

Using browserify we can create our own modules and *require* them in other modules using the ``module.exports`` mechanism!

Creating a module is really simple: In a normal javascript file either assign directly to module.exports or
include all local objects you want to be visible as an attribute to ``module.exports`` -- everything
else will be private to the module.

As an example, let's create an ``src/modules`` folder and put a file module1.js inside it, containing the following:

.. code::

  var variable = 'variable'
  var variable2 = 'variable2'
  var funct = function(x) {
    return x+1;
  }
  var funct2 = function(x) {
    return x+1;
  }

  module.exports['variable'] = variable
  module.exports['funct'] = funct

As you see, although we've defined a number of things in that module, only the variable and funct attributes
of module.exports will be visible when the module is used. To use the module, change main.js like this:

.. code::

  module1 = require('./modules/module1')
  console.log(module1.funct(9))

When you refresh your HTML you'll see 10 in the console. So, require will return the ``module.exports`` objects
of each module. It will either search in your project's ``node_modules`` (when you use just the modfule name,
for example ``moment``, or locally (when you start a path with either ``./`` or ``../`` -- in our case we required
the module ``module1.js`` from the folder ``modules``).

As a final example, we'll create another module that is used by module1: Create a file named ``module2.js`` inside the
``modules`` folder and the following contents:

.. code::

  var funct = function(x) {
      return x+1;
  }

  module.exports = funct

After that, change ``module1.js`` to this:

.. code::

  module2 = require('./module2')

  var variable = 'variable'
  var funct = function(x) {
      return module2(x)+1;
  }

  module.exports['variable'] = variable
  module.exports['funct'] = funct

So ``module1`` will import the ``module2`` module (from the same directory) and call it (since a function is assignedd to module.exports).
When you refresh your HTML you should see 11!

Uglifying your bundle
---------------------

If had taken a look at the file size of your ``bundle.js`` when you'd included moment.js or underscore.js you'd see
that the file size has been greatly increased. Take a peek at ``bundle.js`` and you'll see why: The contents of the module files
will be concatenated as they are, without any changes! This may be nice for development / debugging, however for production
we'd like our bundle.js to be minified -- or uglyfied as it's being said in the javascript world.

To help us with this, uglifying we'll use uglify-js_. First of all, please install it globally

.. code::

  npm install uglify-js -g

and you'll be able to use the ``uglifyjs`` command to uglify your bundles! To use the ``uglifyjs`` command for your ``bundle.js``
try this

.. code::

  uglifyjs dist\bundle.js  > dist\bundle.min.js

and you'll see the size of the bundle.min.js greatly reduced! To achieve even better minification (and code mangling as an added
bonus) you could pass the -mc options to uglify:

.. code::

  uglifyjs dist\bundle.js -mc > dist\bundle.min.js

and you'll see an even smaller bundle.min.js!

As a final step, we can combine the output of browserify and uglify to a single command using a pipe:

.. code::

  browserify src/main.js | uglifyjs -mc > dist/bundle.js
  
this will create the uglified bundle.js! Using the pipe to output to uglifyjs is not possible
with watchify since watchify cannot output to stdout -- however, as we'll see in the next section
this is not a real problem.

The client-side javascript workflow
-----------------------------------

The proposed client-side javascript workflow uses two commands, one for the development and one 
for creating the production bundle. 

For the development, we'll use watchify since we need to immediately re-create the bundle when a
javascript source file is changed and we don't want any uglification:

.. code::
  
  watchify src/main.js -o dist/bundle.js -v
  
For creating our production bundle, we'll use browserify and uglify:

.. code::

  browserify src/main.js  | uglifyjs -mc warnings=false > dist/bundle.js

(i've added warnings=false to uglfiyjs to suppress warnings).

The above two commands can either be put to batch files or added to your existing workflow (for example
as fabric_ commands if you use fabric). However, since we already have a javascrpt project (i.e a ``package.json``)
we can use that to run these commands. Just add a ``scripts`` section to your package.json like this:

.. code::
  
  {
    "dependencies": {
      "moment": "^2.10.3",
      "underscore": "^1.8.3"
    },
    "scripts": {
      "watch": "watchify src/main.js -o dist/bundle.js -v",
      "build": "browserify src/main.js  | uglifyjs -mc warnings=false > dist/bundle.js"
    }
  }

and you'll be able to run ``npm run watch`` to start watchifying for changes and ``npm run build`` to
create your production bundle! 

Conlusion
---------

In the above we saw two (three if we include uglifyjs) javascript tools that will greatly improve our
javascript workflow. Using these we can easily *require* (import) external javascript libraries to
our project without any micromanagement of script tags in html files. We also can seperate our own
client-side code to self-contained modules that will only export interfaces and not pollute the global
namespace. The resulting production client-side javascript file will be output minimized and ready to
be used by the users' browsers. 

All the above are possible with minimal changes to our code and development workflow:
 
- create a package.json and install your dependencies
- require the external libraries (instead of using them off the global namespace)
- define your module's interace through module.exports (instead of polluting the global namespace)
- change your client javascript files to ``bundle.js``
- run ``npm run watch`` when developing and ``npm run build`` before deploying


.. _browserify: http://browserify.org/
.. _watchify: https://github.com/substack/watchify
.. _`NIH syndrome`: http://en.wikipedia.org/wiki/Not_invented_here
.. _require: https://github.com/substack/browserify-handbook#require
.. _`a package for windows`: https://nodejs.org/download/
.. _moment.js: http://momentjs.com/
.. _underscore.js: http://underscorejs.org/
.. _`a lot of transforms`: https://github.com/substack/node-browserify/wiki/list-of-transforms
.. _uglify-js: https://www.npmjs.com/package/uglify-js
.. _fabric: http://www.fabfile.org/