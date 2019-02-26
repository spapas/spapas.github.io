Fixing your Django async job - database integration
###################################################

:date: 2019-02-25 15:20
:tags: django, async, tasks, django-rq, rq
:category: django
:slug: django-fix-async-db
:author: Serafeim Papastefanos
:summary: How to properly fix the errors you get when integrating async jobs (rq, celery etc) with your database in Djang

I've already written 
`two <{filename}async-tasks-with-django-rq.rst>`_
`articles <{filename}django-rq-redux.rst>`_
about django-rq and implementing asynchronous tasks in Django. However I've found out
that there's a very important thing missing from them: How to properly integrate
your asynchronous tasks with your Django database. This is very important because
if it is not done right you will start experiencing strange errors about missing
database objects or duplicate keys. The most troublesome thing about these errors is 
that they are not consistent. Your app may work fine but for some reason you'll see some
of your asynchronous tasks fail with these errors. When you re-queue the async jobs everything will
be ok. 

Of course this behavior (code that runs *sometimes*) smells of a race condition but its not easy to debug
it if you don't know the full story.

In the following I will describe the cause of this error and how you can fix it. As a companion
to this article I've implemented a small project that can be used to test the error and the
fix: `https://github.com/spapas/async-job-db-fix`_.

Notice that although this article is written for django-rq it should also help people that have
the same problems with other async job systems (like celery or django-q).

Description of the project
--------------------------

The project is very simple, you can just add a url and it will retrieve its content asynchronously and
report its length. For the models, it just has a ``Task`` model which is used to provide information about
what we want to the asynchronous task to do and retrieve the result:

.. code-block:: python

    from django.db import models

    class Task(models.Model):
        created_on = models.DateTimeField(auto_now_add=True)
        url = models.CharField(max_length=128)
        url_length = models.PositiveIntegerField(blank=True, null=True)
        job_id = models.CharField(max_length=128, blank=True, null=True)
        result = models.CharField(max_length=128, blank=True, null=True)
        
It also has a home view that can be used to start new asynchronous tasks by creating a ``Task`` object
with the url we got and passing it to the asynchronous task:

.. code-block:: python

    from django.views.generic.edit import FormView
    from .forms import TaskForm
    from .tasks import get_url_length
    from .models import Task

    import time
    from django.db import transaction

    class TasksHomeFormView(FormView):
        form_class = TaskForm
        template_name = 'tasks_home.html'
        success_url = '/'

        def form_valid(self, form):
            task = Task.objects.create(url=form.cleaned_data['url'])
            get_url_length.delay(task.id)
            return super(TasksHomeFormView, self).form_valid(form)

        def get_context_data(self, **kwargs):
            ctx = super(TasksHomeFormView, self).get_context_data(**kwargs)
            ctx['tasks'] = Task.objects.all().order_by('-created_on')
            return ctx

And finally the asynchronous job itself that retrieves the task from the database,
requests its url and saves its length:

.. code-block:: python

    import requests
    from .models import Task
    from rq import get_current_job
    from django_rq import job

    @job
    def get_url_length(task_id):
        jb = get_current_job()
        task = Task.objects.get(
            id=task_id
        )
        response = requests.get(task.url)
        task.url_length = len(response.text)
        task.job_id = jb.get_id()
        task.result = 'OK'
        task.save()

The above should be fairly obvious: The user visits the homepage and enters a url at the input. When he presses submit
the view will create a new ``Task`` object with the url that the user entered and fire-off the ``get_url_length`` asynchronous job passing the
task id of the task that was just created. It will then return immediately without waiting for the asynchronous job to complete. The user will
need to refresh to see the result of his job; this is the usual behavior with async jobs.

The asynchronous job on the other hand will retrieve the task whose id got as a parameter from the database, do the work it needs to do
and update the result when it is finished. 

Unfortunately, the above simple setup will *probably* behave erratically by randomly throwing database related errors! 

Cause of the problem
--------------------

In the previous section I said *probably* because the erratic behavior is caused by a specific setting of your Django project; the ``ATOMIC_REQUESTS``.
This setting can be set on your database connection and if it is ``TRUE`` then each request will be *atomic*. This means that each request will be tied with
a database transaction i.e a transaction will be started when your request starts and commited only when your requests finishes; if for some reason your
request throws an error then the transaction will be rolled back. An example of this setting is:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'ATOMIC_REQUESTS': True,
        }
    }

Now, in my opinion, ``ATOMIC_REQUESTS`` is a great thing to have because it makes everything much easier. I always set it to ``True`` to my projects because
I don't need to actually think about transactions and requests; I know that if there's a problem in a request the whole transaction will be rolle back and no 
garbage will be left in the database. If on the other hand for some reason a request does not need to be tied to a transaction I just set it off
for this specific transaction (using `transaction.non_atomic_requests_`). Please notice that by default the ``ATOMIC_REQUESTS`` has a ``False`` value which means that 
the database will be in autocommit mode meaning that every command will be executed immediately. 

So although the ``ATOMIC_REQUESTS`` is great, it is actually the reason that there are problems with asynchronous tasks. Why? Let's take a closer look at what the ``form_valid`` of the view does:

.. code-block:: python

    def form_valid(self, form):
        task = Task.objects.create(url=form.cleaned_data['url']) #1 
        get_url_length.delay(task.id) #2 
        return super(TasksHomeFormView, self).form_valid(form) #3

It creates the task in #1, fires off the asynchronous task in #2 and continues the execution of the view processing in #3. The important thing to understand 
here is that the transaction will be commited *only after #3* is finished. This means that there's a possibility that the asynchronous task will be started
before #3 is finished thus it won't find the task because the task will *not* be created yet(!) This is a little counter-intuitive but you must remember
that the async task is run by a worker which is a different process than your application server; the worker may be able to start before the transaction is commited.

If you want to actually see the problem *every time* you can add a small delay between the start of the async task and the ``form_valid`` something like this:

.. code-block:: python

    def form_valid(self, form):
        task = Task.objects.create(url=form.cleaned_data['url'])
        get_url_length.delay(task.id)
        time.sleep(1)
        return super(TasksHomeFormView, self).form_valid(form)

This will make the view more slow so the asynchronous worker will always have time to start executing the task (and get the not found error). Also notice
that if you had ``ATOMIC_REQUESTS: False`` the above code would work fine because the task would be created immediately (auto-commited) and the async job would be able to find it.

The solution
------------

So how is this problem solved? Well it's not that difficult now that you know what's causing it!

One solution would be to set ``ATOMIC_REQUESTS`` to ``False`` but that would make all database commands auto-commit so you'll lose
request-transaction-tieing. Another solution would be to set ``ATOMIC_REQUESTS`` to ``True`` and disable atomic requests for the specific view that starts the
asynchronous job using `transaction.non_atomic_requests_`. This is a viable solution however I don't like it because I'd lose the comfort of transaction per request
for this specific request and I would need to add my own transaction handling. 

A third solution is to avoid messing with the database in your view and create the task object in the async job. Any parameters you want to pass to the async job would be
passed directly to the async function. This may work fine in some cases but I find it more safe to create the task in the database before starting the async job so that
I have better control and error handling. This way even if there's an error in my worker and for some reason the async job never starts or it breaks before being able to
handle the database, I will have the task object in the database because it will have been created in the view.

Is there anything better? Isn't there a way to start the executing the async job *after* the transaction of the 
view is commited? Actually yes, there is! For this, `transaction.on_commit`_ comes to the rescue! This function
receives a callback that will be called after the transaction is commited! Thus, to properly fix you project, you should
change the ``form_valid`` method like this:

.. code-block:: python

    def form_valid(self, form):
        task = Task.objects.create(url=form.cleaned_data['url'])
        transaction.on_commit(lambda: get_url_length.delay(task.id))
        time.sleep(1)
        return super(TasksHomeFormView, self).form_valid(form)

Notice that I need to use ``lambda`` to create a callback function that will call ``get_url_length.delay(task.id)`` when the transaction is commited. Now
even though I have the delay there the async job will start after the transaction is commited, ie after the view handler is finished (after the 1 second
delay).

Conclusion
----------

From the above you should be able to understand why sometimes you have problems when your async jobs use the database. To fix it you have various 
options but at least for me, the best solution is to start your async jobs *after* the transaction is commited using ``transaction.on_commit``. Just
change each ``async.job.delay(parameters)`` call to ``transaction.on_commit(lambda: async.job.delay(parameters))`` and you will be fine!


.. _`https://github.com/spapas/async-job-db-fix`: https://github.com/spapas/async-job-db-fix
.. _`transaction.non_atomic_requests`: https://docs.djangoproject.com/en/2.1/topics/db/transactions/#django.db.transaction.non_atomic_requests
.. _`transaction.on_commit`: https://docs.djangoproject.com/en/2.1/topics/db/transactions/#django.db.transaction.on_commit