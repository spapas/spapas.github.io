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

## Conneting to a Microsoft Access database from python

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
print(pypyodbc.drivers())
```

If you have installed the correct Microsoft Access Database Engine 2010 Redistributable you should see .accdb somewhere in the output, like this:

```python
['Driver da Microsoft para arquivos texto (*.txt; *.csv)', 'Driver do Microsoft Access (*.mdb)', 'Driver do Microsoft dBase (*.dbf)', 'Driver do Microsoft Excel(*.xls)', 'Driver do Microsoft Paradox (*.db )', 'Microsoft Access Driver (*.mdb)', 'Microsoft Access-Treiber (*.mdb)', 'Microsoft dBase Driver (*.dbf)', 'Microsoft dBase-Treiber (*.dbf)', 'Microsoft Excel Driver (*.xls)', 'Microsoft Excel-Treiber (*.xls)', 'Microsoft ODBC for Oracle', 'Microsoft Paradox Driver (*.db )', 'Microsoft Paradox-Treiber (*.db )', 'Microsoft Text Driver (*.txt; *.csv)', 'Microsoft Text-Treiber (*.txt; *.csv)', 'SQL Server', 'Oracle in OraClient10g_home1', 'SQL Server Native Client 11.0', 'ODBC Driver 17 for SQL Server', 'Microsoft Access Driver (*.mdb, *.accdb)', 'Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)', 'Microsoft Access dBASE Driver (*.dbf, *.ndx, *.mdx)', 'Microsoft Access Text Driver (*.txt, *.csv)', 'Microsoft Access Text Driver (*.txt, *.csv)']
```

If on the other hand you can't access .accdb files you'll get much less options:

```python
['SQL Server', 'PostgreSQL ANSI(x64)', 'PostgreSQL Unicode(x64)', 'PostgreSQL ANSI', 'PostgreSQL Unicode', 'SQL Server Native Client 11.0', 'ODBC Driver 17 for SQL Server', 'ODBC Driver 17 for SQL Server']
```