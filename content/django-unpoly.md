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

One of the most powerful features of unpoly is [layers](https://unpoly.com/up.layer). A layer is an overlay that can be rendered like a modal / popup / drawer. The simplest way to use a layer is to add an `up-layer='new'` attribute to a link. For example, in the demo app, the link to open a company is like this:

```html
  <a
    up-layer='new'
    up-on-dismissed="up.reload('.table', { focus: ':main' })"
    up-dismiss-event='company:destroyed'
    href="{% url 'company-detail' company.id %}">{{ company.name }}</a>
```

(ignore the other dismiss-related attributes for now). This opens a new modal dialog with the contents of the company detail. It will render the `up-main` inside the modal since we don't provide an `up-target`. If we added an `up-target='.projects'` attribute to this it would render *only* the `.projects` element inside the modal (but remember that it will retrieve the *whole* response since the /companies/detail/id is a normal django DetailView).

You can use `up-mode` attribute to [change the kind of overlay](https://unpoly.com/layer-terminology#available-modes); the default is a `modal`. Also if you want to configure the ways this modal closes you can use the 
`up-dismissable` [attribute](https://unpoly.com/closing-overlays#customizing-dismiss-controls), for example add 
`up-dismissable='button'` to allow closing only with the X button on the top right. Another useful thing is that there's an 
`up-size` attribute for changing the [size of the overlay](https://unpoly.com/customizing-overlays#overlay-sizes).

### Static layers content

A layer can also contain "static" content (i.e not follow a link) by using the `up-content` [attribute](https://unpoly.com/a-up-follow#up-content). This is how the green dots are actually implemented, their html is similar to this:

```html
<a href="#" class="tour-dot viewed" up-layer="new popup" up-content="<p>Navigation links have the <code>[up-follow]</code> attribute. 
        <p>
            <a href=&quot;#&quot; up-dismiss class=&quot;btn btn-success btn-sm&quot;>OK</a>
        </p>
        " up-position="right" up-align="top" up-class="tour-hint" up-size="medium">
        </a>
```

This is implemented in Django using the following template tag:

```python

@register.tag("tourdot")
def do_tourdot(parser, token):
    nodelist = parser.parse(("endtourdot",))
    parser.delete_first_token()
    return TourDotNode(nodelist)


class TourDotNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        rendered = self.nodelist.render(context).strip()
        size = "medium"
        if len(strip_tags(rendered)) > 400:
            size = "large"
        if not rendered.startswith("<p"):
            rendered = "<p>{}</p>".format(rendered)

        rendered += """
        <p>
            <a href="#" up-dismiss class="btn btn-success btn-sm">OK</a>
        </p>
        """
        from django.utils.html import escape

        output = escape(rendered)
        return """
        <a 
            href="#" 
            class="tour-dot"
            up-layer="new popup"
            up-content="{}"
            up-position="right"
            up-align="top"
            up-class="tour-hint"
            up-size="{}"
            >
        </a>
        """.format(
            output, size
        )
```

So we can do something like

```html
{% tourdot %}
  <p>Navigation links have the <code>[up-follow]</code> attribute. Clicking such links only updates a <b>page fragment</b>. The remaining DOM is not changed.</p>
{% endtourdot %}
```

### Advanced layers

Opening layers for popups or for viewing links that doesn't have interactivity is simple. However, when you open forms with layers 
and need to handle these the situation unfortunately starts to get more complex. I recommend to start by reading the 
[subinteractions](https://unpoly.com/subinteractions) section of the unpoly documentation to understand how these things work. Then we'll talk about specific cases and how to handle them with layers and django. In the next sections we'll see some of these cases and how to handle them with Django.

### Opening new layers *over* existing ones

How open a new layer *over* an existing layer (i.e a modal inside a modal) would work? All links and forms that are handled in an existing layer will be handled in the same layer. If we want to open a new layer we need to use the `up-layer='new'` attribute on that link. In the demo, if you click on an existing company to see its details you'll get a layer. If you try to edit that company the edit for will be opened *in the same layer* (notice that if you press the X button to close it you'll go back to the company list without layers). Compare this with the behavior when adding a new project or viewing an existing one. You'll get a layer *inside* a layer (both layers should be visible). You need to close both layers to go back to the company detail. 

Even more impressive: Go to the company detail layer, click an existing project to get to the project detail layer, click *edit*; this will be opened on the *project detail* layer! All this also works fine from the project detail list *without* any modifications! Also if you use the links directly (which will not open a layer you'll also get the proper behavior).

The thing to remember here is that the layer behavior is very intuitive and is compatible with how a server side application works. Everything should work the same no matter if the link is opened in an overlay or in a new page. My recommendation when working with layers is to make sure that the links work fine when are opened on an overlay and when are opened on a new page (by using the URL directly). 

### Closing layers

There are three main ways to [close the layer](https://unpoly.com/closing-overlays) (beyond of course using the (X) button or esc etc):

* Visiting a pre-defined link
* Explicitly closing the layer from the server
* Emitting an unpoly event

Also, when a layer is closed we can decide if the layer did something (i.e the user saved the form) or not (i.e the user clicked the X button). This is called `accepted` or `dismissed` respectively. We can use this to do different things. All the methods of closing a layer have a version for accepting or dismissing the layer.


#### Closing the layer on visiting a link

To close the layer on visiting a link we'll use the `up-accept-location` and `up-dismiss-location` respectively. For example, let's take a peek on the new company link:

```html
  <a
    class='btn btn-primary'
    up-layer='new'
    up-on-accepted="up.reload('.table', { focus: ':main' })"
    up-accept-location='/core/companies/detail/$id/'
    href='{% url "company-create" %}'>New company</a>
```

The important thing here is the `up-accept-location`. When Django creates a new object it redirects to the detail view of that object. In our case this detail view is `'/core/companies/detail/$id/'`; the `$id` is an unpoly thingie that will be replaced by the id of the new object and will be [the result value of the overlay](https://unpoly.com/closing-overlays#overlay-result-values). This value (the id) can then be used on the `up-on-accepted` callback if we want.

Now, let's suppose that we want to close the layer when the user clicks on a *cancel* button that returns to the list of companies. We can do that by adding the `up-dismiss-location` attribute to that `<a>`

```html
up-dismiss-location='{% url "company-list" %}'
```

The difference between these two is that the `up-on-accepted` event will only be called when the overlay is accepted and not on dismissed.

#### Handling hardcoded urls

One thing that Django developers may not like is that the url is hardcoded here. This is because using `{% url "company-detail" "$id" %}` will not work with our urls since we use have the following path for the company detail `"companies/detail/<int:pk>/"`. We can change it to `"companies/detail/<str:pk>/",` to make it work but then it will allow strings in the url and it will throw 500 error instead of 404 when the user uses a string there (to improve that we have to override the `get_object` of the `DetailView` to handle the string case). Another way to improve that is to create a urlid template tag like this:

```python
from django.urls import reverse

@register.simple_tag
def urlid(path, arg):
    if arg == "$id":
        arg = 999
    
    url = reverse(path, args=[arg])
    return url.replace("999", "$id")
```

And then using it like this on the up-accept-location:

```html
up-accept-location='{% urlid "company-detail" "$id" %}'
```

#### Explicitly closing the layer

To close the layer from the server you can you use the

or [`X-Up-Dismiss-Layer`](https://unpoly.com/X-Up-Dismiss-Layer)
response header. When unpoly sees this header in a response it will close the overlay by accepting/dismissing it.

To do that from Django you can have integrated the unpoly middleware call `request.up.layer.accept()` and `request.up.layer.dismiss()` respectively (passing
an optional value if you want).

The same can be used to close the layer from the client side. For example, if you want to close the layer when the user clicks on a *cancel* button that returns to the list of companies you can do that by adding the `up-accept` or `up-dismiss` attribute, like:

```html
<a href='{% urlid "company-detail" "$id" %}' up-dismiss>Return</a>
```

Please notice that the `href` here could be like `href='#'` since this is javascript only, however we added the correct href to make sure the return button will also work when we open the link in a new page (without any layer). Please notice that difference between this and `up-accept-location` or `up-dismiss-location` we mentioned before. In this case the `up-accept/dismiss` directive in placed in the a link that *closes* the overlay. In the former case the `up-accept/dismiss-location` directive is placed in the link that *opens* the overlay.

#### Closing the layer by emitting an unpoly event

The final way to close an overlay is by emitting an event. Unpoly can emit events both from the server, using the [`X-Up-Event`](https://unpoly.com/X-Up-Events) response header or using `request.up.emit(event_type, data)` from the unpoly Django integration. Also events can be emitted from the client side using [`up-emit`](https://unpoly.com/up.emit).

To close the overlay from an event we need to use `up-accept-event` and `up-dismiss-event`.

Let's see what happens when we delete a company. We've got a form like this:

```html
<form up-submit up-confirm='Really?' class="d-inline" method='POST' action='{% url "company-delete" company.id %}'>
  {% csrf_token %}
  <input type='submit' value='Delete' class='btn btn-danger mr-3' />
</form>

This form asks the user for confirmation (using the `up-confirm` directive) and then submits the form on the company delete view. The `CompanyDeleteView` is like this:

```python
class CompanyDeleteView(DeleteView):
    model = models.Company

    def get_success_url(self):
        return reverse("company-list")

    def form_valid(self, form):
        self.request.up.layer.emit("company:destroyed", {})
        return super().form_valid(form)
````        

So, it will emit the `company:destroyed` event and redirect to the list of companies (this is needed to make sure that delete works fine if we call it from a full page instead of an overlay). When we call it from an overlay it will be from the following tag to display the company detail view:

```html
            <a
              up-layer='new'
              up-on-dismissed="up.reload('.table', { focus: ':main' })"
              up-dismiss-event='company:destroyed'
              href="{% url 'company-detail' company.id %}">{{ company.name }}</a>
```              

Notice that we have the `up-dismiss-event` here. If we didn't have that then the overlay wouldn't be closed when we deleted the company but we'd see the list of companies because of the redirect! Also, instead of the `up-dismiss-event` we could use the `up-dismiss-location='{% url "company-list" %}'` similar to how we discussed before. If we did it this way we wouldn't even need to do anything unpoly related in our DeleteView, however using events for this is useful for educational reasons.


### Doing stuff when a layer is closed

After a layer is closed (and depending if it was accepted or dismissed) unpoly allows us to use callbacks to do stuff. The most obvious things are to reload the list of results if a result is added/edited/deleted or to choose a result in a form if we used the overlay as an object picker.

The callbacks are `up-on-accepted` and `up-on-dismissed`.

Let's see some examples from the demo.

On on the new company link we've got `up-on-accepted="up.reload('.table', { focus: ':main' })"` . However on the show details company link we've got `up-on-dismissed="up.reload('.table', { focus: ':main' })"`. This is a little strange at first but we can explain it. First of all, the [up.reload](https://unpoly.com/up.reload) method will do an HTTP request and reload that specific element from the server (in our case the `.table` element that contains the list of companies). The focus option that is passed instructs unopoly to move the focus to (that element)[https://unpoly.com/focus-option]. For the "Add new" company we reload the companies when the form is accepted (when the user clicks on the "Save" button). However for the show details we'll reload every time the overlay is dismissed because when the user edits a company the layer will not be closed but will display the edit company data. Also when we delete the company the layer will be dismissed. Notice that if the user clicks the company details and then presses the (X) button *we'll still do a reload* even though it's not needed because we can't know if the user actually edit a company or not. This is a little bit of a tradeoff but it's not a big deal.

On the company detail we've got `up-on-accepted='up.reload(".projects")'` for adding a new project but (same as before we've got `up-on-dismissed='up.reload(".projects")'`). The `.projects` element is the projects holder inside the company detail. This is exactly the same as the project list but with `up.reload('.table', { focus: ':main' })`  instead of `.projects`.

On the project form we've got `up-on-accepted` both on the suggest name and on the new company button. In the first case, we are opening the name suggestion overlay like this:

```html
<a
    up-layer='new popup'
    up-align='left'
    up-size='large'
    up-accept-event='name:select'
    up-on-accepted="up.fragment.get('#id_name').value = value.name"
    href='{% url "project-suggest-name" %}'>Suggest name</a>
```

Notice that this overlay will be accepted when it receives the `name:select` event. This event passes it the selected name so it will  put it on the `#id_name` input. The [`up.fragment.get`](https://unpoly.com/up.fragment.get) is used to retrieve the input. To understand how this works we need to also see the name suggestion overlay. This is more or less similar to:

```html
  {% for n in names %}
    <a up-emit="name:select"
       up-emit-props='{"name": "{{ n }}"}'
       class="btn btn-info text-light mb-2 mr-1"
       tabindex="0">
      {{ n }}
    </a>
  {% endfor %}
```

So we are using the `up-emit` directive here to emit the `name:select` event *and* we pass it some data which must be a json object. Then this data will be available as a javascript object named `value` on the `up-on-accepted` callback.

This may seem a little complex at first but it isn't after you understand it:

1. We open a new overlay and wait for the `name:select` event to be emitted. We don't care if we are a full page or already inside an overlay
2. The overlay displays a link of client side `<a>` elements that emit the `name:select` event when clicked and also pass the selected name
3. The overlay opener receives the `name:select` event and closes the overlay. It then uses the data to fill an input

The second case is similar but instead of filling an input it opens a new overlay to create and select a new company. This is the create company link from inside the project form:

```html
  <a href='{% url "company-create" %}'
      up-layer='new'
      up-accept-location='{% urlid "company-detail" "$id" %}'
      up-on-accepted="up.validate('form', { params: { 'company': value.id } })"
  >
      New company
  </a>
```

Nothing extra is needed from the company form side! We use the `up-accept-location` to accept the overlay when the company is created (so the user will be redirect to the company-detail view). Then we call the following after the overlay is accepted: `up.validate('form', { params: { 'company': value.id } })`. First of all, please remember that when we use the `up-accept-location` the overlay result 
[will be an object with the captured parts of the url](https://unpoly.com/a-up-layer-new#up-accept-location). In this case we capture the new company id. Then, we call `up.validate` passing it the form and the company id we just retrieved.

It is important that we do `up.validate` here instead of simply setting the value of the select to the newly created id (similar to what we did before with the name) because the newly created value *is not* in the options that this select contains so it can't be picked! If we wanted to do that instead we'd need to first add a new option to the select with the correct id and then set it to that value (which is a little bit more complex since we don't know the name fo the new company at this point).



### Layers and messages

## Troubleshooting