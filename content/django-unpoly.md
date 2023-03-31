Title: Using Unpoly with Django
Date: 2023-03-31 15:20
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
* Modal improvements (layers)

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

## Unpoly configuration

The main way to use unpoly is to add `up-x` attributes to your html elements to enable unpoly behavior. However it is possible to use the unpoly js API (`up`) to set some global configuration. For example, you can use `up.log.enable()` and `up.log.disable()` to enable/disable the unpoly logging to your console. I recommend enabling it for your development environment because it will help you debug when things don't seem to be working. 

To use `up` to configure unpoly you only need to add it on a `<script>` element after loading the unpoly library, for example:

```html
<script src="{% static 'unpoly/unpoly.min.js' %}"></script>
<script src="{% static 'unpoly/unpoly-bootstrap4.min.js' %}"></script>
<script src="{% static 'application.js' %}"></script>
```

And in `application.js` you can use `up` directly, for example to enable logging:

```javascript
  up.log.enable()
```  

We'll see more `up` configuration directives later, however keep in mind that for most `up-x` attributes it is possible to use the config to automatically add that attribute to multiple elements.

## Navigation improvements

Using the above technique, you can start adding `up-follow` to all your links and you'll get a much more responsive application.

One interesting thing is that we didn't need to change *anything* on the backend. The whole response will be retrieved by unpoly and 
will *replace* the `body` of the current page. Actually, it is possible to instruct unpoly to replace only a specific part of the page
using a css selector (i.e replace only the `#content` div). To do this you can add the `up-target` attribute to the link, i.e `<a up-target='#content' up-follow href='linkto'>link</a>`. When unpoly retrieves the response, it will make sure that it has an `#content` 
element and put its contents to the original page `#content` element.

This is called `linking to fragments` in the unpoly docs. To see this in action, try going to the tasks in the demo and add a couple of new task. Then try to edit a that task. You'll notice that the edit form of the task will *replace* the task show card! To do that, unpoly loads the edit task form and matches the `.task` element there with the *current* `.task` element and does the replacement (see [here](https://unpoly.com/fragment-placement#interaction-origin-is-considered) for rules on how this works). 

Beyond the `up-follow`, you can also use two more directives to further improve the navigation: 

* `up-instant` to follow the link on mousedown (without waiting for the user releasing the mouse button)
* `up-preload` to follow the link when the mouse hovers over the link

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

See the `up-main` on the `.container`. This way, all my `up-follow` links will replace the contents of the `.container` element by default. If I wanted to replace a specific part of the page, I could add the `up-target` attribute to the link.

If there's no `up-main` element, unpoly will replace the whole `body` element.

### Make all links followable

It is possible to make all links (or links that follow a selector) [followable by default](https://unpoly.com/handling-everything#following-all-links) by using the `up.link.config.followSelectors` option. 
I would recommend to only do this on greenfield projects where you'll test the functionality anyway. For existing projects I think it's better to add the `up-follow` attribute explicitly to the links you want to make followable.

This is recommend it because there are cases where using unpoly will break some pages, especially if you have some JavaScript code that relies on the page being reloaded. We'll talk about this in the troubleshooting section.

If you have made all the links followable but you want to skip some links and do a full page reload instead, add the `up-follow=false` attribute to the link or use the `up.link.config.noFollowSelectors` to make multiple links non-followable.

You can also make all links instant or preload for example by using `up.link.config.instantSelectors.push('a[href]')` to make all followable links load on mousedown. This should be safe because it will only work on links that are [already followable](https://unpoly.com/handling-everything#following-all-links-on-mousedown). 

### Navigation feedback

One very useful feature of unpoly is that it adds more or less *free* [navigation feedback](https://unpoly.com/up.feedback). This can be enabled by adding an `[up-nav]` element to the navigation section of your page. Unpoly then will add an `up-current` class to the links in that section that match the current URL. This works no matter if you are using `up-follow` or not. You can then style `.up-current` links as you want.

If you are using Bootstrap along with the unpoly-bootstrap integrations you'll get all that without any extra work. The unpoly-bootstrap has the following configuration:

```javascript
up.feedback.config.currentClasses.push('active');
up.feedback.config.navSelectors.push('.nav', '.navbar');
```

So it will automatically add the `up-nav` element on `.nav` and `.navbar` elements and will add the `active` class to the current link (in addition to the `.up-current` class). This is what happens in the demo, if you take a peek you'll see that there are no `up-nav` elements in the navigation bar and we style the `.active` nav links.

### Aliases for navigation feedback

Unpoly also allows you to add aliases for the navigation feedback. For example, you may have `/companies/` and `/companies/new` and you want the `companies` nav link to be active on both of them. To allow that you need to use the `up-alias` attribute on the link like 


```html
<a class='nav-item nav-link' up-follow href='{% url "company-list" %}' up-alias='{% url "company-list" %}new'>Companies</a>
```

(notice that in my case the url of `company-list` is `/companies/` that's why I added `{% url "company-list" %}new` on the alias), or even add multiple links to the alias

```html
<a class='nav-item nav-link' up-follow href='{% url "company-list" %}' up-alias='{% url "company-list" %}*'>Companies</a>
```

This will add the `up-current` class to the `a` element whenever the url starts with `/companies/` (i.e `/companies/`, `/companies/new`, `/companies/1/edit` etc).

Please notice that it is recommended to have a proper url hierarchy for this to work better. For example, if you have `/companies_list/` and `/add_new_company/` you'll need to add the aliases like `up-alias='/companies_list/ /add_new_company/'` (notice the space between the urls). Also, if you want to also handle URLS with query parameters i.e `/companies/?name=foo` then you'll need to add `?*` i.e `/companies/?*`.

One final remark is that it is possible to do some trickery to automatically add up-alias to all your nav links, for example, using this code:

```javascript
  up.macro('nav a[href]', (link) => {
    if(!link.href.endsWith('#')) link.setAttribute('up-alias', link.href + '*')
  })
```

an `up-alias` attribute will be added to all links. The callback of the macro will be called when the selector is matched and
in this case add the `up-alias` attribute to the link. Notice that we use `up.macro` to run this code
[before unpoly compilers](https://unpoly.com/up.macro). We'll talk later about compilers.

## Handling forms

Unpoly can also be used to handle form without page reloads. This is simple to do by adding an `up-submit` attribute to your form. Similar to links you can make [all your forms handled by unpoly](https://unpoly.com/handling-everything#handling-all-forms) but I recommend to be cautious before doing this on existing projects to make sure that stuff doesn't break.

When you add an `up-submit` to a form unpoly will do an AJAX post to submit the form and replace the contents of the `up-target` element with the response (if you don't specify an `up-target` element, it will use the `up-main` element in a similar way as links). This works fine with the default Django behavior, i.e when the form is valid Django will do a redirect to the success url, unpoly will follow that link and render the response of the redirect.

### Integrating with messages

Django has the [messages framework](https://docs.djangoproject.com/en/stable/ref/contrib/messages/) that can be used to add one-time messages
after a form is successfully submitted. You need to make sure that these messages are actually rendered! For example, in the `base.htm` template I mentioned before, we've got the following:


```html
    {% include "partials/_nav.html" %}
    <div up-main class="container">
      {% include "partials/_messages.html" %}
      {% block content %}
      {% endblock %}
    </div>
    {% include "partials/_footer.html" %}
```

please notice that we've got the `partials/_messages.html` template included in the `up-main` element (inside the container). This means that when unpoly replaces the contents of the `up-main` element with the response of the form submission, the messages will be rendered as well. So it will work fine in this case. However, if you are using `up-target` to render only particular parts of the page the flash messages will be actually lost! This happens because unpoly will load the page with the flash messages normally, so these messages will be consumed; then it will match the `.target` and display *only* that part of the response.

To resolve that you can use the `up-hungry` attribute on your messages. For example, in the `partials/_messages.html` template we've got the following:

```html
<div class="flash-messages" up-hungry>
    {% for message in messages %}
        <div class="alert fade show {% if message.tags %} alert-{% if 'error' in message.tags %}danger{% else %}{{ message.tags }}{% endif %}{% endif %}">
            {{ message }}
        </div>
    {% endfor %}
</div>
```

The `up-hungry` attribute will make unpoly refresh that particular part of the page on every page load [even if it's not on the target](https://unpoly.com/up-hungry). For example notice how the message is displayed when you edit or mark as done an existing task in the demo. 

However also notice that no messages are displayed if you create a new task! This happens because the actual response is "eaten" by the layer and the messages are discarded! We'll see how to fix that later.

### Immediate form validation

Another area in which unpoly helps with our forms is that if we add the `up-validate` attribute to our form, unpoly will do an AJAX post to the server whenever the input focus changes and will display the errors in the form without reloading the page. For this  we need a little modification to our views to check if the unpoly wants to validate the form. I'm using the following `form_valid` on a form mixin:

```python
def form_valid(self, form):

    if form.is_valid() and not self.request.up.validate:
        if hasattr(self, "success_message"):
            messages.success(self.request, self.success_message)
        return super().form_valid(form)
    return self.render_to_response(self.get_context_data(form=form))
```

So if the form is not valid or we get an unpoly validate request from unpoly we'll render the response - this will render the form with or without errors. However if the form is actually valid and this is not an unpoly validate request we'll do the usual form save and redirect to the success url. This is enough to handle all cases and is very simple and straightforward. It works fine without unpoly as well since the `up.validate` will be always `False` in this case.

One thing to keep in mind is that this works fine in most cases but may result to problematic behavior if you use components that rely on javascript onload events. The `up-validate` will behave more or less the same as with `up-follow` links. We'll cover this more on the troubleshooting.

### Other form helpers

Beyond these, unpoly offers a [bunch of form helpers](https://unpoly.com/up.form) to run callbacks or auto-submit a form when a field is changed. Most of this functionality can be replicated by other js libraries (i.e jquery) or even by vanilla.js and is geared towards the front-end so I won't cover it more here.

## Using layers

One of the most powerful features of unpoly is [layers](https://unpoly.com/up.layer). A layer is an overlay that can be rendered like a modal / popup / drawer. 



