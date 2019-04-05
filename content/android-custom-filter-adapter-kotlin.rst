How to create a custom filtered adapter in Android
##################################################

:date: 2019-04-05 12:20
:tags: android, kotlin, adapter, filter
:category: android
:slug: android-custom-filter-adapter
:author: Serafeim Papastefanos
:summary: How to create a custom filtered adapter in Android; we'll be using Kotlin for this.

Introduction
------------

Android offers a nice component named AutoCompleteTextView_ that can be used to auto-fill a text box from a list of values.
In its simplest form, you just create an array adapter passing it a list of objects (that have a proper ``toString()`` method).
Then you type some characters to the textbox and by default it will filter the results searching
in the *beginning of the backing object's toString() result*.

However there are times that you don't want to look at the beginning of the string (because you want to look at the middle of the string) or
you don't want to just to search in toString() method of the object or you want to do some more fancy things in object output. For this
you must override the ``ArrayAdapter`` and add a custom ``Filter``.

Unfurtunately this isn't as straightforward as I'd like and I couldn't find a quick and easy tutorial on how it can be done.

So here goes nothing: In the following I'll show you a very simple android application that will have *the minimum viable* custom filtered
adapter implementation. You can find the whole project in github: https://github.com/spapas/CustomFilteredAdapeter but I am going to discuss
everything here also.

The application
---------------

Just create a new project with an empty activity from Android Studio. Use kotlin as the language.

The layout
----------

I'll keep it as simple as possible:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <LinearLayout
            xmlns:android="http://schemas.android.com/apk/res/android"
            xmlns:tools="http://schemas.android.com/tools"
            android:orientation="vertical"
            android:layout_width="match_parent" android:layout_height="match_parent"
            tools:context=".MainActivity">
        <TextView
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="Hello World!"
                android:textSize="32sp"
                android:textAlignment="center"/>
        <AutoCompleteTextView
                android:layout_marginTop="32dip"
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:id="@+id/autoCompleteTextView"/>
    </LinearLayout>

You should just care about the ``AutoCompleteTextView`` with an id of ``autoCompleteTextView``.

The backing data object
-----------------------

I'll use a simple PoiDao Kotlin data class for this:

.. code-block:: kotlin

    data class PoiDao(
        val id: Int,
        val name: String,
        val city: String,
        val category_name: String
    )

I'd like to be able to search to both name, city and category_name of each object. To create a list of the pois to be used to the adapter I can do something like:

.. code-block:: kotlin

    val poisArray = listOf(
        PoiDao(1, "Taco Bell", "Athens", "Restaurant"),
        PoiDao(2, "McDonalds", "Athens","Restaurant"),
        PoiDao(3, "KFC", "Piraeus", "Restaurant"),
        PoiDao(4, "Shell", "Lamia","Gas Station"),
        PoiDao(5, "BP", "Thessaloniki", "Gas Station")
    )


The custom adapter
------------------

This will be an ``ArrayAdapter<PoiDao>`` implementing also the ``Filterable`` interface:

.. code-block:: kotlin

    inner class PoiAdapter(context: Context, @LayoutRes private val layoutResource: Int, private val allPois: List<PoiDao>):
        ArrayAdapter<PoiDao>(context, layoutResource, allPois),
        Filterable {
        private var mPois: List<PoiDao> = allPois

        override fun getCount(): Int {
            return mPois.size
        }

        override fun getItem(p0: Int): PoiDao? {
            return mPois.get(p0)
        }

        override fun getItemId(p0: Int): Long {
            // Or just return p0
            return mPois.get(p0).id.toLong()
        }

        override fun getView(position: Int, convertView: View?, parent: ViewGroup?): View {
            val view: TextView = convertView as TextView? ?: LayoutInflater.from(context).inflate(layoutResource, parent, false) as TextView
            view.text = "${mPois[position].name} ${mPois[position].city} (${mPois[position].category_name})"
            return view
        }

        override fun getFilter(): Filter {
            // See next section
        }
    }

You'll see that we add an instance variable named ``mPois`` that gets initialized in the start with ``allPois`` (which is the initial list of all pois that is passed to the adapter). The mPois
will contain the *filtered* results. Then,
for ``getCount`` and ``getItem`` we return the corresponding valeus from ``mPois``; the ``getItemId`` is used when you have an sqlite backed adapter but I'm including it here for completeness.

The ``getView`` will create the specific line for each item in the dropdown. As you'll see the layout that is passed must have a ``text`` child which is set based on some of the attributes of
the corresponding poi for each position. Notice that we can use whatever view layout we want for our dropdown result line (this is the ``layoutResource`` parameter) but we need to configure
it (i.e bind it with the values of the backing object) here properly.

Finally we create a custom instance of the ``Filter``, explained in the next section.

The custom filter
-----------------

The ``getFilter`` creates an object instance of a Filter and returns it:

.. code-block:: kotlin

    override fun getFilter(): Filter {
        return object : Filter() {
            override fun publishResults(charSequence: CharSequence?, filterResults: Filter.FilterResults) {
                mPois = filterResults.values as List<PoiDao>
                notifyDataSetChanged()
            }

            override fun performFiltering(charSequence: CharSequence?): Filter.FilterResults {
                val queryString = charSequence?.toString()?.toLowerCase()

                val filterResults = Filter.FilterResults()
                filterResults.values = if (queryString==null || queryString.isEmpty())
                    allPois
                else
                    allPois.filter {
                        it.name.toLowerCase().contains(queryString) ||
                        it.city.toLowerCase().contains(queryString) ||
                        it.category_name.toLowerCase().contains(queryString)
                    }
                return filterResults
            }
        }
    }

This object instance overrides two methods of ``Filter``: ``performFiltering`` and ``publishResults``. The ``performFiltering`` is where the actual filtering is done;
it should return a ``FilterResults`` object containing a ``values`` attribute with the filtered values. In this method
we retrieve the ``charSequence`` parameter and converit it to lowercase. Then, if this parameter is not empty we filter the corresponding elements of ``allPois``
(i.e name, city and category_name in our case) using contains. If the query parameter is empty then we just return all pois. Warning java developers; here the if
is used as an expression (i.e its result will be assigned to ``filterResults.values``).

After the performFiltering has finished, the ``publishResults`` method is called. This method retrieves the filtered results in its ``filterResults`` parameter. Thus it sets
``mPois`` of the custom adapter is set to the result of the filter operation and calls ``notifyDataSetChanged`` to display the results.

Using the custom adapter
------------------------

To use the custom adapter you can do something like this in your activity's onCreate:

.. code-block:: kotlin

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val poisArray = listOf(
            // See previous sections
        )
        val adapter = PoiAdapter(this, android.R.layout.simple_list_item_1, poisArray)
        autoCompleteTextView.setAdapter(adapter)
        autoCompleteTextView.threshold = 3

        autoCompleteTextView.setOnItemClickListener() { parent, _, position, id ->
            val selectedPoi = parent.adapter.getItem(position) as PoiDao?
            autoCompleteTextView.setText(selectedPoi?.name)
        }
    }

We create the PoiAdapter passing it the poisArray and ``android.R.layout.simple_list_item_1`` as the layout. That layout just contains a textview named text. As we've already
discussed you can pass something more complex here. The ``thresold`` defined the number of characters that the user that needs to enter to do the filtering (default is 2).

Please notice that when the user clicks (selects) on an item of the dropdown we set the contents of the textview (or else it will just use the object's toString() method to set it).


.. _`AutoCompleteTextView`: https://developer.android.com/reference/android/widget/AutoCompleteTextView

