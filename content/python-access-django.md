Title: Accessing MS Access databases from Python and Django
Date: 2023-03-22 15:20
Tags: access, python, django, database, windows, accdb, mdb
Category: python
Slug: access-microsoft-access-python-django
Author: Serafeim Papastefanos
Summary: Accessing data from a Microsoft Access database with Django


Have you ever needed to use data from a Microsoft Access database on a Django project? 
If so, you might have found that the data is contained in an .accdb file, which can make accessing it a challenge.
Actually, access files are either .mdb (older versions) and .accdb (more current versions); although the 
.mdb files is easier to access from python, most Access database would be .accdb nowadays.

The naive/simple way to access this data is to bite the bullet, install Access on your computer 
and use it to export the tables one by one in a 
more "open" format (i.e xlsx files). After some research I found out that there are ways to connect to 
this Access database through python and querying it directly. Thus I decided to implement a more automatic method 
of exporting your data. In this article, I'll walk you through the steps to accomplish this, 
specifically we'll cover how to:

* Connect to an accdb database 
* Export all the tables of that database to a json file
* Create a models.py based on the exported data
* Import the json data that was exported into the newly created models

For the first two steps we'll only use python. For the last two we'll also need some Django.
By the end of this article, you'll have a streamlined process for accessing your Microsoft 
Access data in your Django projects.



## Connecting to a Microsoft Access database from python

To be able to connect to an Access database from python you can use the
[pypyodbc](https://github.com/pypyodbc/pypyodbc). This is a pure-python library that can connect
to ODBC. To install it run `pip install pypyodbc`; since this is a pure-python the installation should
be always successfull.

However, there is an important caveat when working with .accdb databases:
*You must use Windows* and install 
[Microsoft Access Database Engine 2010 Redistributable](https://www.microsoft.com/en-US/download/details.aspx?id=13255).
This is necessary to ensure that the correct drivers are available, you can also take a look at 
the instructions from pyodbc [here](https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access).

When installing the Access Redistributable, it's crucial to remember that you need to install
either the 32-bit or 64-bit of the Access Redistributable 
depending on your python (you can't install both). 
To check if your python is 32bit or 64bit run `python` and check if it says 32 or 64 bit. Also
please notice that you may be able to install *only* the 32bit or *only* the 64bit version if you have an MS Office installed
(the Access Redistributable will match the MS Office bitness).

If that's the case then my recommendation would be to generate a new virtualenv (similiar to the bitness of the 
Access Redistributable you've installed on your system). Then install pypyodbc on that virtualenv and you should be fine.

If you want to use a .mdb database you should be able to do it without installing anything on Windows and it also should
be possible on Unix (I haven't tested it though). 

To ensure that you've got the correct drivers, run the following snippet
on a python shell:

```python
import pypyodbc
print('\n'.join(pypyodbc.drivers()))
```

If you have installed the correct Microsoft Access Database Engine 2010 Redistributable you should see .accdb somewhere in the output, like this:

```
Microsoft Access Driver (*.mdb)
Microsoft dBase Driver (*.dbf)
Microsoft Excel Driver (*.xls)
Microsoft ODBC for Oracle
Microsoft Paradox Driver (*.db )
Microsoft Text Driver (*.txt; *.csv)
SQL Server
Oracle in OraClient10g_home1
SQL Server Native Client 11.0
ODBC Driver 17 for SQL Server
Microsoft Access Driver (*.mdb, *.accdb)
Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)
Microsoft Access dBASE Driver (*.dbf, *.ndx, *.mdx)
Microsoft Access Text Driver (*.txt, *.csv)
```

If on the other hand you can't access .accdb files you'll get much less options:

```
SQL Server
PostgreSQL ANSI(x64)
PostgreSQL Unicode(x64)
PostgreSQL ANSI
PostgreSQL Unicode
SQL Server Native Client 11.0
ODBC Driver 17 for SQL Server
```

In any case, after you've installed the correct drivers you can connect to the database 
(let's suppose it's named `access_data.accdb` on the parent directory) like this:

```python
import pypyodbc

pypyodbc.lowercase = False
conn = pypyodbc.connect(
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    + r"Dbq=..\\access_data.accdb;"
)
cur = conn.cursor()

for row in cur.tables(tableType="TABLE"):
    print(row)

```

If everything's ok the above will print all the tables that are contained in the database.

## Exporting the data from the Access database to a json file

After you're able to connect to the database you can export all the data to a json file. Actually we'll export both the data of the database and a "description" of the data (the names of the tables along with their columns and types). The description of the data will be useful later. 

The general idea is:

1. Connect the database
1. Get the names of the tables in a list
1. For each table
    * Export a description of its columns
    * Export all its data
1. Write the description and the data to two json files


This is done by running the following snippet:

```python
import pypyodbc
import struct
import json
from datetime import datetime, date
import decimal

print("running as {0}-bit".format(struct.calcsize("P") * 8))

def normalize(s):
    """A simple function to normalize table names"""
    return s.lower().replace(" ", "_")


conn = pypyodbc.connect(
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    + r"Dbq=..\\access_data.accdb;"
)
cur = conn.cursor()
tables = []
for row in cur.tables(tableType="TABLE"):
    # Only get the table names
    tables.append(row[2])

# data will contain the data of all tables. It will have the following structure:
# {"table_1": [{"column_1": value, "column_2": value}, ...], "table_2": ...}
data = {}
# descriptions will have  a description of all the tables. It will have the following structure:
# [
#   {
#       "table_name": "table 1",
#       "fixed_table_name": "table_1",
#       "columns": [
#           {"name": "column_1", "fixed_name": "column_1","type": "str"},
#           {"name": "column_2", "fixed_name": "column_2","type": "int"},
# ]
descriptions = []

for table_name in tables:
    fixed_table_name = normalize(table_name)
    print(f"~~~~~~~~~~~~~{table_name} {fixed_table_name}~~~~~~~~~~~~~")
    q = f'SELECT * FROM "{table_name}"'
    description = {
        "table_name": table_name,
        "fixed_table_name": fixed_table_name,
        "columns": [],
    }
    descriptions.append(description)

    cur.execute(q)
    # Here we get the description of the columns of the table from the cursor; we'll use that to fill the description.columns list
    columns = cur.description
    for c in columns:
        description["columns"].append(
            {"name": c[0], "fixed_name": normalize(c[0]), "type": c[1].__name__}
        )

    print("")

    # And here we retrieve the data of the whole table
    # Notice we use some double for loop comprehension to 
    # create a json object with a column_name: value structure
    # for each row
    data[fixed_table_name] = [
        {normalize(columns[index][0]): column for index, column in enumerate(value)}
        for value in cur.fetchall()
    ]

cur.close()
conn.close()

# This is a function to serialize datetime and decimal objects 
# to json; without it the json.dump function will fail if the 
# results contain dates or decimals
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError("Type %s not serializable" % type(obj))


with open("..\\access_description.json", "w") as outfile:
    # Notice the default=json_serial 
    json.dump(descriptions, outfile, default=json_serial)

with open("..\\access_data.json", "w") as outfile:
    json.dump(data, outfile, default=json_serial)
```

If you run the above code and don't see any errors you should have two json files in the parent directory: `access_description.json` and `access_data.json`. The dump of your access database is complete!

## Creating a models.py based on the exported data

Now that we have the description of the data in our database it is possible to create a small script that would help us
generate the models for importing that data into Django. This could by done by a snippet similar to this:

```python
import json

def get_ctype(t):
    """Depending on the type of each column add a different field in the model"""
    if t == "str":
        return "TextField(blank=True, )"
    elif t == "int":
        return "IntegerField(blank=True, null=True)"
    elif t == "float":
        return "FloatField(blank=True, null=True)"
    elif t == "bool":
        return "BooleanField(blank=True, null=True)"
    elif t == "datetime":
        return "DateTimeField(blank=True, null=True)"
    elif t == "date":
        return "DateField(blank=True, null=True)"
    elif t == "Decimal":
        return "DecimalField(blank=True, null=True, max_digits=15, decimal_places=5)"
    else:
        print(t)
        raise NotImplementedError

# Load the descriptions we created in the previous step
descriptions = json.load(open("..\\access_description.json"))

# mlines will be an array of the lines of the models.py file
mlines = ["from django.db import models", "", ""]

for d in descriptions:
    # Create a model for each table
    mname = d["fixed_table_name"].capitalize()
    mlines.append(f"class {mname}(models.Model):")
    for c in d["columns"]:
        ctype = get_ctype(c["type"])
        mlines.append(f"    {c['fixed_name']} = models.{ctype}")
    mlines.append("")
    mlines.append("    class Meta:")
    mlines.append(f"        db_table = '{d['fixed_table_name']}'")
    mlines.append(f"        verbose_name = '{d['table_name']}'")

    mlines.append("")
    mlines.append("")


with open("..\\access_models.py", "w", encoding="utf-8") as outfile:
    outfile.write("\n".join(mlines))
```

This will generate a fine named access_models.py. You should edit this file a 
to add your primary and foreign keys. In an ideal world this would be done automatically,
however I couldn't find a way to extract the primary and foreign keys of the tables from
the Access database. Also by default I've set all fields to allow blank and null values; please
you should fix that according to your needs.

After you edit the file, create a new app in your Django project and
copy the file to the models.py file of the new app. Add that app to your `INSTALLED_APPS` in
the settings.py file
and run `python manage.py migrate` to create the tables in your database.


## Import the json data to Django

The final piece of the puzzle is to import the data we extracted before directly in Django.
Because we know the names of all the models and fields this is trivial to do:

```python
from django.core.management.base import BaseCommand
import json
from django.db import transaction
from access_data import models

# This is a list of all the fields that are foreign keys; these need special handling
FK_FIELDS = [
    # ...
]

# You need to add the table names from the access database here. This is required
# if you have relations in order to add first the tables without dependencies and last
# the tables that belong on these 
TABLE_NAMES = [
    # ...
]

def fix_fks(k):
    """Add _id to the end of the field name if it is a foreign key to pass the pk of the
    foreign key instead of the whole object"""
    if k in FK_FIELDS:
        return k + '_id'
    return k

def get_model_by_table(table):
    """Get the model by the table name"""
    return getattr(models, table.capitalize())

class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):

        with open("..\\access_data.json") as f:
            j = json.load(f)

        # Delete the existing data before importing. This is optional but I find it useful
        # Notice that we delete the tables in reverse order to avoid foreign key errors
        for table in reversed(TABLE_NAMES):
            get_model_by_table(table).objects.all().delete()

        for table in TABLE_NAMES:
            for row in j[table]:
                # Create a dictionary with the column name: column value;
                # notice the fix_fks to add the _id to the column
                row_ok = {fix_fks(k): v for k,v in row.items()}
                print(row_ok)
                # Create the object; we could add thse to an array and do a bulk_create instead
                get_model_by_table(table).objects.create(**row_ok)
```

The above code may error out if you have missing or bad data in your database. You should fix accordingly.

## Conclusion

In conclusion, accessing and using data from Microsoft Access databases in Django may seem daunting at first, 
but with the right tools and techniques, it can be a straightforward process. 
By using the pypyodbc library and following the instructions outlined in this post, you can connect to your 
.mdb or .accdb database and export its tables and schema to JSON files. 
From there, it is trivial to create a models.py file for Django and 
a management command to import the data.

Although I've presented these steps as separate snippets, you could also combine them into a 
single management command within Django. The possibilities are endless, and with a little bit of 
creativity, you can tailor this approach to your specific needs and data.


