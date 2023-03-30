Title: Using Unpoly with Django
Date: 2023-03-22 15:20
Tags: python, django, unpoly, javascript
Category: django
Slug: using-unpoly-with-django
Author: Serafeim Papastefanos
Summary: A guide on using Unpoly with Django


Over the past few years, there has been a surge in the popularity of frontend frameworks, such as React and Vue. While there are certainly valid use cases for these frameworks, I believe that they are often unnecessary, as most web applications can be adequately served by traditional request/response web pages without any frontend framework. The high usage of these frameworks is largely driven by FOMO and lack of knowledge about alternatives. However, using such frameworks can add unnecessary complexity to your project, as you now have to develop two projects in parallel (the frontend and the backend) and maintain two separate codebases.

That being said, I understand that some projects may require extra UX enhancements, such as dynamic modals, navigation, and form submissions without full page reloads, or immediate form validation feedback. In such cases, the library 
[Unpoly](https://unpoly.com/)
can be a powerful tool for adding dynamic behavior to your pages without the need for a full-fledged frontend framework.

Unpoly is a JavaScript library that allows you to write dynamic web applications with minimal changes to your existing server-side code. It works by adding custom attributes to your HTML elements, which can then be used to trigger JavaScript behavior on the client side. This means you can add things like AJAX requests, form validation, and page transitions without needing to write much JavaScript.

Unpoly is similar to other libraries like intercooler, htmx or turbo however I find it to be the easiest to be used in the kind of projects I work on. 

In this guide, we'll go over how to use Unpoly with Django. Specifically, we'll cover the following topics:

* An unpoly demo
* Integrating unpoly with Django
* Navigation improvements
* Form improvements
* Modal improvements

## An unpoly demo

Unpoly provides a [demo application](https://demo.unpoly.com/) written in Ruby. I've re-implemented this in Django
so you can quickly take a peek at how Unpoly can improve your app. The code is at https://github.com/spapas/django-unpoly-demo
and the actual demo is at: https://unpoly-demo.spapas.net or https://unpoly-demo.onrender.com/ (deployed on render.com). Please
notice this site uses an ephemeral database so the data may be deleted at any time.

Try navigating the site and you'll see things like:

* Navigation feedback
* Navigation without page reloads
* Forms opening in modals
* Form submissions without page reloads
* Form validation feedback without page reloads

All this is implemented mostly with traditional Django class based views and templates in addition to a few unpoly attributes.

## Integrating unpoly with Django

To integrate unpoly with Django you only need to include the unpoly JavaScript and CSS library to your project. This is a normal .js file
that you can retrieve from the [unpoly install page](https://unpoly.com/install). Also, if you are using Bootstrap 3,4 or 5 I recommend
to also download the corresponding unpoly-bootstrapX.js file.

Unpoly communicates with your backend through custom X-HTTP-UP headers. You could use the headers directly however it is also possible to install the [python-unpoly](https://gitlab.com/rocketduck/python-unpoly)
library to make things easier. After installing that library you'll add the `unpoly.contrib.django.UnpolyMiddleware` in your `MIDDLEWARE` list resulting in an extra `up` attribute to your request. You can then use this `up` attribute through the [API](https://unpoly.readthedocs.io/en/latest/usage.html) for easier access to the unpoly headers.

To make sure that everything works, add the `up-follow` to one of your links, i.e change `<a href='linkto'>link</a>`
to <a up-follow href='linkto'>link</a>. When you click on this link you should observe that instead of a full-page reload
you'll get the response immediately! What really happens is that unpoly will make an AJAX request to the server, retrieve the response and render it on the current page making the response seem much faster! 

## Navigation improvements

Using the above technique, you can start adding `up-follow` to all your links and you'll get a much more responsive application.

One interesting thing is that we didn't need to change *anything* on the backend. The whole response will be retrieved by unpoly and 
will *replace* the `body` of the current page. Actually, it is possible to instruct unpoly to replace only a specific part of the page
using a css selector (i.e replace only the `#content` div). To do this you can add the `up-target` attribute to the link, i.e `<a up-target='#content' up-follow href='linkto'>link</a>`. When unpoly retrieves the response, it will make sure that it has an `#content` 
element and put its contents to the original page `#content` element.

This is called `linking to fragments` in the unpoly docs.

### Using the up-main

To make things simpler, you can declare an element to be the default replacement target. This is done by adding the `up-main` attribute to an element. This way, all `up-follow` links will replace that particular element by default unless they have an `up-target` element themselves.

What I usually do is that I've got a `base.html` template looking something like this:

```html
    {% include "partials/_nav.html" %}
    <div up-main class="container">
      {% include "partials/_messages.html" %}
      {% block content %}
      {% endblock %}
    </div>
    {% include "partials/_footer.html" %}
```    

See the `up-main` on my container. This way, all my `up-follow` links will replace the contents of the `.container` element by default. If I wanted to replace a specific part of the page, I could add the `up-target` attribute to the link.

### Make all links followable

It is possible to 

### Navigation feedback

