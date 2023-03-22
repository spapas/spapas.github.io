Title: Accessing MS Access databases from Python and Django
Date: 2023-03-22 15:20
Tags: access, python, django, database, windows, accdb, mdb
Category: python
Slug: access-microsoft-access-python-django
Author: Serafeim Papastefanos
Summary: Accessing data from a Microsoft Access database with Django

Recently I needed to use the data from a Microsoft Access database on a Django project. The data was contained on
an .accdb file. Access files are either .mdb (older versions) and .accdb (more current versions). 

The simple way to access this data is to install Access on your computer and export the tables one by one in a 
more "open" format (i.e xlsx files). However, after some research I found out that there are ways to connect to 
this Access database through python and query it. Thus I decided to implement a more automatic method of doing
that. So, in this article we'll do the following:

* Connect to an accdb database 
* Export all the tables of that database to a json file
* Create a models.py based on the exported data
* Import the json data that was exported into the newly created models

For the first two steps we'll only use python. For the last two we'll also need some Django.

## Connecting to a Microsoft Access database from python

To be able to connect to an Access database from python you'll need you should use the
[pypyodbc](https://github.com/pypyodbc/pypyodbc). This is a pure-python library that can connect
to ODBC. To install it run `pip install pypyodbc`; since this is a pure-python the installation should
be always successfull.

One thing to keep in mind is that it to connect to an .accdb database 
*you must use Windows* and install 
[Microsoft Access Database Engine 2010 Redistributable](https://www.microsoft.com/en-US/download/details.aspx?id=13255),
see the instructions from pyodbc [here](https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Microsoft-Access).

The most important thing to remember is that you need to install the 32-bit or 64-bit of the Access Redistributable 
depending on your python. To check if your python is 32bit or 64bit run python and check if it says 32 or 64 bit. Also
please notice that you may be able to install *only* the 32bit or only the 64bit version if you have an MS Office installed.
If that's the case then my recommendation would be to generate a new virtualenv (similiar to the Access Redistributable
you'll be able to instal).

If you want to use a .mdb database you should be able to do it without installing anything on Windows and it also should
be possible on Unix (I haven't tested it though). To make sure that you've got the correct drivers, run the following snippet
on a python shell:

```python
import pypyodbc
print('\n'.join(pypyodbc.drivers()))
```

If you have installed the correct Microsoft Access Database Engine 2010 Redistributable you should see .accdb somewhere in the output, like this:

```python
['Driver da Microsoft para arquivos texto (*.txt; *.csv)', 'Driver do Microsoft Access (*.mdb)', 'Driver do Microsoft dBase (*.dbf)', 'Driver do Microsoft Excel(*.xls)', 'Driver do Microsoft Paradox (*.db )', 'Microsoft Access Driver (*.mdb)', 'Microsoft Access-Treiber (*.mdb)', 'Microsoft dBase Driver (*.dbf)', 'Microsoft dBase-Treiber (*.dbf)', 'Microsoft Excel Driver (*.xls)', 'Microsoft Excel-Treiber (*.xls)', 'Microsoft ODBC for Oracle', 'Microsoft Paradox Driver (*.db )', 'Microsoft Paradox-Treiber (*.db )', 'Microsoft Text Driver (*.txt; *.csv)', 'Microsoft Text-Treiber (*.txt; *.csv)', 'SQL Server', 'Oracle in OraClient10g_home1', 'SQL Server Native Client 11.0', 'ODBC Driver 17 for SQL Server', 'Microsoft Access Driver (*.mdb, *.accdb)', 'Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)', 'Microsoft Access dBASE Driver (*.dbf, *.ndx, *.mdx)', 'Microsoft Access Text Driver (*.txt, *.csv)', 'Microsoft Access Text Driver (*.txt, *.csv)']
```

If on the other hand you can't access .accdb files you'll get much less options:

```python
['SQL Server', 'PostgreSQL ANSI(x64)', 'PostgreSQL Unicode(x64)', 'PostgreSQL ANSI', 'PostgreSQL Unicode', 'SQL Server Native Client 11.0', 'ODBC Driver 17 for SQL Server', 'ODBC Driver 17 for SQL Server']
```

In any case, after you've installed the correct drivers you can connect to the database (let's suppose it's nameed `access_data.accdb` on the parent directory) like this:

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

def fix(s):
    """A simla function to normalize table names"""
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
    fixed_table_name = fix(table_name)
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
            {"name": c[0], "fixed_name": fix(c[0]), "type": c[1].__name__}
        )

    print("")

    # And here we retrieve the data of the whole table
    # Notice we use some double for loop comprehension to 
    # create a json object with a column_name: value structure
    # for each row
    data[fixed_table_name] = [
        {fix(columns[index][0]): column for index, column in enumerate(value)}
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