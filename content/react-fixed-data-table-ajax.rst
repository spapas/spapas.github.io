Ajax data with Fixed Data Table for React
#########################################

:date: 2015-12-22 15:20
:tags: javascript, react, fixed-data-tables, FixedDataTable 
:category: javascript
:slug: ajax-with-react-fixed-data-table
:author: Serafeim Papastefanos
:summary: A simple demonstration on using FixedDataTable with Ajax data

.. contents::

Introduction
------------

FixedDataTable_ is a nice React component from Facebook that is used to render tabular data.
Its main characteristic is that it can handle many rows without sacrificing performance, however
probably due to this fact I was not able to find any examples for loading data using Ajax - all
examples I was able to find had the data already loaded (or created on the fly). 

So, although FixedDataTable is able to handle many rows, I am against transfering all of them to the user 
whenever our page loads since at most one page of data will be shown on screen (30 rows or so ?) - 
any other actions (filtering, sorting, aggregate calculations etc) should be done on the server. 

In the following I will present a simple, react-only example with a FixedDataTable that can be 
used with server-side, asynchronous, paginated data. 

Our project
-----------

Let's see an example of what we'll build:

.. image:: /images/ajax_fixed_data_tables.gif
  :alt: Our project
  :width: 600 px

As a source of the data I've used the `Star Wars API`_ and specifically its `People API`_ by issuing
requests to http://swapi.co/api/people/?format=json. This will return an array of people from the
star wars universe in JSON format - the results are paginated with a page size of 10 (and we can switch
to another page using the extra ``page=`` request parameter). 

I will use es6 with the object spread operator (as described in `a previous article <{filename}using-browserify-es6.rst>`_)
to write the code, using a single main.js as a source which will be transpiled to ``dist/bundle.js``. 

The placeholder HTML for our application is:

.. code::

    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8" />
        <title>Hello Ajax Fixed Data Table!</title>
        <link rel="stylesheet" href='https://cdnjs.cloudflare.com/ajax/libs/fixed-data-table/0.6.0/fixed-data-table.min.css'>
      </head>
      <body>
        <div id="main"></div>
        <script type="text/javascript" src='dist/bundle.js' ></script>
      </body>
    </html>

The versions that are used are react 14.3 and fixed-data-table 0.6.0. You can find this project in github @
https://github.com/spapas/react-tables -- tag name ``fixed-data-table-ajax``.

How FixedDataTable gets its data
--------------------------------

The data of a ``FixedDataTable`` component is defined through a number of ``Column`` components
and specifically, the ``cell`` attribute of that component which sould either return be a static string
to be displayed in that column or a React component (usually a ``Cell``) that will be displayed in
that column or even a function that returns a string or a react component. The function (or component) 
passed to ``cell`` will have an object with a ``rowIndex`` attribute (among others) as a parameter,
for example the following

.. code::

    <Column
      header={<Cell>Url</Cell>}
      cell={props => props.rowIndex}
      width={200}
    />
    
will just display the rowIndex for each cell. 

So we can see that for each cell that FixedDataTable wants to display it will use its corresponding
``cell`` attribute. 
So, a general though if we wanted to support asynchronous, paginated data
is to check the rowIndex and retrieve the correct page asynchronously.
This would lead to a difficulty: What should the ``cell`` function return? We'll try to resolve this
using an ``AjaxCell`` function that should return a react componet to put in the cell:

AjaxCell: Non working version 1
-------------------------------

A first sketch of an ```AjaxCell`` component could be something like this: 

.. code::

    // Careful - not working
    const AjaxCell1 = ({rowIndex, col, ...props}) => {
        let page = 1;
        let idx = rowIndex;
        if(rowIndex>=pageSize) {
            page = Math.floor(rowIndex / pageSize) + 1;
            idx = rowIndex % pageSize;
        }
        fetch('http://swapi.co/api/people/?format=json&page='+page).then(function(response) { 
            return response.json();
        }).then(function(j) {
            // Here we have the result ! But where will it go ? 
        });
        return /// what ?
    }
  
The col attribute will later be used to select the attribute we want to display in this cell.
The ``page`` and ``idx`` will have the correct page number and idx inside that page (for example,
if ``rowIndex`` is 33, ``page`` will be 4 and idx will be 3. The problem with the above is that
the fetch function will be called *asynchronously* so when the AjaxCell returns it will *not* have
the results (yet)! So we won't be able to render anything :( 

AjaxCell: Non working version 2
-------------------------------

To be able to render *something*, we could put the results of fetching a page to a ``cache`` dictionary -- and only
fetch that page if it is not inside the ``cache`` - if it is inside the cache then we'll just return
the correct value: 

.. code::

    // Careful - not working correctly
    const cache = {}
    const AjaxCell2 = ({rowIndex, col, forceUpdate, ...props}) => {
        let page = 1;
        let idx = rowIndex;
        if(rowIndex>=pageSize) {
            page = Math.floor(rowIndex / pageSize) + 1;
            idx = rowIndex % pageSize;
        }
        if (cache[page]) {
            return <Cell>{cache[page][idx][col]}</Cell>
        } else {
            console.log("Loading page " + page);
            fetch('http://swapi.co/api/people/?format=json&page='+page).then(function(response) { 
                return response.json();
            }).then(function(j) {
                cache[page] = j['results'];
            });
        }
        return <Cell>-</Cell>;
    }

The above will work, since it will return an empty (``<Cell>-</Cell>``) initially but when the 
``fetch`` returns it will set the ``cache`` for that page and return the correct value (``<Cell>{cache[page][idx][col]}</Cell>``).

However, as can be understood, when the page first loads it will call ``AjaxCell2`` for all visible cells --
because fetch is asynchronous and takes time until it returns (and sets the cache for that page), so the
``fetch`` will be called for *all* cells! 

AjaxCell: Non working version 3
-------------------------------

``fetch`` ing each page multiple times is of course not acceptable, so we'll add a ``loading`` flag
and ``fetch`` will be called only when this flag is ``false``, like this:

.. code::

    // Not ready yet
    const cache = {};
    let loading = false;
    const AjaxCell2 = ({rowIndex, col, ...props}) => {
        let page = 1;
        let idx = rowIndex;
        if(rowIndex>=pageSize) {
            page = Math.floor(rowIndex / pageSize) + 1;
            idx = rowIndex % pageSize;
        }
        if (cache[page]) {
            return <Cell>{cache[page][idx][col]}</Cell>
        } else if(!loading) {
            console.log("Loading page " + page);
            loading = true;
            
            fetch('http://swapi.co/api/people/?format=json&page='+page).then(function(response) { 
                return response.json();
            }).then(function(j) {
                cache[page] = j['results'];
                loading = false;
            });
        }
        return <Cell>-</Cell>;
    }
    
This works much better - the cells are rendered correctly and each page is loaded only once. However, if for example
I tried to move to the end of the table quickly, I would see some cells that are always loading (they never get their correct value). This is because 
there is no way to know that the fetch function has actually completed in order to update with the latest (correct) value of that
cell and will contain the stale placeholder (``<Cell>-</Cell>``) value. 

AjaxCell: Final version
-----------------------

To clear the stale data we need to do an update to the table data
when each fetch is finished -- this should be done by a callback that will be passed to the ``AjaxCell``, like this:

.. code:: 

    const cache = {};
    let loading = false;
    const AjaxCell = ({rowIndex, col, forceUpdate, ...props}) => {
        let page = 1;
        let idx = rowIndex;
        if(rowIndex>=pageSize) {
            page = Math.floor(rowIndex / pageSize) + 1;
            idx = rowIndex % pageSize;
        }
        if (cache[page]) {
            return <Cell>{cache[page][idx][col]}</Cell>
        } else if(!loading) {
            console.log("Loading page " + page);
            loading = true;
            
            fetch('http://swapi.co/api/people/?format=json&page='+page).then(function(response) { 
                return response.json();
            }).then(function(j) {
                cache[page] = j['results'];
                loading = false;
                forceUpdate();
            });
        }
        return loadingCell;
    }

So we pass a forceUpdate callback as a property which is called when a fetch is finished. This may
result to some not needed updates to the table (since we would do a fetch + forceUpdate for non-displayed
data) but we can now be positive that when the data is loaded the table will be updated to dispaly it.

The Table container component
-----------------------------

Finally, the component that contains the table is the following: 

.. code::

    class TableContainer extends React.Component {
        render() { 
            return <Table
                rowHeight={30} rowsCount={87} width={600} height={200} headerHeight={30}>
                
                <Column
                  header={<Cell>Name</Cell>}
                  cell={ <AjaxCell col='name' forceUpdate={this.forceUpdate.bind(this)} /> }
                  width={200}
                />
                <Column
                  header={<Cell>Birth Year</Cell>}
                  cell={ <AjaxCell col='birth_year' forceUpdate={this.forceUpdate.bind(this)} /> }
                  width={200}
                />
                <Column
                  header={<Cell>Url</Cell>}
                  cell={ <AjaxCell col='url' forceUpdate={this.forceUpdate.bind(this)} /> }
                  width={200}
                />
                
            </Table>
        }
    }

I've made it a component in order to be able to bind the ``forceUpdate`` method of the component to and
``this`` and pass it to the ``forceUpdate`` parameter to the ``AjaxCell`` component. I've hard-coded
the rowsCount value -- instead we should have done an initial fetch to the first page of the API to get
the total number of rows and only after that fetch had returned display the ``<Table>`` component (left
as an exercise to the reader).

Some enchancements
------------------

Instead of displaying ``<Cell>-</Cell>`` (or ``</Cell>``) when the page loads, I propose to define a 
cell with an embedded spinner, like

.. code::

    const loadingCell = <Cell>
        <img width="16" height="16" alt="star" src="data:image/gif;base64,R0lGODlhEAAQAPIAAP///wAAAMLCwkJCQgAAAGJiYoKCgpKSkiH/C05FVFNDQVBFMi4wAwEAAAAh/hpDcmVhdGVkIHdpdGggYWpheGxvYWQuaW5mbwAh+QQJCgAAACwAAAAAEAAQAAADMwi63P4wyklrE2MIOggZnAdOmGYJRbExwroUmcG2LmDEwnHQLVsYOd2mBzkYDAdKa+dIAAAh+QQJCgAAACwAAAAAEAAQAAADNAi63P5OjCEgG4QMu7DmikRxQlFUYDEZIGBMRVsaqHwctXXf7WEYB4Ag1xjihkMZsiUkKhIAIfkECQoAAAAsAAAAABAAEAAAAzYIujIjK8pByJDMlFYvBoVjHA70GU7xSUJhmKtwHPAKzLO9HMaoKwJZ7Rf8AYPDDzKpZBqfvwQAIfkECQoAAAAsAAAAABAAEAAAAzMIumIlK8oyhpHsnFZfhYumCYUhDAQxRIdhHBGqRoKw0R8DYlJd8z0fMDgsGo/IpHI5TAAAIfkECQoAAAAsAAAAABAAEAAAAzIIunInK0rnZBTwGPNMgQwmdsNgXGJUlIWEuR5oWUIpz8pAEAMe6TwfwyYsGo/IpFKSAAAh+QQJCgAAACwAAAAAEAAQAAADMwi6IMKQORfjdOe82p4wGccc4CEuQradylesojEMBgsUc2G7sDX3lQGBMLAJibufbSlKAAAh+QQJCgAAACwAAAAAEAAQAAADMgi63P7wCRHZnFVdmgHu2nFwlWCI3WGc3TSWhUFGxTAUkGCbtgENBMJAEJsxgMLWzpEAACH5BAkKAAAALAAAAAAQABAAAAMyCLrc/jDKSatlQtScKdceCAjDII7HcQ4EMTCpyrCuUBjCYRgHVtqlAiB1YhiCnlsRkAAAOwAAAAAAAAAAAA==" />
    </Cell>
    
and return this instead. 

Also, if your REST API returns too fast and you'd like to see what would happen if the server request took too long to return, you could 
change fetch like this

.. code::


    fetch('http://swapi.co/api/people/?format=json&page='+page).then(function(response) { 
        return response.json();
    }).then(function(j) {
        setTimeout( () => {
            cache[page] = j['results'];
            loading = false;
            forceUpdate();
        }, 1000);
    });

to add a 1 second delay.


Conslusion
----------

The above is a just a proof of concept of using FixedDataTable with asynchronously loaded server-side data. 
This of course could be used for small projects (I am already using it for an internal project) but I recommend
using the `flux architecture <{filename}react-flux-tutorial.rst>`_ for more complex projects. What this more or
less means is that a store component
should be developed that will actually keep the data for each row, and a ``fetchCompleted`` action should be 
dispatched when the ``fetch`` is finished instead of calling ``forceUpdate`` directly.

.. _FixedDataTable: https://facebook.github.io/fixed-data-table/
.. _`functions are objects`: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function
.. _`Star Wars API`: http://swapi.co/
.. _`People API`: http://swapi.co/documentation#people