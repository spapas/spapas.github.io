Automatically create a category table in Postgresql by extracting unique table values
#####################################################################################

:date: 2017-07-04 09:05
:tags: postgresql, plpgsql
:category: postgresql
:slug: postgresql-auto-create-category-column
:author: Serafeim Papastefanos
:summary: A postgresql script to help you automatically create a new category table by extracting its values from a table and generate the relations

Recently I was given an SQL table containing some useful data. The problem with that table was that it was was non-properly normalized but was completely flat,
i.e all its columns contained varchar values while, some of them should have instead contained foreign keys to other tables. Here's an example of how this
table looked like:

=====  =========  ========== ============
Parts
-----------------------------------------
ID     Serial     Category   Manufacturer
=====  =========  ========== ============
1      423431     Monitor    LG
2      534552     Monitor    LG
3      435634     Printer    HP
4      534234     Printer    Samsung
5      234212     Monitor    Samsung
6      123123     Monitor    LG
=====  =========  ========== ============

The normalized version of this table should have been instead like this:

=====  =========  =========== ===============
Parts
---------------------------------------------
ID     Serial     Category_id Manufacturer_id
=====  =========  =========== ===============
1      423431     1           1
2      534552     1           1
3      435634     2           2
4      534234     2           3
5      234212     1           3
6      123123     1           2
=====  =========  =========== ===============

with the following extra tables that contain the category values with proper foreign keys:

== =======
Category
----------
ID Name
== =======
1  Monitor
2  Printer
== =======

== ==========
Manufacturer
-------------
ID Name
== ==========
1  Monitor
2  Printer
== ==========

The normalized version should be used instead of the flat one `for reasons which at this moment must be all too obvious`_. 

Having such non-normalized tables is also a common problem I experience with Django: When creating a model
I usually define some ``CharField``  with pre-defined ``choices`` which "will never change". Sometime during the
development (if I am lucky) or when the project is live for years I will be informed that the choices need not
only to be changed but must be changed by the users of the site without the need to change the source code! Or
that the choices/categories have properties (beyond their name) that need to be defined and used in the project. Both
of these cases mean that these categories need to be extracted from simple strings to full Django models (i.e get 
normalized in their own table)!

In this post I will present a function written in PL/pgsql that will automatically normalize a column from a 
flat table like the previous. Specifically, using the previous example, 
if you have a table named ``part`` that has a non-normalized
column named ``category`` then when you call ``select export_relation('part', 'category')`` the following
will happen:

* A new table named ``part_category`` will be created. This table will contain two columns ``id`` and ``name``, with ``id`` being the primary key and ``name`` having a unique constraint. If the table exists it will be dropped and re-ccreated
* A new column named ``category_id`` will be added to ``part``. This column will be a foreign key to the new table ``part_category``.
* For each unique value ``v`` of ``category``:
    * Insert a new record in ``part_category`` with ``v`` in the ``name`` field of the table and save the inserted id to ``current_id``
    * Set ``current_id`` to ``category_id``  to all rows of ``part`` where ``category`` has the value of ``v``
   

Before diving in to the PL/pgSQL script that does the above changes to the table I'd like to notice that I am
not very experienced with PL/pgSQL since I rarerly use it
(I actually avoid writing code in the database) however, because the case I described is ideal for using a database script
I've bitten the bullet and implemented it. 

Beyond it's actual functionality, this script can be used as a reference/cookbook for common PL/pgSQL tasks:

* Create/define a PL/pgSQL function (stored procedure)
* Declare variables
* Assign values to variables
* Execute SQL commands with variable defined table / column names
* Log process in PL/pgSQL
* Executing code conditionally
* Loop through the rows of a query
* Save the primary key of an inserted row


The script works however I feel that more experienced PL/pgSQL developers would write things different - if you have any
proposals please comment out and I'll be happy to incorporate them to the script.

Now, let's now take a look at the actual script:

.. code-block:: plpgsql

    CREATE OR REPLACE FUNCTION export_relation(table_name varchar, column_name varchar)     
    RETURNS void AS $$ 
    DECLARE
        val varchar;
        res boolean;
        new_table_name varchar;
        new_column_name varchar;
        current_id int;
    BEGIN
        new_table_name := table_name || '_' || column_name;
        new_column_name := column_name || '_id' ;

        execute format ('drop table if exists %s cascade', new_table_name);
        execute format ('CREATE TABLE %s (id serial NOT NULL, name character varying(255) NOT NULL, CONSTRAINT %s_pkey PRIMARY KEY (id), CONSTRAINT %s_unique UNIQUE (name))WITH ( OIDS=FALSE)',
            new_table_name, new_table_name, new_table_name
        );

        execute format('select exists(SELECT column_name  FROM information_schema.columns WHERE table_name=''%s'' and column_name=''%s'') as x', table_name, new_column_name) into res;
        if res is false then
            raise notice 'Creating colum';
            execute format ('ALTER TABLE %s ADD COLUMN %s integer null', table_name, new_column_name);
            execute format ('ALTER TABLE %s ADD CONSTRAINT fk_%s FOREIGN KEY (%s) REFERENCES %s(id)', table_name, new_column_name, new_column_name, new_table_name);
        end if ;

        for val IN execute format ('select %s from %s group by(%s)', column_name, table_name, column_name) LOOP
            RAISE NOTICE 'Inserting new value %s ...', val;
            execute format ('insert into  %s(name) values (''%s'') returning id', new_table_name, val) into current_id;
            raise notice 'Created ID %', current_id;
            execute format ('update %s set %s = %s where %s = ''%s''', table_name, new_column_name,current_id , column_name, val );
        END LOOP;

        /* Uncomment this if you want to drop the flat column 
        raise notice 'Dropping colmn';
        execute format ('alter table %s drop column %s', table_name, column_name);
        */
        
    END;
    $$ LANGUAGE plpgsql;

The first line creates or updates the script. You can just copy over this script to an SQL window and run it as many times as you like (making changes
between runs) and the script will be always updated. The function that is created is actually a procedure since it returns ``void`` and takes two parameters.
The ``DECLARE`` section that follows contains all the variables that are used in the script:

* ``val`` is the current value of the category when looping through their values
* ``res`` is a boolean variable used for a conditional
* ``new_table_name`` is the name of the table that will be created
* ``new_column_name`` is the name of the column that will be added to the old table
* ``current_id`` is the id of the last inserted value in the new table

After the ``BEGIN`` the actual procedure starts: First the values of ``new_table_name`` and ``new_column_name`` are initialized to be used throughout the code and
then the new table is dropped (if exists) and re-created. Noticce the ``execute format (parameter)`` function that executes the SQL contained in the parameter which
is a string and is constructed using the variables we've defined. The next line checks if the old table has the new column (i.e category_id) and saves
the result in the ``res`` variable to check if the new column exists and if not add it to the old table.

A loop enumerating all unique values of the category column of the old table is then executed. Notice that ``val`` will contain a single value since the SQL that is executed
will return a single column (that's why it is declared as varchar). If we returned more than one column from the select the val could be declared as ``record`` and access its
properties through dot notation (``val.prop1`` etc). The value is inserted to the newly created table using a ``insert into table values () returning id`` SQL syntax  
(so that the new id will be returned - this is an insert/select hybrid command) and saved to the ``current_id`` variable. The ``current_id`` variable then is used to update
the new column that was added to the old table with the proper foreign key value. 

Notice that I've a commented out code in the end - if you want you can uncomment it and the old (flat) column will be dropped - so in my examply the ``category`` column will be
removed since I will have ``category_id`` to find out the name of each category. I recommend to uncomment this and actually drop the column since when you have both ``category``
and ``category_id`` the values of these two columns are going to get out of sync and since you'll have duplicate information your table will be even more non-normalized. You can
of course keep the column to make sure that the script works as you want since if the column is not dropped you can easily return to the previous state of the database by 
removeing the new table and column.

To call it just run ``select export_relation('part', 'category')`` and you should see some debug info in the messages tab. When the script is finished you'll have the
``part_category`` table and ``category_id`` column in the ``part`` table.


.. _`for reasons which at this moment must be all too obvious`: http://www.imdb.com/title/tt0057012/quotes?item=qt0454452
