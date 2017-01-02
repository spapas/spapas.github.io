Creating custom components for ag-grid
######################################

:date: 2017-01-02 15:10
:tags: javascript, component, ag-grid, grid
:category: javascript
:slug: ag-grid-custom-components
:author: Serafeim Papastefanos
:summary: How to create custom components (renderers and editors) for the excellent ag-grid grid library

https://jsfiddle.net/6vmvdmzj/4/

Recently I had to integrate an application with a javascript (client-side) excel-like grid. After some research
I found out that ag-grid_ is the best javascript grid library. It has an open source version with a MIT license
so it can safely be used by all your projects and a commercial, enteprise version that includes a bunch of 
extra features. The open source version should be sufficient for most projects however I really recommend
buying the commercial version to support this great product.

The greatest characteristic of ag-grid, at least for me, is its openess and great API that enables you to
extend it to support all your needs! An example of this great API will be presented in this article where
I will implement two components that can be included in your grid:

* An array editor through which you will be able to create cells that can be used to insert a list of values. For example, if you have a grid of employees, you will be able to add a "children" cell that will contain the names of each employee's children properly separated (one line per child)
* An object editor through which you will be able to create cells that can be used to insert flat objects. For example, for the grid of employees, you may add an "address" cell that, when edited will be expanded to seperate fields for Address, City, Zip code and Country.

A common ground
---------------

First of all, let's create a simple example that will act as a common ground for our components:

.. jsfiddle:: 6vmvdmzj/6

As you can see, I have defined a bunch of columns for the grid and then create a new grid passing it the ``myGrid`` div
and the ``gridOptions`` (which are kept to a minimum). Finally, there's an event handler for button click that adds an
empty row:

.. code-block:: javascript

    var columns = [
        {
            headerName: 'ID', field: 'id', width: 50, editable: true  
        }, {
            headerName: 'Name', field: 'name', width: 100, editable: true
        }, {
            headerName: "Address", field: "address", width: 200, editable: true
        }, {
            headerName: "Children", field: "children", width: 200, editable: true
        }
    ];

    var gridOptions = {
        columnDefs: columns,
        rowData: []
    };

    new agGrid.Grid(document.querySelector('#myGrid'), gridOptions);

    document.querySelector('#addRow').addEventListener("click", function() {
        gridOptions.api.addItems([{}]);
    });

You may be able to edit both the address and the children of each employee in the above example however this is 
not intuitive. The editors will be able to enter any kind of address they want and add the children seperated by commas,
spaces, dashes or whatever they want. Of course you could add validators to enforce some formatting for these fields 
however I think that using custom components has a much better user experience.

Please notice that the above example along with the following tutorial will be implemented in pure (no-framework) javascript. Integrating
ag-grid with a javascript framework like angular or react in an SPA should not be difficult however I find it easier to adjust my SPA
so that the grid component is seperate and does not need interoperability with other SPA components since all components like renderers
and editors will be integrated to the grid!

Also, using pure javascript for your
custom components makes them faster than adding another layer of indirection through react as can be seen on the on `ag-grid react integration`_:

   If you do use React, be aware that you are adding an extra layer of indirection into ag-Grid. ag-Grid's internal framework is already highly tuned to work incredibly fast and does not require React or anything else to make it faster. If you are looking for a lightning fast grid, even if you are using React and the ag-grid-react component, consider using plain ag-Grid Components (as explained on the pages for rendering etc) inside ag-Grid instead of creating React counterparts.

Editors and renderers
---------------------

A custom column in ag-grid actually has two distinctive parts: An object that is used for rendering_ and an object that is used
for editing_ the cell value. You can have columns with the built in editor and a custom renderer, columns with the built in renderer
and a custom editor and cells with custom editors and rendererers. 

.. _ag-grid: https://www.ag-grid.com/
.. _rendering: https://www.ag-grid.com/javascript-grid-cell-rendering/
.. _editing: https://www.ag-grid.com/javascript-grid-cell-editing/
.. _`ag-grid react integration`: https://www.ag-grid.com/best-react-data-grid/index.php
