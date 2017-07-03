Automatically create a category table in Postgresql by extracting unique table values
#####################################################################################

:date: 2017-07-03 15:10
:tags: postgresql, plpgsql, 
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
that the categories have properties (beyond their name) that need to be defined and used in the project. Both
of these cases mean that these categories need to be extracted from simple strings to full Django models (i.e get normalized in
their own table)!

In this post I will present a function written in PL/pgsql that will automatically normalize a column from a 
flat table like the previous. Specifically, if you have a table named ``tablex`` that has a non normalized
column named ``columny`` then when you call ``select export_relation('tablex', 'columny')`` the following
will happen:

* A new table named ``tablex_columny`` will be created. This table will contain two columns ``id`` and ``name``. If the table exists it will be dropped
* A new column named ``columny_id`` will be added to ``tablex``. This column will be a foreign key to the new table ``tablex_columny``
* For each unique value ``v`` of ``columny``:
    - Insert a new record in ``tablex_columny`` with ``v`` in the ``name`` field of the table and save the inserted id to ``current_id``
    - Set ``current_id`` to ``columny_id``  to all rows of ``tablex`` where ``columny`` is equal to ``v``

Before diving in to the script that does the above I'd like to notice that I don't usually write plpgsql 
(I actually avoid writing code in the database) however this is an ideal case of a PL/pgSQL script. The script
works however I feel that more experienced PL/pgSQL developers would write things different - if you have any
proposals please comment out and I'll be happy to incorporate them to the script
    
    
Let's now take a look at the actual script:

.. code-block:: plpgsql

    CREATE OR REPLACE FUNCTION export_relation(table_name varchar, column_name varchar)     
    RETURNS void AS $$ 
    DECLARE
        ref varchar;
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

        for ref IN execute format ('select %s from %s group by(%s)', column_name, table_name, column_name) LOOP
            RAISE NOTICE 'Inserting new value %s ...', ref;
            execute format ('insert into  %s(name) values (''%s'') returning id', new_table_name, ref) into current_id;
            raise notice 'Created ID %', current_id;
            execute format ('update %s set %s = %s where %s = ''%s''', table_name, new_column_name,current_id , column_name, ref );
        END LOOP;

        /* Uncomment this if you want to drop the flat column 
        raise notice 'Dropping colmn';
        execute format ('alter table %s drop column %s', table_name, column_name);
        */
        
    END;
    $$ LANGUAGE plpgsql;
    

select export_relation('django_content_type2', 'app_label')

.. _Werkzeug: http://werkzeug.pocoo.org/
.. _`for reasons which at this moment must be all too obvious`: http://www.imdb.com/title/tt0057012/quotes?item=qt0454452
