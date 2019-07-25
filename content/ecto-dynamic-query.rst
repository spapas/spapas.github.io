Declarative Ecto query filters
##############################

:date: 2019-07-25 14:20
:tags: elixir, phoenix, ecto, queries, declarative
:category: elixir
:slug: declarative-ecto-query-filters
:author: Serafeim Papastefanos
:summary: Being able to declare your Ecto query filter even on fields spanning joins


Continuing my Elixir journey_ I'd like to discuss here a method to implement one of my 
`favorite Django features`_: Declarative query filters. This functionality is not a core Django 
feature but it is offered
through the excellent django-filter_ package: Using this, you can create a ``Filter`` class which defines
which fields are to be used for filtering the queryset and how each field will be queried (i.e using 
things like exact, like, year of date etc). 

This is a functionality I am greatly missing in Elixir/phoenix
so I've tried implementing it on my own. Of course, django-filter has various other capabilities that
result from the implicit generation of things that Django offers like automatically creating the html
for the declared fields, automatically declare the fields based on their types etc but such things are
not supported by phoenix in any case so I won't be trying in them here.

During my research I've seen a bunch of blog posts or packages about this thing however they didn't
properly support joins (i.e you could only filter on fields on a specific schema) or needed too much 
work to filter on joins (i.e define different filters for each part of the join). In the solution
I'll present here you'll just define a filter for the specific query you need to filter no matter how
many joins it has (just like in django-filters).

What will it do
---------------

The solution is more or less a self contained Elixir module named ``QueryFilterEx`` that can be used
to declaratively filter your queries.
To use that you'll need to declare your filters using
a simple array of maps. The filters should then be added in your form using a different input
for each filter; then your queryset will be filtered with all the values you've added to the
inputs using ``AND``.

The module has a very simple API consisting of three functions:

* ``get_changeset_from_params(params, filters)``: Pass it the ``GET`` request parameters you got from your form and the declared filters array to return you a proper changeset (which you can then use to build your form in your html)
* ``make_filter_changeset(filters, params)``: This function actually generates the changeset using the filters and a ``Map`` of ``filter_name: value`` pairs (it is actually used by ``get_changeset_from_params``)
* ``filter(query, changeset, filters)``: Filter the ``query`` using the previously created ``changeset`` and the declared filters array

You can find a sample of the technique presented in this article in my PHXCRD repository:
https://github.com/spapas/phxcrd  for example in the ``user_controller`` or ``authority_controller``.


Preparing the query
-------------------

In order to use the ``QueryFilterEx`` module you'll need to properly "prepare" your Ecto query. By preparing
I don't mean a big deal just the fact that you'll need to *name all your relations*  (or at least name all
the relations you're going to use for filtering). This is very simple to do, for example for the following
query:

.. code-block:: elixir

    from(a in Authority,
      join: ak in AuthorityKind,
      on: [id: a.authority_kind_id],
      preload: [authority_kind: ak]
    )

you can name the relations by adding two ``as:`` atoms like this:     

.. code-block:: elixir

    from(a in Authority, as: :authority,
      join: ak in AuthorityKind, as: :authority_kind,
      on: [id: a.authority_kind_id],
      preload: [authority_kind: ak]
    )

So after each `join:` you'll add a name for your joined relation (and also add a name for your initial
relation). Please notice that you can use any name you want for these (not related to the schema names).

Declaring the filters
---------------------

To declare the filters you'll just add an array of simple Elixir maps. Each map must have the following fields:

* ``:name`` This is the name of the specific filter; it is mainly used in conjunction with the queryset and the form fields to set initial values etc
* ``:type`` This is the type of the specific filter; it should be a proper Ecto type like ``:string``, ``:date``, ``:integer`` etc. This is needed to properly cast the values and catch errors
* ``:binding`` This is the name of the relation this filter concerns which you defined in your query using ``:as`` (discussed in previous section)
* ``:field_name`` This is the actual name of the field you want to filter on
* ``:method`` How to filter on this field; I've defined a couple of methods I needed but you can implement anything you want

The methods I've implemented are the following:

* ``:eq`` Equality
* ``:ilike`` Field value starts with the input - ignore case
* ``:icontains`` Field value contains the input - ignore case
* ``:year`` Field is a date or datetime an its year is the same as the value
* ``:date`` Field is a datetime and its date part is equal to the value

Anything else will just be compared using ``=`` (same as ``:eq``).

Integrating it with a controller
--------------------------------

As an example let's see how ``QueryFilterEx`` is integrated it with the phxcrd user_controller. 
The query I'd like to filter on is the following (see that everything I'll need is named using ``:as``:

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

To declare the filters I like to create a module attribute ending with ``filters``, something like
``@user_filters`` for example. Here's the filters I'm going to use for user_controller:

.. code-block:: elixir

  @user_filters [
    %{name: :username, type: :string, binding: :user, field_name: :username, method: :ilike},
    %{name: :authority_name, type: :string, binding: :authority, field_name: :name, method: :icontains},
    %{name: :permission_name, type: :string, binding: :permission, field_name: :name, method: :ilike},
    %{name: :last_login_date, type: :date, binding: :user, field_name: :last_login, method: :date}
  ]

So it will check if the ``user.username`` and ``permission.name`` start with the passed value, 
``authority.name`` contains the passed value and if the ``user.login_date`` (which is a datetime)
is the same as the passed date value.

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
      |> Repo.all()

    render(conn, "index.html", users: users, changeset: changeset)
  end

It is very simple, it just uses the ``get_changeset_from_params`` method I discussed before to
generate the changeset and then uses it to filter the query. Also please notice that it passes
the changeset to the template to be properly rendered in the filter form.

The template
------------

The template for the user index action is the following:

.. code-block:: html

  <%= form_for @changeset, AdminRoutes.user_path(@conn, :index), [method: :get, class: "filter-form", as: :filter],  fn f -> %>
    <%= label f, :username, gettext "Username" %>
    <%= text_input f, :username  %>

    <%= label f, :authority_name, gettext "Authority name" %>
    <%= text_input f, :authority_name  %>

    <%= label f, :permission_name, gettext "Permission name" %>
    <%= text_input f, :permission_name  %>

    <%= label f, :last_login_date, gettext "Last login date" %>
    <%= text_input f, :last_login_date  %>
    <%= error_tag f, :last_login_date %>

    <%= submit gettext("Filter"), class: "ml-5" %>
    <%= link gettext("Reset"), to: AdminRoutes.user_path(@conn, :index), class: "button button-outline ml-2" %>
  <% end %>
  <%= for user <- @users do %>
  <!-- display the user info -->
  <% end %>

Notice that it gets the ``@changeset`` and uses it to properly fill the initial values and display
error messages. For this case I've only added an error_tag for the ``:last_login_date`` field,
the others since are strings do not really need it since they will accept all values.

Also, the form method  form must be ``:get`` since we only filter (not change anything) and I've passed
the ``as: :filter`` option to the ``form_for`` to collect the parameters under the ``filter`` server side 
parameter (this can be anything you want and can be optionally be 
passed to ``QueryFilterEx.get_changeset_from_params`` to know which parameter the filters are collected on).

How does this work?
-------------------

In this section I'll try to explain exactly how the ``QueryFilterEx`` module works. Before continuing
I want to thank the people at the `Elixir forum`_ and #elixir-lang Freenode IRC chat 
that helped me with understanding how to be able to `create dynamic bindings`_.

So I'll split this explanation in two parts: Explain ``QueryFilterEx.get_changeset_from_params`` 
and ``make_filter_changeset`` (easy) and
then explain ``QueryFilterEx.filter`` (more difficult).

``QueryFilterEx.get_changeset_from_params`` and ``make_filter_changeset``
=========================================================================

This function generates a changeset using the GET request parameters and the list of declared filters. The
create changeset is a `schemaless one`_ since it may contains fields of various schemas (or fields that
are not even exist on a schema). To generate it it uses the `cast/4`_ function passing it a ``{data, types}``
first parameter to generate the schemaless changeset. It has two public methods: ``get_changeset_from_params``
and ``make_filter_changeset``. The ``get_changeset_from_params`` is the one we've used to integrate
with the controller and is used to retrieve the filter parameters from the request
parameters based on the collect parameter of the form we mentioned before (the ``as: :filter``). If such
parameters are found they will be passed to ``make_filter_changeset`` (or else it will pass an empty 
struct). Notice that the ``filter_name`` by default is ``"filter"`` but you can change it to anything
you want.

.. code-block:: elixir

  def get_changeset_from_params(params, filters, filter_name \\ "filter") do
    case params do
      %{^filter_name => filter_params} ->
        filters |> make_filter_changeset(filter_params)

      _ ->
        filters |> make_filter_changeset(%{})
    end
  end    

The ``make_filter_changeset`` is the function that actually creates the schemaless changeset. To do that
it uses two private functions that operate on the passed filters array: ``make_filter_keys``
to extract the ``:name`` field of each key filter and the ``make_filter_types`` to generate a
``Map`` of ``%{name: :type}`` as needed by the ``types`` of the ``{data, types}`` tuple passed 
to ``cast`` (the ``data`` is just an empty ``Map``):

.. code-block:: elixir

  defp make_filter_keys(filters) do
    filters |> Enum.map(& &1.name)
  end

  defp make_filter_types(filters) do
    filters |> Enum.map(&{&1.name, &1.type}) |> Map.new()
  end

  def make_filter_changeset(filters, params) do
    data = %{}
    types = filters |> make_filter_types

    {data, types}
    |> Ecto.Changeset.cast(params, filters |> make_filter_keys) 
    |> Map.merge(%{action: :insert})
  end

One interesting thing here is the ``Map.merge(%{action: :insert})`` that is piped to the 
generated changeset. This is needed to actually display the validation errors, if there's
no action to the changeset (and there won't be since we aren't going do any updates to the database
with this changeset) then the casting errors won't be displayed.

Please notice that although I use the ``get_changeset_from_params`` in my controller the important
function here is the ``make_filter_changeset``. The ``get_changeset_from_params`` is mainly used to
retrieve the filter-related GET query parameter; however to use ``QueryFilterEx`` you can just 
create (however you want) a ``Map`` of ``filter_name: value`` pairs  and pass it to 
``make_filter_changeset`` to get the changeset.

``QueryFilterEx.filter``
========================

The ``filter`` method gets three parameters. The ``query``, the ``changeset`` (that was created with 
``make_filter_changeset``) and the declared ``filters``. This function will then check all declared ``filters``
one by one and see if the ``changeset`` contains a change for this filter (i.e if the field has a value).
If yes it will append a `where/3`_ to the query based on the passed value of the ``changeset`` and the 
declared filter ``:method``.

To do that it just uses ``Enum.reduce`` starting with the initial query as an accumulator and
reducing on all the declared ``filters``: 

.. code-block:: elixir

  def filter(query, changeset, filters) do
    changes = Map.fetch!(changeset, :changes) 
    filters |> Enum.reduce(query, creat_where_clauses_reducer(changes))
  end

  defp creat_where_clauses_reducer(changes) do
    fn %{name: name, field_name: field_name, binding: binding, method: method}, acc ->
      case Map.fetch(changes, name) do
        {:ok, value} ->
          acc |> creat_where_clause(field_name, binding,  method, value)

        _ ->
          acc
      end
    end
  end

Notice that the ``creat_where_clauses_reducer`` function returns a function (the reducer) that
``reduce`` will use. This function checks to see if the current changes of the ``changeset`` contain
the ``filter_name:``. If yes it will pass the following values to the ``creat_where_clause`` function:

* The accumulated query (``acc``)
* The ``field_name:``, ``:binding`` and ``:method`` values of the current filter
* The value of the changes of the ``changeset``

If the current ``filter_name`` is not contained in the changes then it just returns the accumulated query as it is.

Let's now take a look at the ``creat_where_clause`` function:

.. code-block:: elixir  

  defp creat_where_clause(acc, field_name, binding,  method, value) do
    case method do
      :eq -> acc |> where(
        [{^binding, t}],
        field(t, ^field_name) == ^value
      )
      :ilike -> acc |> where(
        [{^binding, t}],
        ilike(field(t, ^field_name), ^("#{value}%") )
      ) 
      :icontains -> acc |> where(
        [{^binding, t}],
        ilike(field(t, ^field_name), ^("%#{value}%") )
      ) 
      :year -> acc  |> where(
        [{^binding, t}],
        fragment("extract (year from ?) = ?", field(t, ^field_name), ^value)
      )
      :date -> acc  |> where(
        [{^binding, t}],
        fragment("? >= cast(? as date) and ? < (cast(? as date) + '1 day'::interval"), field(t, ^field_name), ^value, field(t, ^field_name), ^value)
      ) 
      _ -> acc |> where(
        [{^binding, t}],
        field(t, ^field_name) == ^value
      )
      
    end
  end

This function is just a simple ``case`` that pipes the accumulated query to a different ``where`` clause
depending on the ``method:``. Let's take a closer look at what happens when ``:method == :eq``:

.. code-block:: elixir  

  acc |> where(
    [{^binding, t}],
    field(t, ^field_name) == ^value
  )

This may seem a little confusing so let's take a look at a simple ``where`` first: 

.. code-block:: elixir  

  from(u in User) |> where([u], u.name == "root") |> Repo.all()

Nothing fancy here, now let's add a named query:

.. code-block:: elixir

  from(u in User, as: :user) |> where([user: u], u.name == "root") |> Repo.all()

Notice that now we can declare that ``u`` is an alias for the ``users`` named binding. What if
we used the tuples syntax for the ``user: u`` instead of the keyword one:

.. code-block:: elixir

  from(u in User, as: :user) |> where([{:user, u}], u.name == "root") |> Repo.all()

Yes this still works. What if we wanted to use a variable for the binding name in the where?  

.. code-block:: elixir

  binding = :user
  from(u in User, as: :user) |> where([{^binding, u}], u.name == "root") |> Repo.all()

I think it starts to make sense now, let's finally use a variable for the field name also:

.. code-block:: elixir

  binding = :user
  field_name = :name
  from(u in User, as: :user) |> where([{^binding, u}], field(u, ^field_name) == "root") |> Repo.all()

So this is exactly how this works!

Beyond the ``:eq`` I've got the definitions for the other methods I described there, the most 
complex one is probably the ``:date`` which is something like: 

.. code-block:: elixir

  where(
    [{^binding, t}],
    fragment("? >= cast(? as date) and ? < (cast(? as date) + '1 day'::interval"), field(t, ^field_name), ^value, field(t, ^field_name), ^value)
  ) 

What this does is that it generates the following SQL fragment:

.. code-block:: sql 

  field_name >= cast(value as date) AND field_name < (cast(value as date) + '1 day'::interval)

You can add your own methods by adding more clauses to the case of the ``creat_where_clause`` function 
and following a similar pattern.

Conclusion
----------

By using the ``QueryFilterEx`` module presented here you can very quickly declare the fields you want
to filter on and the method you want to use for each field no matter if these fields are in the same
schema or are accessed through joins. You can easily extend the functionality of the module by adding
your own methods. The only extra thing you need to do is to just add names to your queries.


.. _journey: https://spapas.github.io/2019/06/04/phoenix-form-select2-ajax/
.. _`favorite Django features`: https://spapas.github.io/2017/10/11/essential-django-packages/
.. _django-filter: https://github.com/carltongibson/django-filter/:
.. _`Elixir forum`: https://elixirforum.com/
.. _`create dynamic bindings`: https://elixirforum.com/t/create-dynamic-bindings-for-where-clause/23797/7
.. _`schemaless one`: https://hexdocs.pm/ecto/Ecto.Changeset.html#module-schemaless-changesets
.. _`where/3`: https://hexdocs.pm/ecto/Ecto.Query.html#where/3
.. _`cast/4`: https://hexdocs.pm/ecto/Ecto.Changeset.html#cast/4