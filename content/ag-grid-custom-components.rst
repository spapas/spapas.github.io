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

Please notice that the above example along with the following components will be implemented in pure (no-framework) javascript. Integrating
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
and a custom editor and cells with custom editors and rendererers. I urge you to read the documentation_ on both renderers and 
editors in order to understand most of the decisions I have made for the implemented components.

A renderer can be:
    
* a function that receives the value of the cell and returns either an HTML string or a complete DOM object
* a class that provides methods for returning the HTML string or DOM object for the cell

The function is much easier to use however biting the bullet and providing a renderer class is better for non-trivial rendering. 
This is because the function will be called each time the cell needs to be *refreshed* (refer to the docs on what refreshing means)
while, the class provides a specific ``refresh()`` method that is called instead. This way, using the class you can generate the DOM structure
for the cell once, when it is first created and then when its value changes you'll only call its refresh method to update the value. We'll
see how this works later.

An editor is a class that should provide methods for returning the DOM structure for the cell editing (for example an ``<input>`` field)
and the current value of the field.

Both renderer and editor classes can be attached to columns using ``cellEditor`` and ``cellRenderer`` column properties. You also may 
pass per-column properties to each cell using the ``cellEditorParams`` and ``cellRendererParams`` propertie. For example, you may have
a renderer for booleans that displays icons for true/false and you want to use different icons depending on the column type, or you
may want to create a validation-editor that receives a function and accepts the value you enter only if the function returns true - the
valid function could be different for different column types.

Creating the object cell editor
-------------------------------

The first component we'll present here is an object renderer/editor. This component will receiver a list of fields and will
allow the user to edit them in a popup grouped together. Here's a fiddle with the Address of each employee using the 
object editing component:

.. jsfiddle:: 0o85uywr/3

To integrate it with the ag-grid I've added an addressFields list containg the fields of the object like this:

.. code-block:: javascript

    var addressFields = [
      {'name': 'address', 'label': 'Address' },
      {'name': 'zip', 'label': 'ZIP' },
      {'name': 'city', 'label': 'City' },
    ]

and then passed this as a parameter to both the renderer and editor for the address field:

.. code-block:: javascript

    {
        headerName: "Address", field: "address", width: 200, editable: true,
        cellRenderer: ObjectCellRenderer,
        cellEditor: ObjectEditor,
        cellEditorParams: {
          fields: addressFields
        },
        cellRendererParams: {
          fields: addressFields
        }
    }
    
The ``ObjectEditor`` and ``ObjectCellRenderer`` are the actual editor and renderer of the component. I will start by representing the renderer first:

.. code-block:: javascript

    function ObjectCellRenderer() {
    }

    ObjectCellRenderer.prototype.init = function (params) {
        this.span = document.createElement('span');
        this.span.innerHTML='';
        this.refresh(params)
    };
    
The ObjectCellRender is an javascript object to which we define an ``init`` method. This method will be called by ag-grid when
the component is first created, passing it a params object with various useful params, like the user-defined parameters (from ``cellRendererParams``)
and the actual value of othe cell. We just create an empty span DOM element that will be used to display the value of the object and call ``refresh``.

.. code-block:: javascript

    ObjectCellRenderer.prototype.refresh = function(params) {
        var res = ''
        if(params.value) {
            for(var i=0;i<params.fields.length;i++) {
                res += params.fields[i].label + ': ';
                res += params.value[params.fields[i].name] + ' ';
            }
        }
        
        this.span.innerHTML=res;
    }

    ObjectCellRenderer.prototype.getGui = function () {
        return this.span;
    };
    
The ``refresh`` method generates the text value of the cell (that will be put inside the span we created in init). It first checks if the ``value`` attribute
of ``params`` is defined and if yes, it appends the label of each object attribute (which we pass through ``cellRendererParams.fields.label``) along with its value
(which is retrieved from the ``params.value`` using ``cellRendererParams.fields.name``). Notice ag-grid puts the result of the ``getGui`` method in the cell - so
we just return the span we create. Also, we created the span element in init but filled it in refresh - to avoid it creating the same element lots of times (this would
be more imporntant of course on more expensive operations).

Now let's continue with ``ObjectEditor``:

.. code-block:: javascript

    function ObjectEditor() {
        
    }

    var onKeyDown = function(event) {
        var key = event.which || event.keyCode;
        if (key == 37 ||  // left
            key == 39 || // right
            key == 9 ) {  // tab
            event.stopPropagation();
        }
    }

    ObjectEditor.prototype.init = function (params) {
        this.container = document.createElement('div');
        this.container.style = "border-radius: 15px; border: 1px solid grey;background: #e6e6e6;padding: 10px; ";
        this.container.onkeydown = onKeyDown
        
        for(i=0;i<params.fields.length;i++) {
            var field = params.fields[i];
            label = document.createElement('label');
            label.innerHTML = field.label+': ';
            input = document.createElement('input');
            input.name = field.name;
            if (params.value) {
              var val = params.value[field.name].replace(/^\s+|\s+$/g, ""); 
              if (val && val!='') {
                  input.value = val;
              } else {
                  input.value ='';
              }
            }
            
            this.container.appendChild(label);
            this.container.appendChild(input);
            this.container.appendChild(document.createElement('br'));
        }
        
        var saveButton = document.createElement('button');
        saveButton.appendChild(document.createTextNode('Ok'))
        saveButton.addEventListener('click', function (event) {
            params.stopEditing();
        });
        this.container.appendChild(saveButton);
    };
    
The ``init`` function of ObjectEditor ise used to create a container div element that will hold the actual input elements. Then, using the fields
that were passed as a parameter to the editor it creates a label an input and a br element and inserts it to the container div. The input is
instantiated with the current value of each attribute (if it has one) while its name is taken from the name element of the fields parameter. 
Finally, a saveButton is created that will stop the editing when clicked.

.. code-block:: javascript

    ObjectEditor.prototype.getGui = function () {
        return this.container;
    };

    ObjectEditor.prototype.afterGuiAttached = function () {
        var inputs = this.container.getElementsByTagName('input');
        inputs[0].focus();    
    };

    ObjectEditor.prototype.getValue = function () {
        var res = {};
        var inputs = this.container.getElementsByTagName('input');
        for(j=0;j<inputs.length;j++) {
              res[inputs[j].name] = inputs[j].value.replace(/^\s+|\s+$/g, "");
        }
        return res;
    };

    ObjectEditor.prototype.destroy = function () {
    };

    ObjectEditor.prototype.isPopup = function () {
        return true;
    };
    
The other methods of ObjectEditor are simpler: ``getGui`` actually returns the container we built in the ``init``, ``afterGuiAttached``
is called when the component is attached to the DOM and focuses on the first input element, ``getValue`` enumerates the input elements,
takes their value (and names) and return an object with the name/value pairs, ``destroy`` dosn't do anything however it must be defined
and can be used for cleaning up if needed and ``isPopup`` returns true to display the container as a popup instead of inline.

.. _ag-grid: https://www.ag-grid.com/
.. _rendering: https://www.ag-grid.com/javascript-grid-cell-rendering/
.. _editing: https://www.ag-grid.com/javascript-grid-cell-editing/
.. _`ag-grid react integration`: https://www.ag-grid.com/best-react-data-grid/index.php
.. _documentation: https://www.ag-grid.com/documentation-main/documentation.php