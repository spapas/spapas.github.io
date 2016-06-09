Change the primary color of bootstrap material design
#####################################################

:date: 2014-12-16 16:20
:tags: css, design, boostrap-material-design, less, node.js
:category: css
:slug: change-bootstrap-material-primary-color
:author: Serafeim Papastefanos
:summary: A tutorial to help users change the primary color of Bootstrap material design


Introduction
------------

`Bootstrap Material Design`_ is a great theme that sits on top of `Bootstrap`_ and transforms it to
`Material Design`_! The great thing about Bootstrap Material Design is that you just need to include
its css and js files after your Bootstrap files and ...

boom! Your page is Material Design compatible!

.. image:: https://google.github.io/material-design-icons/action/svg/ic_thumb_up_24px.svg


A nice feature of Bootstrap Material Design is that you can change its default color to a new one (I
don't really like the current - greenish one). This is easy for people with less skills however I
found it rather challenging when I tried it. That's why I will present a step by step tutorial on
changing the default primary color of the Bootstrap Material Design theme:

Step 1: Get the code
--------------------

Use git to make a local clone of the project with ``git clone https://github.com/FezVrasta/bootstrap-material-design.git``. This will create a directory
named ``bootstrap-material-design``. Or you can download the latest version of the code using (https://github.com/FezVrasta/bootstrap-material-design/archive/master.zip)
and unzip it to the ``bootstrap-material-design`` directory.


Step 2: Install node.js and npm
-------------------------------

You need to have `node.js`_ and npm installed in your system - this is something very easy so I won't go into any details about this. After you have installed
both node.js and npm you need to put them in your path so that you'll be able to run ``npm -v`` without errors and receive something like ``1.4.14``.

Step 3: Install less
--------------------

less_ is a CSS preprocessor in which Bootstrap Material Design has been written. To install it, just enter the command ``npm install -g less``. After that
you should have a command named ``lessc`` which, when run would output something like: ``lessc 2.1.1 (Less Compiler) [JavaScript]``.


Step 4: Create the customizations files
---------------------------------------

Go to the directory where you cloned (or unzipped) the Bootstrap Material Design code and create a file named ``custom.less`` (so, that file should be
in the same folder as with ``bower.json``, ``Gruntfile.js`` etc) with the following contents:

.. code::

    @import "less/material.less";

    // Override @primary color with one took from _colors.less
    @primary: @indigo;

(I wanted to use the indigo color as my primary one - you may of course use whichever color from the ones defined in ``less/_variables.less`` you like)

This file may contain other default values for variables - if I find anything useful I will add it to this post (also please reply with any recommendations).

**Update 13/10/2015** After a request from commenter Jofferson Ramirez Tiquez, here's a custom.less that overrides more colors from ``_variables.css``
(beyond the primary color, it changes the success color to teal and info and warning to the corresponding hex color values):

.. code:: 

    @import "less/material.less";

    @primary: @indigo;
    @success: @teal;
    @info: #CFD8DC;
    @warning:#455A64;
    

Step 5: Create your custom material css file
--------------------------------------------

Finally, run the following command: ``lessc custom.less  > material-custom.css``. This will create a file named ``material-custom.css`` that contains your
custom version of Bootstrap Material Design! If you want your ``material-custom.css`` to be compressed, add the ``-x`` option like this:  ``lessc -x custom.less  > material-custom.css``.

You may now include ``material-custom.css`` instead of ``material.css`` (or the minified version of it) to your projects and you'll have your own primary color! 


**Update 09/06/2016**: After some comments I returned to this blog post and tried to re-create the custom
css file. Unfortunately, for the latest versions of the bootstrap-material-design, the above step by step instructions need to be changed in two places:

* Step 1: Instead of only the bootstrap-material-design code, you also need to retrieve the code of the original bootstrap. To do that you can do a ``git clone https://github.com/twbs/bootstrap.git`` so that you'll have the bootstrap directory next to the bootstrap-material-design directory. Be careful on that, you should have two directories side by side, one containing the bootstrap code and another containing the bootstrap-material-design code. This is required because bootstrap-material-design references some bootstrap variables (from ``less/_import-bs-less.less``).
* Step 4: For the customizations file (``custom.less``), you should change the line ``@import "less/material.less";`` to ``@import "less/bootstrap-material-design.less";`` because the name of that file has been changed.

After these two changes you should once again be able to create your custom css file!


.. _`Bootstrap Material Design`: https://github.com/FezVrasta/bootstrap-material-design
.. _`Bootstrap`: http://getbootstrap.com/
.. _`Material Design`: http://www.google.com/design/spec/material-design/introduction.html
.. _`node.js`: http://nodejs.org/
.. _`less`: http://lesscss.org/
.. _bootswatch: https://bootswatch.com/
.. _`django-material`: https://github.com/viewflow/django-material