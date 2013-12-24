Django authority data
#####################

:date: 2013-11-05 14:20
:tags: django, python, security
:category: django
:slug: django-authoritiy-data
:author: Serafeim Papastefanos
:summary: An implementation & discussion of authority data for Django

.. contents::

Introduction
------------

One common requirement in an organization is to separate users in authorities (meaning departments / units / branches etc)
and each authority have its own data. So users belonging to the "Athens Branch" won't be able to 
edit data submitted from users of the "Thessaloniki Branch". 

This is a special case of the more general row-level-security in which each instance of a domain object will
have an ACL. Row-level-security would need a many-to-many relation between object instances and authorities, something
that would be overkill in our case. 

Authority data is also a more general case of the user-data meaning that each user can have access
to data that he inserts in the system. Implementing user-data is easy using the techniques we will present below.

We have to notice that the django permissions do not support our requirements since they define security for all instances of a model.

Defining authorities
--------------------

In order to have custom authorities I propose first of all to add an Authority model that would define the authority. Even if
your authorities only have a name I believe that adding the Authority model would be beneficial.
Now, there are many ways to separate normal django users (``django.contrib.auth.models.User``) to authorities:
   
Using groups
============

Just define a ``django.contrib.auth.models.Group`` for each authority and add the users to the groups you want using the django-admin.
Your Authority model would have an one-to-one relation with the ``django.contrib.auth.models.Group`` so you will be able to find out the other
information of the authority (since django groups only have names).

Now you can just get the groups for the user and find out his authorities. This could lead to problems when users belong to django groups
that are not related to authorities so you must filter these out (for instance by checking which groups actually have a corresponding Authority).

By storing the authority to the session
=======================================

When the user logs in you can add an attribute to the session that would save the authority of the user. To do that, you should define
a custom middleware that checks to see if there is an authority attribute to the session and if not it will do whatever it needs to find it and set it.
An example is this:

.. code:: 

  class CustomAuthorityMiddleware:
    def process_request(self, request):
      if not request.session.get('authority'):
        authority = get_the_authority(request.user)
        request.session['authority']=authority
        
This way, whenever you want to find out the authority of the user you just check the session.
        
By using a Custom User Profile
==============================

Just create a `django user profile`_ and add to it a ``ForeignKey`` to your Authority model:

.. code::

  class Profile(models.Model):
    user = models.OneToOneField('django.auth.User')
    authority = models.ForeignKey('authorities.Authority', blank=True, null=True )
    
  class Authority(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length=64, )
    auth_type = models.CharField(max_length=16, )
    
    
You can get the authority of the user through ``request.user.profile.authority``.

Getting the authority of the user has to be DRY
===============================================

Whatever method you use to define the authorities of your users you have to remember that it is very
important to define somewhere a function that will return the authority (or authorities) of a 
user. You need to define a function even in the simple case in which your function would just return ``request.user.profile.authority``.
This will greatly help you when you wish to add some logic to this, for instance "quickly disable users belonging to Authority X
or temporary move users from Authority Y to authority Z".

Let us suppose that you have defined a ``get_user_authority`` function. Also, you need to define a ``has_access`` function
that would decide if a users/request has access to a particular object. This also needs to be DRY.

Adding authority data
---------------------

To define authority data you have to add a field to your model that would define its authority, for instance like this:

.. code::

  class AuthorityData(models.Model):
    authority = models.ForeignKey('authorities.Authority', editable=False,)
    
This field should not be editable (at least by your end users) because they shouldn't be able to change the authority of the data they insert.

If you want to have user-data then just add a ``models.ForeignKey('django.auth.User', editable=False)``

Now, your Create and Update Class Based Views have to pass the request to your forms and also your Detail and Update CBV should allow only getting
objects that belong to the authority of the user:

    
.. code::

  class AuthorityDataCreateView(CreateView):
    model=models.AuthorityData

    def get_form_kwargs(self):
        kwargs = super(AuthorityDataCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

  class AuthorityDataDetailView(DetailView):
    def get_object(self, queryset=None):
        obj = super(AuthorityDataDetailView, self).get_object(queryset)
        if if not user_has_access(obj, self.request):
            raise Http404(u"Access Denied")
        return obj
        
  class AuthorityDataUpdateView(UpdateView):
    model=models.AuthorityData

    def get_form_kwargs(self):
        kwargs = super(AuthorityDataUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
    
    def get_object(self, queryset=None):
        obj = super(AuthorityDataUpdateView, self).get_object(queryset)
        if if not user_has_access(obj, self.request):
            raise Http404(u"Access Denied")
        return obj
        

Your ModelForm can now use the request to get the Authority and set it (don't forget 
that you should not use ``Meta.exclude`` but instead use ``Meta.include``!):
    
.. code::

  class AuthorityDataModelForm(forms.ModelForm):
      class Meta:
        model = models.AuthorityData
        exclude = ('authority',)

      def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ActionModelForm, self).__init__(*args, **kwargs)

      
      def save(self, force_insert=False, force_update=False, commit=True):
        obj = super(AuthorityDataModelForm, self).save(commit=False)
        if obj:
            obj.authority = get_user_authority(self.request)
            obj.save()
        return obj  
    
The previous work fine for Create/Detail/Update CBVs but not for ListsViews. List views querysets
and in general all queries to the object have to be filtered through authority. 

.. code::
 
    class AuthorityDataListView(ListView):
      def get_queryset(self):
        queryset = super(AuthorityDataModelForm, self).get_queryset()
        return queryset.filter(authority = get_user_authority(request))
        
Conclusion
----------

Using the above techniques we can define authority (or just user) data. Your AuthorityData should
have a ``ForeignKey`` to your Authority  and you have configure your queries, ModelForms and CBVs
to use that. If you have more than one models that belong to an authority and want to stay DRY then you'd need 
to define all the above as mixins_.
    
.. _`django user profile`: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#extending-the-existing-user-model
.. _mixins: https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
