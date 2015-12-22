Improve your client-side-javascript workflow more by using ES6
##############################################################

:date: 2015-11-16 14:20
:tags: javascript, browserify, node, npm, watchify, generic, uglify, babel, es6
:category: javascript
:slug: using-browserify-es6
:author: Serafeim Papastefanos
:summary: Browserify can be used to integrate next generation javascript (es6) to your client side scripts using babel.

.. contents::


**Update 22/12/2015:** Add section for the object-spread operator.

Introduction
------------

In a `previous article <{filename}using-browserify.rst>`_
we presented a simple workflow to improve your client-side (javascript) workflow
by including a bunch of tools from the node-js world i.e browserify_ and
its friends, watchify_ and uglify-js_.

Using these tools we were able to properly manage our client side dependencies
(no more script tags in our html templates) and modularize our code
(so we could avoid monolithic javascript files that contained all our code).
Another great improvement to our workflow would be to include ES6 to the mix!

ES6 (or EcmaScript 2015) is more or less "Javascript: TNG". It has many features
that greatly improve the readability and writability of javascript code - for instance,
thick arrows, better classes, better modules, iterators/generators, template strings,
default function parameters and many others!
More info on these features and how they could be used can be found on the es6features_ repository.

Unfortunately, these features are either not supported at all, or they are partially supported
on current (November 2015) browsers. However all is *not* lost yet: Since we already use browserify
to our client side workflow, we can easily enable it to read source files with ES6 syntax
and transform them to normal javascript using a transformation through the babel_ tool.

In the following, we'll talk a bit more about the node-js package manager (npm) features,
talk a little about babel and finally
modify our workflow so that it will be able to use ES6! Please notice that to properly follow this article
you need to first read the `previous one <{filename}using-browserify.rst>`_.

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

In any case, to be able to use ES6, we'll need to install babel and its es6 presets
(don't forget that you need to have a ``package.json`` for the dependencies to be
saved so either do an ``npm init`` or create a ``package.json`` file containing only
``{}``):

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


The object-spread operator
--------------------------

Many examples in the internet use the `object spread operator`_ which is `not part of es6`_ so our
proposed babel configuration does not support it! 
To be able to use this syntax, we'll need to install the corresponding babel plugin by using
``npm install babel-plugin-transform-object-rest-spread --save`` and add it to our babel configuration
in the plugins section, something like this:

.. code ::

    "presets": [
      "es2015",
      "react"
    ],
    "plugins": [
      "transform-object-rest-spread"
    ]

If everything is ok this should be transpiled without errors using ``node_modules\.bin\browserify testbabe.js -t babelify``

.. code ::
 
  let x = {a:1 , b:2 };
  let y = {...x, c: 3};
    
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
.. _`not part of es6`: http://stackoverflow.com/questions/31115276/ecmascript-6-spread-operator-in-object-deconstruction-support-in-typescript-and
.. _`object spread operator`: https://facebook.github.io/react/docs/jsx-spread.html#spread-attributes