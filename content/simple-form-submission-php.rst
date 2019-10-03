How to properly handle an HTML form
###################################

:date: 2019-10-03 14:20
:tags: html, form, php
:category: html
:slug: html-form-submit-php
:author: Serafeim Papastefanos
:summary: An introductory tutorial on how to properly handle a form. PHP is used for pedagogical reasons.

One of the simplest things somebody would like to do in a web application is to display a form to the user and then handle the data the application
received from the form. This is a very common task however there are many loose ends and things that a new developer can do wrong. Recently, I tried
to explain this to somebody however I couldn't find a tutorial containing all the information I think it is important. So I decided to write it here.

To make it very easy to test it and understand it I decided to use PHP to handle the form submission. I must confess that I don't like PHP and I never
use it in production apps (unless I need to support an existing one). However, for such simple tasks and examples PHP is probably the easiest thing for
a new developer to understand: Just create a ``.php`` file and put it in a folder in your apache ``htdocs``; there now you can test the behavior!

This tutorial will be as comprehensive as possible and will try to explain all things that I feel that need explaining. However I won't go into details 
about HTML or PHP syntax; you'll need to know some things about them to understand what's going on here; after all the important thing is to understand
the big picture so you can re-implement them in your case (or understand why your web framework does what it does).

A quick HTTP primer
-------------------

So, what happens during a form display and submission? To properly understand that you need to know what an HTTP request is. An HTTP request is the way
the browser "requests" a URL from a web server. This is thoroughly explained in the HTTP protocol however, for our purposes here it should suffice to say
that an HTTP request is a text message that is send from the browser/HTTP Client to the HTTP/web server. This message should have the following format:

.. code::

  METHOD PATH HTTP/VERSION
  Header 1: Value 1
  Header 2: Value 2

  Request data

The ``METHOD`` can be one of various methods supported in the HTTP protocol like `GET, POST, PUT, OPTIONS` etc however the most popular and the ones we'll talk about here
are ``GET`` and ``POST``. The ``PATH`` is the actual url of the "page" you want to view without the server part. So if you are visiting ``http://www.example.com/path/to/page.html``
the path parameter will have a value of ``/path/to/page.html``. The ``HTTP/VERSION`` will contain the version of HTTP the client uses; usually it is something like
``HTTP/1.1``. Finally, after that first line there's a bunch of optional headers with various extra information the client wants to pass to the 
server (for example what encoding it supports, what's the host it connects to etc). 

Additionally, in case 
of a ``POST`` request the headers are followed by a blank line which in turn is followed by a chunk of "data" that the client passes to the server. 

The server will then response back with a text message similar to this (HTTP Response):

.. code::

  HTTP/VERSION STATUS
  Header 1: Value 1
  Header 2: Value 2

  Response data

The ``HTTP/VERSION`` will also be something like ``HTTP/1.1`` while the ``STATUS`` will be the status of the response. This status
is a 3-digit numeric value followed by a textual description of the
status. There are `various statuses that you can receive`_, however the statuses can be grouped by the number they start with like this:

* 1xx: Information; rarely used
* 2xx: Success; status 200 is the most common one
* 3xx: Redirection (browser must visit another page); either permanent or temporary
* 4xx: Client error; 404 is page not found (also access denied errors will be 40x)
* 5xx: Server error; something fishy happened to the server while responding

In this article we'll mainly talk about 2xx and 3xx: A ``200 OK`` answer is the most common one, it means that the HTTP request was
completed successfully. A ``302 FOUND`` request means that the browser should display a "different" path; that path will be provided in
a ``Location: path`` header. When the browser receives a redirect it will do another ``GET`` request to retrieve the redirect to page.

Notice that the Headers and Data parts of the server reply may also be optional like for the client however they usually exist 
(especially with a 200 response; without the data the client won't have anything to display). 

So when a browser "requests" a page it will send an HTTP ``GET`` to the path. This happens all the time when we visit(click) links or entering
urls to our browser. However, when we submit an HTML form the situation is a little more complex.

Form methods
------------

An html form is a ``<form>`` tag that contains a bunch of ``<input>`` elements each one of which should have *at least* a name property.
One of the inputs will usually be is a submit button.

Also, the form tag has two important attributes:

* ``action``: Defines the url where the post will be submitted to; it can be omitted to submit the form to the current path
* ``method``: Will be either GET or POST

Thus, a sample form is something like:

.. code-block:: html
  
  <form method="GET" action="form.php" >
    <input type='text' name='input1'>
    <input type='text' name='input2'>
    <input type='submit'>
  </form>

So what are the differences between a ``<form method='GET'>`` and a ``<form method='POST'>``?

* Submitting an HTML form will translate to either an HTTP GET request or an HTTP POST request to the server depending on the method attribute 
* The data of a GET form will be encoded in the PATH of the HTTP request while the data of the POST form will be in the corresponding data part of the HTTP Request
* A form that is submitted with GET should be idempotent i.e it should *not* modify anything in the server; a form that is submitted with POST should modify something the server

So, the form we defined previously (that has a GET method) will issue the following HTTP request (if we fill the values value1 and value2 to the inputs):

.. code::

  GET /form.php?input1=value1&input2=value2 HTTP/1.1

One the other hand if the form had a POST method the HTTP request would be like this:

.. code::

  POST /form.php HTTP/1.1

  input1=value1&input2=value2 

Notice that in the first case the data is in the PATH in the 1st line of the request while in the second case it is passed in the data section.
Also, in both cases the encoded data of the form is similar to ``input1=value1&input2=value2``: it is a list of ``key=value`` pairs seperated
with ``&`` where the ``name`` attribute of each ``input`` is used as the key.

Concerning the idempotency of the action; this is not something that the HTTP protocol can enforce but it relies on the developer to implement it.
When a form will not change anything to the server then it should be implemented as a method=GET. For example when you have a form with a search
box that just returns some results. On the other hand, when a form does change things for example when you create a new item in an application
then it should be implemented as a method=POST.

The browser has a different behavior after a GET vs after a POST because it expects that when you do a GET request then it won't matter if that
request is repeated many times. One the other hand, the browser will try to prevent you from submitting a request many times (because something is
changed in the server so the user must do it intentionally by for example pressing a button to submit the form). 

Proper form handling
--------------------

So, following the previous section we can now explain how to handle a form properly:

For a GET form we don't have to do anything fancy; we just retrieve the parameter values and we display the data these parameters correspond to
just like if we displayed any other page.

For a POST form however we need to be extra careful as to avoid re-duplication of data and have a good user experience: When a POST form is
submitted we need first to make sure that the submitted parameters are valid (for example there are no missing required fields). If the form is not
valid then we will return a status 200 OK explaining to the user what went wrong; we usually return the same page containing the initial form with
the fields that had errors marked. 

On the other hand, if the form *was valid* we need to do the actual action that the form corresponds to; for example insert something to the database.
After this is finished we should return a *redirect* (302) to either a different or even the same page. This will result to the browsing doing a
GET request to the page we redirect to so there would be no danger of the user refreshing the page and resubmitting the form. We should *not*
return a 200 OK after a POST request because then the user would be able to press F5 to duplicate the previous POST request (and re-insert the data).

One extra thing that we need to consider is how should we inform the user that his action was successful after the form submission and 
redirection? As we said, we can't return a 200 OK message so we can't really "create" the response, we instead need to redirect to another page.
A common practice for this is to use a "flash" message; this is offered by many web frameworks through specific functions
but can be easily implemented. I'll explain how in the next section.

Implementing flash messages
---------------------------

Before talking about the flash message I'd like to quickly explain what's a cookie and a browser session in HTTP, because
the flash message builds upon these concepts:

A cookie is a way for the server to tell the client to store some information to be re-used later. What happens is that
the server returns an HTTP header line similar to ``Set-Cookie: cookie-name=cookie-value``. When the client receives that
header line it will pass an HTTP header line similar to ``Cookie:  cookie-name=cookie-value`` to all future requests 
so the server will know which value it had send to the client (there are various options for expiring cookies etc but they
are not important here). This may seem like a primitive solution however because HTTP is a stateless protocol 
that's the only way for the server to store information about a client. If you disable cookies completely in a browser 
then there won't be a way for the server to remember you, for example you won't be able to login anywhere!

A session is a better way to store info about the client that builds upon the cookies. What happens is that when a client visits
a site for the first time (so it has no cookies for that particular site) the server will send back a cookie named ``session_id`` (or something like
that) containing a very big random number. The server will save this session id number in a persistent storage (for example in a
database or a text file) and will correlate that number with information for that particular client. When the client sends back that 
``session_id`` cookie the server will fetch the correlated info for that particular client from the persistent storage (and may
update them etc). This way the server can store whatever info it wants about a particular client. The server usually keeps a
a dictionary (map) of key-values for each session.

Now, a flash message is some information (message) that should be displayed to the user *once*. For example a message like 
"Your form has been submitted!".

A simple way to implement this is to add a ``message`` 
attribute to the session when you want to display the flash message. The next page that is displayed (irrelevantly if there's a redirect involved)
will check to see if there's a ``message`` attribute to the session; if yes it will display the actual message and remove the ``message`` attribute
from the session (so it won't be displayed again). 

Implementing the form submission
--------------------------------

Following the above guidelines I'll present here a typical, production-ready form submission for PHP. Some choices I've made:

* I am going to implement a POST form since a GET form doesn't need any special handling
* The form handler will be the same PHP page as the one displaying the form. This is a usual thing to do, you check the HTTP method and either display the form as-is (if it is GET) or handle the submission (if it is POST)
* When the form is submitted successfully redirect to the same page and display a flash message
* Check for valid input and display the error message

So without further ado here's the complete php code that will submit your form; store it in a file named ``test.php``:

.. code-block:: php

  <!DOCTYPE HTML>
  <html>

  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>TEST FORM</title>
    <link href="https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css" rel="stylesheet">
  </head>

  <body class="bg-gray-100">
    <div class="px-8 py-8 w-1/2 m-auto">

      <?php
      session_start();
      if ($_SESSION['message'] ?? '') {
        echo '<div class="rounded bg-green-300 px-2 py-2">'.$_SESSION['message'].'</div>';
        unset($_SESSION['message']);
      }

      $nameErr = $wsErr = $name = $comment = "";
      $formValid = true;

      if ($_SERVER["REQUEST_METHOD"] == "POST") {
        if (empty($_POST["name"])) {
          $nameErr = "Name is required";
          $formValid = false;
        } else {
          $name = $_POST["name"];
        }

        if (empty($_POST["comment"])) {
          $comment = "";
        } else {
          $comment = $_POST["comment"];
        }

        if ($formValid) {
          if (1 == rand(1, 2)) {
            $_SESSION['message'] = "Success! You have submitted the values: <b>" . $name . " / " . $comment . "</b>";
            header('Location: ./test.php');
            exit();
          } else {
            $wsErr = "Error while trying to submit the form!";
          }
        }
      }
      ?>

      <h1 class="text-4xl font-bold text-indigo-500">Test a PHP form!</h1>
      
      <form class='border border-blue-800 rounded p-2' method="POST">

        <?= $wsErr ? "<div class='text-red-600 py-3'>" . $wsErr . "</div>" : "" ?>

        <div class="p-1">
          <label for="name">Name:</label> <input class="border border-blue-800 rounded" id="name" type="text" name="name" value="<?= $name ?>">
          <span class="text-red-600">* <?= $nameErr; ?></span>
        </div>

        <div class="p-1">
          <label for="comment">Comment:</label> <textarea class="border border-blue-800 rounded" id="comment" name="comment" rows="5" cols="40"><?= $comment ?></textarea>
        </div>

        <input class="rounded px-2 my-4 py-2 bg-blue-800 text-gray-100" type="submit" name="submit" value="Save">
      </form>
    </div>
  </body>
  </html>
  
So how is that working? As we can see there's the php code first and the html is following (with some sprinkles of php). The HTML code is rather simple: It will
display a ``POST`` form with two inputs named ``name`` and ``comment``. Notice that we pass the ``$name`` and ``$comment`` php variables as their values.
It also has a submit button and will display the ``$wsErr`` variable if it is not null (which means that there was an error while submitting the data). The PHP
code now first starts the session (i.e it passes the ``session_id`` cookie to the client if such a cookie does not exist) checks to see if there's a 
``message`` attribute to the session. If such a message exists it will display it in a rounded green panel and remove that from the session (so it won't be displayed
again next time):

.. code-block:: php
      
  session_start();
  if ($_SESSION['message'] ?? '') {
    echo '<div class="rounded bg-green-300 px-2 py-2">'.$_SESSION['message'].'</div>';
    unset($_SESSION['message']);
  }

After that there are some variable initializations and we check if the HTTP request is ``POST`` (if the request is GET we'll just disply the HTML):

.. code-block:: php

  if ($_SERVER["REQUEST_METHOD"] == "POST") {

For each of the inputs we check if they are empty or not and assign their values to the corresponding php variable. If the name is empty then we'll
set ``$formValid = false;`` and add an error message since this field is required. Then, if ``$formValid`` is not false we can do the actual action
(for example write to the database). I've simulated that using a coin-toss with rand (so there's a 50% possibility that the action will fail). If 
the action "failed" then nothing happened in the database so we should return the same page with the ``wsErr`` variable containing the error.

However if the action is successful that means that the data has been inserted to the database so we'll need to set the flash message and do
the redirect (the name of the page containing the form is ``/test.php`` so we'll redirect to it):

.. code-block:: php

  $_SESSION['message'] = "Success! You have submitted the values: <b>" . $name . " / " . $comment . "</b>";
  header('Location: ./test.php');
  exit(); 

The two commands above (``header`` and ``exit``) will do the actual redirect in php. Since the session contains the ``message`` it will
be displayed after the redirect has finished!


Conclusion
----------

So following the above tutorial, here's what you should absolutely do to submit an HTML form:

* Use HTTP POST if the form is going to change data on the server; use HTTP GET otherwise (mainly for search/filter forms)
* When using POST: Redirect when the form is valid and the action on the server has finished successfully; never return a 200 OK status when you've changed things in the server (database)
* Use flash messages to pass information to the user after a redirect


.. _`easily overriden`: https://docs.djangoproject.com/en/1.8/topics/http/views/#the-http404-exception
.. _`see here`: https://docs.djangoproject.com/el/2.1/ref/views/#django.views.defaults.page_not_found
.. _`various statuses that you can receive`: https://httpstatuses.com/