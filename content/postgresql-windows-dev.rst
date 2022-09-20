Setting up Postgres on Windows for development
##############################################

:date: 2022-09-20 11:10
:tags: windows, postgresql, development
:category: postgresql
:slug: postgresql-windows-dev
:author: Serafeim Papastefanos
:summary: How to setup Postgres for development on Windows

Introduction
------------

To install Postgresql for a production server on Windows you'd usually go to the
`official website`_ and use the download link. This will give you an executable 
installer that would install Postgresql on your server and help you configure it.

However, since I only use Windows for development (and never running any in 
production on Windows) I've found out that there's a much better and easier way to install
postgresql for development and windows which I'll describe in this post. 

If you want to avoid reading the whole post, you can just follow the steps described on the 
`TL;DR below`_ however I'd recommend reading to understand everything.

Downloading the server
----------------------

First, you'll 
click the `zip archives`_ link on the . `official website`_ and then 
download the zip archive of the Postgres version you'll want to install. Right now there are
archives for every current version like 14.5, 13.8, 12.12 etc. Let's get the latest one, 14.5.

This will give me a zip file named ``postgresql-14.5-1-windows-x64-binaries.zip`` which contains a 
single folder named ``pgsql``. I'll extract that folder, rename it to ``pgsql145`` and move it to ``c:\progr``
(I keep stuff there to avoid putting everything on C:\). Now you should have a folder named 
``c:\progr\pgsql145`` that contains a bunch of folder named ``bin``, ``doc``, ``include`` etc.

Setting up the server
---------------------

Now we are ready to setup Postgresql. Open a command line and move to the ``pgsql145\bin`` folder:

.. code:: 

  cd c:\progr\pgsql145\bin

The bin folder contains *all* executables of your server and client, like ``psql.exe`` (the CUI client),
``pg_dump.exe`` (backup), ``initdb.exe`` (create a new DB cluster), ``createdb/dropdb/createuser/dropuser.exe ``
(create/drop database/user - these can also be run from SQL)
and ``postgres.exe`` which is the actual server executable.

Our first step is to create a database cluster using initdb. We need to pass it a folder that will
contain the data of our cluster. So we'll run it like:

.. code:: 

  initdb.exe -D c:\progr\pgsql145\data

(also you could run ``initdb.exe -D ..\data``, since we are on the bin folder). We'll get output similar to:

.. code:: 

  The files belonging to this database system will be owned by user "serafeim".
  This user must also own the server process.

  The database cluster will be initialized with locale "Greek_Greece.1252".
  The default database encoding has accordingly been set to "WIN1252".
  The default text search configuration will be set to "greek".

  Data page checksums are disabled.

  fixing permissions on existing directory c:/progr/pgsql145/data ... ok
  creating subdirectories ... ok
  selecting dynamic shared memory implementation ... windows
  selecting default max_connections ... 100
  selecting default shared_buffers ... 128MB
  selecting default time zone ... Europe/Bucharest
  creating configuration files ... ok
  running bootstrap script ... ok
  performing post-bootstrap initialization ... ok
  syncing data to disk ... ok

  initdb: warning: enabling "trust" authentication for local connections
  You can change this by editing pg_hba.conf or using the option -A, or
  --auth-local and --auth-host, the next time you run initdb.

  Success. You can now start the database server using:

      pg_ctl -D ^"c^:^\progr^\pgsql145^\data^" -l logfile start

And now we'll have a folder named ``c:\progr\pgsql145\data`` that contains files like 
``pg_hba.conf``, ``pg_ident.conf``, ``postgresql.conf`` and various folders that will keep our 
database server data. All these can be configured but we're going to keep using the default config
since it fits our needs!

Notice that:

* The files of our database belong to the "serafeim" role. This role is automatically created by initdb. This is the same username that I'm using to log in to windows (i.e my home folder is ``c:\users\serafeim\`` folder) so this will be different for you. If you wanted to use a different user name or the classic ``postgres`` you could pass it to ``initdb`` with the -U parameter, for example: ``initdb.exe -D c:\progr\pgsql145\data_postgres -U postgres``.
* By default "trust" authentication has been configured. This means, copying from `postgres trust authentication page`_ that "[...] PostgreSQL assumes that anyone who can connect to the server is authorized to access the database with whatever database user name they specify (even superuser names)". So local connections will always be accepted with the username we are passing. We'll see how this works in a minute.
* The default database encoding will be WIN1252 (on my system). We'll talk about that a little more later (hint: it's better to pass -E utf-8 to set your cluster encodign to utf-8)

Starting the server
-------------------

We could use the ``pg_ctl.exe`` executable as proposed by the initdb to start the server as a a background process. 
However, for our purposes it's better to start the server as a foreground process on a dedicated window. So we'll run the ``postgres.exe`` directly like:

.. code::
      
    postgres.exe -D c:\progr\pgsql145\data
   
or, from the ``bin`` directory we could run ``postgres.exe -D ..\data``. The output will be 

.. code::

  2022-09-20 09:34:10.184 EEST [10648] LOG:  starting PostgreSQL 14.5, compiled by Visual C++ build 1914, 64-bit
  2022-09-20 09:34:10.189 EEST [10648] LOG:  listening on IPv6 address "::1", port 5432
  2022-09-20 09:34:10.189 EEST [10648] LOG:  listening on IPv4 address "127.0.0.1", port 5432
  2022-09-20 09:34:10.330 EEST [3084] LOG:  database system was shut down at 2022-09-20 09:34:08 EEST
  2022-09-20 09:34:10.369 EEST [10648] LOG:  database system is ready to accept connections

Success! Our server is running and listening on 127.0.0.1 port 5432. This means that it accepts connection *only* from our local machine
(which is what we want for our purposes). We can now connect to it using the ``psql.exe`` client. Open another cmd, go to ``C:\progr\pgsql145\bin``
and run ``psql.exe``: You'll probably get an error similar to ``psql: error: connection to server at "localhost" (::1), port 5432 failed: FATAL:  database "serafeim" does not exist``
(unless your windows username is ``postgres``).

By default psql.exe tries to connect with a role with the username of your Windows user and to a database named after the user you are 
connecting with. Our database server *has* a role named ``serafeim`` (it is created by default by the initdb as described before) but it doesn't have a database named ``serafeim``! Let's connect
to the ``postgres`` database instead by passing it as a parameter ``psql postgres``:

.. code::

  C:\progr\pgsql145\bin>psql postgres
  psql (14.5)
  WARNING: Console code page (437) differs from Windows code page (1252)
          8-bit characters might not work correctly. See psql reference
          page "Notes for Windows users" for details.
  Type "help" for help.

  postgres=# select version();
                            version
  ------------------------------------------------------------
  PostgreSQL 14.5, compiled by Visual C++ build 1914, 64-bit
  (1 row)

Success! 

Let's cerate a sample user and database to make user that everything's working fine ``createuser.exe koko``,
``createdb kokodb`` and connect to the ``kokodb`` as ``koko``: ``psql -U koko kokodb``.

.. code::

  kokodb=> create table kokotable(foo varchar);
  CREATE TABLE
  kokodb=> insert into kokotable values('kokoko');
  INSERT 0 1
  kokodb=> select * from kokotable;
    foo
  --------
  kokoko
  (1 row)

Everything's working fine! In the meantime, we should get useful output on our postgres dedicated windows, like 
``2022-09-20 09:36:01.899 EEST [9704] FATAL:  database "serafeim" does not exist``. To stop it, just press ``Ctrl+C``
on that window and you should get output similar to: 

.. code::

  2022-09-20 09:46:45.178 EEST [10648] LOG:  background worker "logical replication launcher" (PID 7860) exited with exit code 1
  2022-09-20 09:46:45.185 EEST [10048] LOG:  shutting down
  2022-09-20 09:46:45.278 EEST [10648] LOG:  database system is shut down

I usually add a ``pg.bat`` file on my ``c:\progr\pgsql145\`` that will start the database with its data folder. It's contents are only
``bin\postgres.exe -D data``

So let's create the pg.bat like this:

.. code::

  c:\>cd c:\progr\pgsql145

  c:\progr\pgsql145>copy con pg.bat
  bin\postgres.exe -D data
  ^Z
          1 file(s) copied.

  c:\progr\pgsql145>pg.bat  
  2022-09-20 09:49:53.642 EEST [11660] LOG:  starting PostgreSQL 14.5, compiled by Visual C++ build 1914, 64-bit
  ...

One final thing to notice is that, since we use the trust authentication there's no check for the password, so if we 
tried to pass a password like ``psql -U koko -W kokodb`` it will work no matter what password we type.

Encoding stuff
--------------

The default encoding situation
==============================

You may have noticed before that the default encoding for databases will be ``WIN1252`` (or some other 
similar 8-bit character set). You never want that (I guess this default is there for compatibility reasons), 
you want to have utf-8 encoding. So you should either
pass the proper encoding to initdb, like:

.. code::

  initdb -D ..\datautf8 -E utf-8

This will create a new cluster with utf-8 encoding. All databases created on that cluster will be utf-8 by default.

If you've already got a non-utf-8  cluster, you should force utf-8 for your new database instead:

.. code::
  
  createdb -E utf-8 -T template0 dbutf8

Notice that I also passed the ``-T template0`` parameter to use the ``template0`` `template database`_. If I 
tried to run ``createdb -E utf-8 dbutf8`` (so it would use the ``template1``) I'd get an error similar to:

.. code::

  createdb: error: database creation failed: ERROR:  new encoding (UTF8) is incompatible with the encoding of the template database (WIN1252)
  HINT:  Use the same encoding as in the template database, or use template0 as template.


About the psql codepage warning
===============================

You may (or may not) have noticed a warning similar to this when starting the server:

.. code::

  WARNING: Console code page (437) differs from Windows code page (1252)
        8-bit characters might not work correctly. See psql reference
        page "Notes for Windows users" for details.

Some more info about this can be found in the `psql reference page`_ and 
`this SO issue`_. To avoid this warning you'll use ``chcp 1252`` to set the console code page to 1252
before running psql.

I have to warn you though that using psql.exe from the windows console **will be problematic** anyway
because of not good unicode support. You can use it fine as long as you write only ascii characters but
I'd avoid anything else.

That's why I'd recommend using a graphical database client like for example dbeaver_.


.. _`TL;DR below`:

A TL;DR walkthrough
-------------------

Here are the steps to follow to get a working postgresql server on windows:

1. Download the postgresql windows binaries of the version you want from the `zip archives`_ page and extract it to a folder, let's name it ``pgsql``.
2. Go to ``pgsql\bin`` folder on a command line
3. Run ``initdb.exe -D ..\data -E utf-8`` from inside the ``pgsql\bin`` folder of the  to create a new database cluster with utf-8 encoding on the ``data`` directory
4. Run ``postgresql.exe -D ..\data`` to start the database server
5. Go to ``pgsql\bin`` folder on another command line
6. Run ``psql postgres`` to connect to the ``postgres`` database with a role similar to your windows username
7. Profit!

Conclusion
----------

Using the above steps you can easily setup a postgres database server on windows for development. Some advantages of the method
proposed here are:

* Since you configure the data directory you can have as many clusters as you want (run initdb with different data directories and pass them to postgres)
* Since nothing is installed globally, you can have as many postgresql versions as you want, each one having its own data directory. Then you'll start the one you want each time! For example I've got Postgresql 12,13 and 14.5.
* Using the trust authentication makes it easy to connect with whatever user
* Running the database from postgresql.exe so it has a dedicated window makes it easy to know what the database is doing, peeking at the logs and stopping it (using ctrl+c)

.. _`official website`: https://www.postgresql.org/download/windows/
.. _`zip archives`: https://www.enterprisedb.com/download-postgresql-binaries
.. _`postgres trust authentication page`: https://www.postgresql.org/docs/current/auth-trust.html
.. _`psql reference page`: https://www.postgresql.org/docs/14/app-psql.html`
.. _`this SO issue`: https://stackoverflow.com/questions/20794035/postgresql-warning-console-code-page-437-differs-from-windows-code-page-125
.. _dbeaver: https://dbeaver.io/
.. _`template database`: https://www.postgresql.org/docs/current/manage-ag-templatedbs.html