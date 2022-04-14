Using clojure from Windows
##########################

:date: 2022-04-14 11:20
:tags: clojure, windows, cmd
:category: clojure
:slug: clojure-windows
:author: Serafeim Papastefanos
:summary: How to install and use clojure from Windows

In this small article I'm going to post a guide on how to install and use clojure from Windows using good old' cmd.exe.

Unfortunately, most guides on the official clojure site have instructions on using Clojure from Windows through Powershell or WSL.
For my own reasons I hate both these approaches and only use the cmd.exe to interact with the Windows command line. 

There are more or less two approaches to using clojure. Using leiningen_ or using the clj tools. 
The clojure official guide seems to be `biased towards clj tools`. However I think that leiningen may be easier for new users.
I'll cover both approaches here. 

*Warning* Before doing anything else please make sure to install Java. You need a version of java that is at least 1.8. Try running 
``java -version`` in cmd.exe to make sure you have java and it is the correct version.

Leiningen
---------

To install leiningen you just download the lein.bat file from their page and put it in a folder in your PATH. You'll then run
lein and it will download all dependencies and install itself! 

To start a clojure repl to be able to play with clojure you write ``lein repl``. If everything went smooth you should see a prompt 
and if you write ``(+ 1 2)`` you should get ``3``. To exit press ``ctrl+d`` or write ``exit``.

To start a new project you'll use ``lein new [template name] [project name]``. For example, to create a new app you'll write:
``lein new app leinapp``. You'll get a new directory called ``leinapp``. The important stuff in this directory are: 

* ``project.clj``: The basic descriptor of your project; here you can set various attrs of your project and also add dependencies
* src\\leinapp: The source directory of your project. This is where you'll put your code. 
* test\\leinapp: Add tests here
 
There should be a ``core.clj`` file inside your src\\leinapp folder. The ``main`` function is the entry point of the app. Try running 
``lein run`` from the project folder and you should get the output of the ``main`` function. 

Add this to the end of the ``core.clj`` to define a ``foo`` function: 

.. code-block:: clojure

    (defn foo []
      "bar")

And run ``lein repl``. You should get a repl command prompt for your application
in the ``leinapp.core`` namespace (if you named your app ``leinapp``). Type 
``(foo)`` and you should see ``"bar"``.

To create a stand alone jar with your code (called *uberjar*) you can use ``lein uberjar``. This will create a file 
named ``target\uberjar\leinapp-0.1.0-SNAPSHOT-standalone.jar``. Then try ``java -jar target\uberjar\leinapp-0.1.0-SNAPSHOT-standalone.jar``
(notice I'm still on the leinapp project folder) and you'll see the output of main!


clj
---

Using the clj is a more *modern* approach to clojure development. As I said before the official clojure page seems to be biased towards
using this approach. The problem is that it seems to require Powershell to run as you can see on the  `clj on Windows` page.

Thankfully, the good people at the clojurians_ slack pointed me to deps.clj_ project. This is an implementation of clj in clojure and
can be installed natively on Windows by downloading the .zip `from the releases page`_. This zip should contain a deps.exe file. Put 
that executable it in your path. You can also rename it to clj.exe if you want. Also if you have the powershell installed you can run this command from cmd.exe
``PowerShell -Command "iwr -useb https://raw.githubusercontent.com/borkdude/deps.clj/master/install.ps1 | iex"`` to install it automatically.

You can now run ``deps`` and you should get a clojure repl similar to ``lein repl``. 

To create a new project skeleton you can use the 
use the deps-new_ project. To install it run the following command from cmd.exe: 
``deps -Ttools install io.github.seancorfield/deps-new "{:git/tag """v0.4.9"""}" :as new`` (please notice that there are various 
`problems with the quoting on windows`_ but this command should work fine). 

To create a new app run: ``deps -Tnew app :name organization/depsapp`` and you'll get your app in the ``depsapp`` folder. If you want 
a similar form as with lein, try ``deps -Tnew app :name depsapp/core :target-dir depsapp``. Now the ``depsapp`` folder will contain:

* ``deps.edn``: The basic descriptor of your project; here you can set various attrs of your project and also add dependencies. This more or less changes the project.clj we got from leiningen.
* src\\depsapp: The source directory of your project. This is where you'll put your code. 
* test\\depsapp: Add tests here

To run the project, try: ``deps -M -m depsapp.core`` or 
``deps  -M:run-m`` or 
``deps  -X:run-x`` to directly run the greet function (``run-m`` and ``run-x`` are aliases defined in ``deps.edn`` take a peek).

To start a REPL, run ``deps``. Notice this will start on the ``user`` namespace, so you'll need to do something like:

.. code-block:: clojure

  user=> (require 'depsapp.core)
  nil
  user=> (depsapp.core/foo)
  "bar"

to run a ``(foo)`` function that you've added in the ``core.clj`` file.

To run the tests use: ``deps -T:build test``. 

To create the uberjar you'll run: 
``deps -T:build ci`` (tests must pass). Then execute it directly using 
``java -jar target\core-0.1.0-SNAPSHOT.jar``.

Also, notice that it's really simple to create a new project with deps without the deps-new. For example,
create a folder named ``manualapp`` and in this folder 
create a ``deps.edn`` file containing just the string ``{}``. Then add another folder named ``src`` with a  ``hello.clj`` file
containing something like:

.. code-block:: clojure

  (ns hello)

  (defn foo []
    "bar")

  (defn run [opts]
    (println "Hello world"))

You can then open a REPL on the project using ``deps`` or run the run function using ``deps -X hello/run``.

VSCode integration
------------------

Both leining and clj projects can easily be used with VSCode. First of all, install the calva package in your VSCode. Then, open your
clojure project in VScode and press ``ctrl+shift+p`` to bring up the command pallete. Here write "Jack" (from jack-in) and select it 
(also this has the shortctut ``ctrl+alt+c ctrl+alt+j``). Select the correct project type (``leiningen`` or ``deps.edn``). A repl 
will be opened to the side; you can then go to your core.clj file and run ``ctrl+alt+c enter`` to load the current file.

Then you can move to the repl on the side and run the function with ``(foo)`` or run ``(-main)``. Also you can write ``(foo)`` 
in your source file and press ``ctrl+enter`` to execute it and see the result; the ``ctrl+enter`` will execute the form where your 
cursor is. See this_ for more.



.. _`biased towards clj tools`: https://clojure.org/guides/getting_started
.. _`leiningen`: https://leiningen.org/
.. _`clj on Windows`: https://github.com/clojure/tools.deps.alpha/wiki/clj-on-Windows
.. _`clojurians`: https://clojurians.slack.com/
.. _deps.clj: https://github.com/borkdude/deps.clj
.. _`from the releases page`: https://github.com/borkdude/deps.clj/releases
.. _deps-new: https://github.com/seancorfield/deps-new
.. _`problems with the quoting on windows`: https://clojure.org/reference/deps_and_cli#quoting
.. _this: https://calva.io/try-first/