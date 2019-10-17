Declarative Ecto query sorting
##############################

:date: 2019-10-17 12:20
:tags: elixir, phoenix, ecto, queries, declarative
:category: elixir
:slug: declarative-ecto-query-sorting
:author: Serafeim Papastefanos
:summary: Being able to declare your Ecto query sorting even on fields spanning joins


In a `previous article`_ I presented a method for declaring dynamic filters for your ecto queries.
Continuing this article, I'll present here a way to allow dynamic sorting for your queries using
fields that may even span relations.

What will it do
---------------

The solution is a couple of function that can be put inside the ``QueryFilterEx`` I mentioned
in the `previous article`_. Please make sure that you've completely read and understand this
article before continuing here.

To use the dynamic sorting function you'll need to declare the fields that would allow sorting using
a simple array of strings. The sort fields should then be added as links to your phoenix page which 
will then pass an ``order_by=field_name`` query parameter to your controller.

The module has a very simple API consisting of a single function:

* ``sort_by_params(query, params, allowed_sort_fields)``: Pass it the query, the ``GET`` request parameters you got from your form and the declared sort fields array to return you a sorted query

You can find a sample of the technique presented in this article in my PHXCRD repository:
https://github.com/spapas/phxcrd  for example in the ``user_controller`` or ``authority_controller``.


Preparing the query
-------------------

In order to use dynamic sorting you'll need to properly "prepare" your Ecto query by *naming all your relations*  
as I've already explained in the `previous article`_.

Declaring the sort fields
-------------------------

To declare the sort fields you'll just add an array of fields you'll want to allow sorting on. Each field
should have the form ``binding_name__field_name`` where ``binding_name`` is the name of the table 
you've declared in your
query and ``field_name`` is the name of the field that the query will be sorted by. This is the way 
that the sort
fields will also be declared in the phoenix html page. Django users will definitely remember the 
``model__field`` convention.

Declaring the sort fields here and using them again in the html page may seem reduntant, however
it is absolute necessary to declare a priori which fields are allowed because the sort http params 
will be received
as strings and to be used in queries these strings will be converted to atoms. The number of atoms is
finite (there's an absolute limit of allowed atoms in an erlang program; if that limit is surpassed
your program will crash) so you can't allow the user to pass whatever he wants (so if the ``order_by``
parameter does not contain one of the fields you declare here then no strings will be converted to atoms).


Integrating with a controller
-----------------------------

As an example let's see how the dynamic sort fields will be integrated with the phxcrd user_controller. 
The query I'd like to filter on is the following (see that everything I'll need is named using ``:as``):

.. code-block:: elixir

    from(u in User, as: :user,
      left_join: a in Authority, as: :authority,
      on: a.id == u.authority_id,
      left_join: up in UserPermission,
      on: up.user_id == u.id,
      left_join: p in Permission, as: :permission,
      on: up.permission_id == p.id,
      preload: [authority: a, permissions: p]
    )

To declare the sort fields I like to create a module attribute ending with ``sort_fields``, something like
``@user_sort_fields`` for example. Here's the sort fields I'm going to use for user_controller:

.. code-block:: elixir

  @user_sort_fields [
    "user__username", "user__name", "user__last_login"
  ]

So it will only allow the ``user.username``, ``user.name`` and ``user.last_login`` fields for sorting.
I could easily sort by ``authority.name`` or ``permission.name`` in a similar fashion.

Finally, here's the full code of the index controller:

.. code-block:: elixir

  def index(conn, params) do
    changeset = QueryFilterEx.get_changeset_from_params(params, @user_filters)

    users =
      from(u in User,
        as: :user,
        left_join: a in Authority, as: :authority,
        on: a.id == u.authority_id,

        left_join: up in UserPermission,
        on: up.user_id == u.id,
        left_join: p in Permission, as: :permission,
        on: up.permission_id == p.id,
        preload: [authority: a, permissions: p]
      )
      |> QueryFilterEx.filter(changeset, @user_filters)
      |> QueryFilterEx.sort_by_params(params, @user_sort_fields)
      |> Repo.all()

    render(conn, "index.html", users: users, changeset: changeset)
  end

Notice that this is exactly the
same as the controller I discussed in the dynamic filters article with the addition of the 
``QueryFilterEx.sort_by_params(params, @user_sort_fields)`` pipe to do the sorting.

The template
------------

The template for the user index action is also the same with a couple of minor changes: Instead of 
using a static header for the table title I will use a link that will change the sorting order:

.. code-block:: html

  <thead>
    <tr>
      <th>
        <%= link gettext("Username"), to: create_order_url(@conn, "user__username") %>
      </th>
      <th>
        <%= link gettext("Name"), to: create_order_url(@conn, "user__name") %>
      </th>
      <th>First name</th>
      <th>Last name</th>
      <th>Email</th>
      <th>Am / Am phxcrd</th>
      <th>Kind</th>

      <th>
        <%= link gettext("Last login"), to: create_order_url(@conn, "user__last_login") %>
      </th>
      <th>Is enabled</th>

      <th></th>
    </tr>
  </thead>

Notice that I just used the ``create_order_url`` function passing it the ``@conn`` and the 
sort field. This ``create_order_url`` function is implemented in a module I include in
all my views and will properly add an ``order_by=field`` in the url (it will also add
an ``order_by=-field`` if the same header is clicked twice). I will explain it more 
in the following sections.

Finally, please notice that if you use pagination and sorting you need to properly handle the ``order_by``
query parameter when creating the next-previous page links. Actually, there are three things
competing on their url parameter dominance; I'd like to talk about that in the next interlude.

Interlude: HTTP GET parameter priority
======================================

Now, in an index page you will probably have three things all of which will want to put parameters
to your urls to be activated:

* Query filtering; this will put a ``filter`` query parameter to filter your query. Notice that because of how phoenix works (it allows maps in the query parameters) the filter can be a single query parameter but contain multiple filters (i.e the filter will be something like ``%{"key1" => "value1", "key2" => "value2"}``
* Order by: This will put an ``order_by`` query parameter to denote the field that the query will be sorted
* Pagination: This will put an ``page`` query parameter to denote the current page

I like to give them a priority in the order I've listed them; when one of them is changed, it will
*clear* the ones following it. So if the query filters are changed both the pagination and the order by
fields will be cleared, if the order by field is changed then only the pagination field will be cleared
but if the pagination field is changed both the query filters and the order by fields will be kept there.

I think that's the best way to do it from an UX point of view; try to think about it and you'll probably
agree.

How does this work?
-------------------

In this section I'll try to explain exactly how the dynamic sort fields work.

So I'll split this explanation in two parts: Explain ``create_order_url`` 
and then explain ``sort_by_params``.

``create_order_url`` 
=====================

This function receives three parameters: The current ``@conn``, the name of a ``field`` to
sort by and an optional list of query parameters that need to be kept while creating the
order by links. I've put this function in a ``ViewHelpers`` module that I am including to
all my views (by adding an ``import PhxcrdWeb.ViewHelpers`` line to the ``PhxcrdWeb`` module).

Let's take a look at the code:

.. code-block:: elixir

  def create_order_url(conn, field_name, allowed_keys \\ ["filter"]) do
    Phoenix.Controller.current_url(conn, get_order_params(conn.params, allowed_keys, field_name))
  end

This doesn't do much, it just uses the phoenix's ``current_url`` that generates a new
url to the current page, passing it a dictionary
of http get parameters that should be appended to the url that 
are created through ``get_order_params``. Notice that there's an
``allowed_keys`` parameter that contains the query parameters that we need to keep after
the sorting (see the previous interlude). 
By default I pass the ``filter`` query parameter so if theres a filter (check
my previous article) it will keep it when sorting (but any pagination will be cleared;
if I sort by a new field I want to go to the first page there's no reason for me to keep
seeing the page I was on before changing the order by).

The ``get_order_params`` receives the query parameters of the current connection (as a map),
the allowed keys I mentioned before and the actual name of the field to sort on. This method is a
little more complex:

.. code-block:: elixir
  
  defp get_order_params(params, allowed_keys, order_key) do
    params
    |> Map.take(allowed_keys ++ ["order_by"])
    |> Enum.map(fn {k, v} -> {String.to_atom(k), v} end)
    |> Map.new()
    |> Map.update(
      :order_by,
      order_key,
      &case &1 do
        "-" <> ^order_key -> order_key
        ^order_key -> "-" <> order_key
        _ -> "-" <> order_key
      end
    )
  end

It only keeps the parameters in the ``allowed_keys`` list and the current ``order_by`` parameter 
(if there's one)  discarding everything else. It will then convert the keys of the map to atoms and 
put them in a new map. Finally, it will update the ``order_by`` field (if exists) either by 
switching the ``-`` in front of the field to declare asc/desc sorting or adding it for the field 
that was clicked. Actually the logic of that ``Map.update`` is the following:

* If there's no ``:order_by`` key then add it and assign the passed ``order_key``
* If the current value of ``:order_by`` is equal to ``order_key`` with or without a ``-`` then toggle the ``-`` (this happens when you click on a field that is already used for sorting)
* If the current value of ``:order_by`` is anything else (i.e not the same as the ``order_key``) then just change ``:order_by`` to ``-orderKey`` (this happens when there's sorting but you click on a different field, not the one used for the sorting)

Notice that this juggling between map, list of keywords and then map again (using ``Enum.map`` and then
``Map.new`` etc) is needed because
the query parameters are in a map with strings as keys form (``%{"key" => "value"}``) while
the ``current_url`` function needs the query params in a map with atoms as keys form 
(``%{key: "value"}``).


``sort_by_params``
==================

The ``sort_by_params`` method gets three parameters: The ``query`` that will be sorted, 
the existing http parameters map (so as to retrieve the ``order_by`` value)
and the declared list of allowed sorting fields. Let's take a look at it:

.. code-block:: elixir

  def sort_by_params(qs, %{"order_by" => "-" <> val}, allowed),
    do: do_sort_by_params(qs, val, :asc, allowed)

  def sort_by_params(qs, %{"order_by" => val}, allowed),
    do: do_sort_by_params(qs, val, :desc, allowed)

  def sort_by_params(qs, _, _), do: qs

This multi-legged function will only do something if there's an ``order_by`` parameter in the http
parameters (else it will just return the query as is) and will call ``do_sort_by_params`` passing 
it the received query, 
either ``:asc`` or ``:desc`` (depending if there's a ``-`` in front of the value) and the
received allowed fields list. 

The ``do_sort_by_params`` makes sure that the passed parameter is in the allowed list 
and if yes
it creates the atoms of the binding and field name (using ``String.to_atom``) and
does the actual sorting to the passed query:

.. code-block:: elixir

  defp do_sort_by_params(qs, val, ord, allowed) do
    if val in allowed do
      [binding, name] = val |> String.split("__") |> Enum.map(&String.to_atom/1)
      qs |> order_by([{^binding, t}], [{^ord, field(t, ^name)}])
    else
      qs
    end
  end

The line ``qs |> order_by([{^binding, t}], [{^ord, field(t, ^name)}])`` may seem a little 
complex but it has been thoroughly explained in the previous article.

Conclusion
----------

By using the methods described here you can easily add a dynamic sorting to your queries
through fields that may span relations just by creating a bunch of http GET links 
and passing them an ``order_by`` query parameter.


.. _`previous article`: https://spapas.github.io/2019/07/25/declarative-ecto-query-filters/
.. _`favorite Django features`: https://spapas.github.io/2017/10/11/essential-django-packages/
.. _django-filter: https://github.com/carltongibson/django-filter/:
.. _`Elixir forum`: https://elixirforum.com/
.. _`create dynamic bindings`: https://elixirforum.com/t/create-dynamic-bindings-for-where-clause/23797/7
.. _`schemaless one`: https://hexdocs.pm/ecto/Ecto.Changeset.html#module-schemaless-changesets
.. _`where/3`: https://hexdocs.pm/ecto/Ecto.Query.html#where/3
.. _`cast/4`: https://hexdocs.pm/ecto/Ecto.Changeset.html#cast/4