Using both Python 2 and 3 in Windows
####################################

:date: 2017-12-20 11:20
:tags: python, python-2, python-3, windows
:category: python
:slug: python-2-3-windows
:author: Serafeim Papastefanos
:summary: How to install and use both Python 2.x and 3.x on Windows

The release of Django 2.0 was a milestone in the history of Python since it
completely dropped support for Python 2.x. I am a long time user of Django
and, loyal to the philosophy of "if it is working don't change" I was always
using Python 2.x. 

Of course right now this needs to change since new applications will need to
be developed to the latest version of Django (and Python). I am using
Windows for development (almost exclusively) and what I wanted was to 
be able to create and use virtual environments for both my old projects
(using Python 2) and new projects (using Python 3). 

The above requirement is not as straight-forward as I'd like - actually it is
if you know what you need to do and which tools you must use. That's why I
decided to write a quick step by step tutorial on how to use both versions
of Python in your Windows environment. Notice that I am using Windows 10,
Python 2.7.14 an Python 3.6.4.

First of all, let's download both versions of Python
from the `Python download page`_. I downloaded the files
python-2.7.14.msi and python-3.6.4.exe (not sure why the one is .msi and the other
is .exe it doesn't matter anyway).

Firstly I am installing Python 2.7.14 and selecting:

* Install for all users 
* Install to default folder
* Press next to following screen (install default customizations)
* This won't add the python.exe of Python 2.7 to path

Next I am install Python 3.6.4:

* Make sure to click "Install launcher for all users (recommended)"
* I also check "Add Python 3.6to PATH" (to add the Python 3.6 executable to path)
* I then just click "Install Now" (this will put Python 3.6 to c:\)

Right now if you open a terminal window (Windows+R - cmd.exe) and run Python you will
initiate the Python 3.6 interpreter. This is useful for just dropping in a Python interpreter.

Remember the "Install launcher for all users (recommended)" we clicked before? This installs
the python launcher which is used to select between Python versions. 
If you run it without parameters the Python 3.6 interpreter will by started. You can pass
the -2 parameter to start the python 2.x interpreter or -3 to explicitly declare the
python 3.x interpreter:

```

```




.. _`Python download page`: https://www.python.org/downloads/