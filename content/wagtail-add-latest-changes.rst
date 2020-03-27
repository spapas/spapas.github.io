Adding a latest-changes list to your Wagtail site
##################################################

:date: 2020-03-27 14:20
:tags: django, wagtail
:category: wagtail
:slug: wagtail-add-latest-changes
:author: Serafeim Papastefanos
:summary: How to add a list of the latest changes to your wagtail site


I think that a very important tool for a new production Wagtail_ site is to have a list
where you'll be able to take a look at the latest changes. Most editors are not 
experienced enough when using a new tool so it's easy to make bad quality edits. A 
user could take a look at their changes and guide them if something's not up to good standards.

In this article I'll present a simple way to add a latest-changes list in your Wagtail site.
This is working excellent with Wagtail 2.8, I haven't tested it with other wagtail versions
so your milage may vary. In the meantime, I'll also introduce a bunch of concepts of Wagtail
I find interesting.


A starter project
-----------------

Let's create a simple wagtail-starter project (this is for windows you should be able to easily follow the same steps in Unix like systems):


.. code:: 

  C:\progr\py3>mkdir wagtail-starter
  C:\progr\py3>cd wagtail-starter
  C:\progr\py3\wagtail-starter>py -3 -m venv venv
  C:\progr\py3\wagtail-starter>venv\Scripts\activate
  (venv) C:\progr\py3\wagtail-starter>pip install wagtail
  (venv) C:\progr\py3\wagtail-starter>wagtail.exe start wagtail_starter
  (venv) C:\progr\py3\wagtail-starter>cd wagtail_starter
  (venv) C:\progr\py3\wagtail-starter\wagtail_starter>python manage.py migrate
  (venv) C:\progr\py3\wagtail-starter\wagtail_starter>python manage.py createsuperuser
  (venv) C:\progr\py3\wagtail-starter\wagtail_starter>python manage.py runserver

When you've finished all the above you should be able to go to http://127.0.0.1/ and see your homepage and then
visit http://127.0.0.1/admin/ and login with your superuser. What we'd like to do is add a "Latest changes"
link in the "Reports" admin section like this:

.. image:: /images/latest-changes-template.png
  :alt: New menu
  :width: 580 px

Implementing the latest-changes menu
------------------------------------

Start with a new app
====================

To start the menu implementation I recommend putting everything related to it in a separate django application
so you can easily re-use it to multiple sites. For this, let's create a new django app using:

.. code:: 

  (venv) C:\progr\py3\wagtail-starter\wagtail_starter>python manage.py startapp latest_changes

And add ``'latest_changes'`` to the list of our ``INSTALLED_APPS`` at the file ``wagtail_starter\settings\base.py``.

Add the view
============

Let's add the code for the view that will display the latest changes page. Modify the latest_changes/views.py file like this:

.. code:: 

  from django.shortcuts import render
  from wagtail.admin.views.reports import ReportView
  from wagtail.core.models import UserPagePermissionsProxy
  from wagtail.core.models import Page


  class LatestChangesView(ReportView):
      template_name = "reports/latest_changes.html"
      title = "Latest changes"
      header_icon = "date"

      def get_queryset(self):
          self.queryset = Page.objects.order_by("-last_published_at")
          return super().get_queryset()

      def dispatch(self, request, *args, **kwargs):
          if not UserPagePermissionsProxy(request.user).can_remove_locks():
              return permission_denied(request)
          return super().dispatch(request, *args, **kwargs)


As you can see the above code adds a very small view that overrides ``ReportView`` which is used
also by the locked pages view so most things are already implemented by that view. The only thing we do
here is to override the ``get_queryset`` method to denote which pages we want to display and 
the ``dispatch`` to add some permission checks. Here we check that a user ``can_remove_locks`` but we
could do other checks if needed. Finally, notice that we have overriden the template name which we'll
define in a minute.

To properly add that view in our urls.py we can use a wagtail hook named ``register_admin_py``. Wagtail hooks
are a great way to excend the wagtail admin; to use them, you have to generate a file name ``wagtail_hooks.py``
in one of your apps. This file will be auto-impoted by wagtail when your app is started.

Thus, in our case we'll add a ``wagtail_hooks.py`` file in the ``latest_changes`` app with the following code:

.. code::

  from django.http import HttpResponse
  from django.conf.urls import url
  from wagtail.core import hooks
  from .views import LatestChangesView

  @hooks.register('register_admin_urls')
  def urlconf_time():
    return [
      url(r'^latest_changes/$', admin_view, name='latest_changes'),
    ]

The above just hooks up the ``LatestChangesView`` we defined before to the ``/admin/latest_changes/`` url. 

If everything's ok till now you should be able to visit: http://127.0.0.1:8000/admin/latest_changes/ and 
get an error for a missing template - remember that we haven't yet defined ``utils/reports/latest_changes.html``.

Add the template
================

To add the template we'll need to create a folder named ``templates`` under our ``latest_changes`` app and then
add a ``reports`` folder to it. Finally in that folder add a ``latest_changes.html``. So the full path of
the ``latest_changes.html`` should be: ``wagtail_starter\latest_changes\templates\reports\latest_changes.html``:

.. code::

  {% extends 'wagtailadmin/reports/base_report.html' %}
  {% load i18n %}
  {% block listing %}
      {% include "reports/_list_latest.html" %}
  {% endblock %}

  {% block no_results %}
      <p>{% trans "No changes found." %}</p>
  {% endblock %}

I've selected the ``reports`` subfolder just to be compatible with what wagtail does, you can just put ``latest_changes.html``  directly
under ``templates``; don't forget to update the ``LatestChangesView`` defined before though! The above page includes a 
snippet named ``reports/_list_latest.html" thus you also need to add a ``_list_latest.html`` file in the same folder with the 
following contents:


.. code::
  
  {% extends "wagtailadmin/pages/listing/_list_explore.html" %}

  {% load i18n wagtailadmin_tags %}

  {% block post_parent_page_headers %}
  <tr>
  <th>Title</th>
  <th>Last update</th>
  <th>Kind</th>
  <th>Status</th>
  <th>Owner / last publish / last edit</th>
  </tr>
  {% endblock %}

  {% block page_navigation %}
      <td>
          {{ page.owner }} / {{ page.live_revision.user }} / {{ page.get_latest_revision.user }}
      </td>
  {% endblock %}

Please notice that my ``_list_latest.html`` snippet extends the wagtail provided ``_list_explore.html`` template and
overrides some things that can be overriden from that file. If you want to do more changes you'll need to copy over
everything and change things as you wish instead of extending.

Also, keep in mind that because you added a ``templates`` folder you'll need to restart your django development server.

Finally, if everything is ok until now you should be able to visit http://127.0.0.1:8000/admin/latest_changes/ and see
your view! It will say "No changes found" if you've followed the steps here; just go to Pages - Home from the wagtail
menu and edit that page (just save it). Now visit http://127.0.0.1:8000/admin/latest_changes/ again and behold! Your
own latest changes view:

.. image:: /images/last_changes_view.png
  :alt: The view
  :width: 780 px

Displaying our menu item
========================

The last piece of the puzzle missing is to actually display a menu item under the Reports menu of wagtail admin. For this
we are going to use our friends, the wagtail hooks. So, change the wagtail_hooks.py file like this (I'm also including
the code from adding the url):

.. code::

  from django.http import HttpResponse
  from django.conf.urls import url
  from django.urls import reverse
  from wagtail.admin.menu import MenuItem
  from wagtail.core import hooks
  from wagtail.core.models import UserPagePermissionsProxy
  from .views import LatestChangesView

  @hooks.register('register_admin_urls')
  def urlconf_time():
      return [
        url(r'^latest_changes/$', LatestChangesView.as_view(), name='latest_changes'),
      ]


  class LatestChangesPagesMenuItem(MenuItem):
      def is_shown(self, request):
          return UserPagePermissionsProxy(request.user).can_remove_locks()


  @hooks.register("register_reports_menu_item")
  def register_latest_changes_menu_item():
      return LatestChangesPagesMenuItem(
          "Latest changes", reverse("latest_changes"), classnames="icon icon-date", order=100,
      )

The above code uses the ``register_reports_menu_item`` which is a hook that can be used to add a child 
specifically to the Reports menu item. Notice that it uses the ``LatestChangesPagesMenuItem`` which
is a class that inherits from ``MenuItem``; the only thing that is overriden there is the ``is_shown``
method so it will have the same permissions as the ``LatestChangesView`` we defined above so user 
that will see the menu item will also have permissions to display the view. Here's the final menu item:

.. image:: /images/latest_changes_menu.png
  :alt: The menu item
  :width: 380 px


Conclusion
==========

We've seen the steps required to add a latest pages view to your wagtail admin site. I have to admit that
it is a little work however the nice thing is that this is all self-included in a single application. You can
just get tha application and copy over it to your wagtail site; after you add that application to INSTALLED_APPS
you should get the whole functionality without any more modifications to your project. To help you more
with this I've included the whole code of this project in the https://github.com/spapas/wagtail-latest-changes repository.

You can either clone this repository to see the functionality or just copy over the ``latest_changes`` folder to
your wagtail project to include the functionality directly (don't forget to fix the ``INSTALLED_APPS`` setting)!



.. _Wagtail: https://wagtail.io
