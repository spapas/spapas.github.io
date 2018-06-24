Using partial templates to modernize Django
###########################################

:date: 2018-05-11 14:20
:tags: django, python
:category: python
:slug: modernize-django-with-partials
:author: Serafeim Papastefanos
:summary: How to use partial templates to make your Django application look and feel more modern
:status: draft

Now, to create the virtual environments we'll use the virtualenv module which is installed
by default in Python 2.x (try running ``py -2 -m pip freeze`` to see the list of installed
packages for Python 2.x) and the venv module which is included in the Python 3.x core. So
to create a virtualenv for Python 2 we'll run ``py -2 -m virtualenv name-of-virtualenv``
and for Python 3 ``py -3 -m venv name-of-virtualenv``.

.. raw:: html

    ss 
    <script type="text/javascript" >
    console.log("X")
    alert("Y")
    </script>
    dd

.. code::

    C:\progr\py>py -2 -m virtualenv venv-2
    New python executable in C:\progr\py\venv-2\Scripts\python.exe
    Installing setuptools, pip, wheel...done.

    C:\progr\py>py -3 -m venv venv-3

    C:\progr\py>venv-2\Scripts\activate

    (venv-2) C:\progr\py>python -V
    Python 2.7.14
    
    (venv-2) C:\progr\py>deactivate

    C:\progr\py>venv-3\Scripts\activate

    (venv-3) C:\progr\py>python -V
    Python 3.6.4

That's how easy it is to have both Python 2.7 and Python 3.6 in your Windows!

.. _`Python download page`: https://www.python.org/downloads/
.. _`as per this`: https://stackoverflow.com/questions/7943751/what-is-the-python-3-equivalent-of-python-m-simplehttpserver
