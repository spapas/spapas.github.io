Phoenix forms integration with select2 and ajax
###############################################

:date: 2019-06-04 14:20
:tags: elixir, phoenix, select2, autocompelte, ajax
:category: elixir
:slug: phoenix-form-select2-ajax
:author: Serafeim Papastefanos
:summary: How to create a proper ajax-autocomplete solution for your foreign key fields with Phoenix Forms and select2

During the past months I've tried to implement a project using `Elixir`_ and the `Phoenix framework`_. Old 
visitors of my blog will probably remember that I mainly use Django for back-end development but I decided to
also give Phoenix a try.

My first impressions are positive but I don't want to go into detail in this post; I'll try to add a more 
extensive post comparing Elixir / Phoenix with Python / Django someday.

The problem that this particular post will try to explain is how to properly integrate a jQuery `select2`_ 
dropdown ajax with autocomplete search to your `Phonix Forms`_. This seems like a very common problem however I
couldn't find a proper solution anywhere in the internet. It seems that most people using Phoenix prefer to 
implement their autocompletes using SPA like functionality (react etc). Also I found `this project`_ that
seems to be working, however it does not use select2 and I really didn't like to mess with a different 
JS library for reasons that should be too obvious to most people.

So here we'll implement a simple solution for allowing your foreign key value to be autocompleted through ajax 
using select2. The specific example is that you have a User that belongs to an Authority i.e user has a field
named `authority_id` which is a foreign key to authority. We'll add a functionality to the user edit form to
select the authority using ajax-autocomplete.

Please notice that you can find a working version of this tutorial in my Phoenix Crud template project: 
https://github.com/spapas/phxcrd. This project contains various other functionality that I need but you should be
able to test the user - authority integration by following the instructions there.

The schemas
-----------

For this tutorial, we'll use two schemas: A ``User`` and an ``Authority``. Each ``User`` belongs to an ``Authority``
(thus will have a foreign key to ``Authority``; that's what we want to set using the ajax select2). Here are 
the ecto schemas for these entities:

.. code-block:: elixir

    defmodule Phxcrd.Auth.Authority do
      use Ecto.Schema

      import Ecto.Changeset
      alias Phxcrd.Auth.User

      schema "authorities" do
        field :name, :string
        has_many :users, User, on_replace: :nilify
        timestamps()
      end

      @doc false
      def changeset(authority, attrs) do
        authority
        |> cast(attrs, [:name])
        |> validate_required([:name], message: "The field is required")
        |> unique_constraint(:name, message: "The name already exists!")
      end

      use Accessible
    end

.. code-block:: elixir

    defmodule Phxcrd.Auth.User do
      use Ecto.Schema

      import Ecto.Changeset
      alias Phxcrd.Auth.Authority

      schema "users" do
        field :email, :string
        field :username, :string
        field :password_hash, :string
        field :password, :string, virtual: true

        belongs_to :authority, Authority

        timestamps()
      end

      @doc false
      def changeset(user, attrs) do
        user
        |> cast(attrs, [:username, :email, :authority_id])
        |> validate_required([:username, :email ])
      end

      use Accessible
    end

Notice that both these entities are contained in the ``Auth`` context and were created using
``mix phx.gen.html``; I won't include the migrations here.
    
The search API
--------------

Let's now take a look at the search api for ``Authority``. I've added an ``ApiController``  which contains
the following function:

.. code-block:: elixir

    def search_authorities(conn, params) do
        q = params["q"]

        authorities =
          from(a in Authority,
            where: ilike(a.name, ^"%#{q}%")
          )
          |> limit(20)
          |> Repo.all()

        render(conn, "authorities.json", authorities: authorities)
    end
    
Notice that this retrieves a `q` parameter and makes an `ilike` query to `Authority.name`. It then
passes the results to the view for rendering. Here's the corresponding function for `ApiView`:

.. code-block:: elixir

    def render("authorities.json", %{authorities: authorities}) do
        %{results: Enum.map(authorities, &authority_json/1)}
      end

      def authority_json(a) do
        %{
          id: a.id,
          text: a.name
        }
    end
    
Notice that select2 wants its results in a JSON struct with the following form ``{results: [{id: 1, name: "Authority 1"}]}``.

To add this controller action to my routes I've added this to ``router.ex``:

.. code-block:: elixir

    scope "/api", PhxcrdWeb do
        pipe_through :api

        get "/search_authorities", ApiController, :search_authorities
    end

Thus if you visit ``http://127.0.0.1/search_authorities?q=A`` you should retrieve authorities containing ``A`` in their name.

The controller
--------------

Concenring the ``UserController`` I've added the following methods to it for creating and updating users:

.. code-block:: elixir

  def new(conn, _params) do
    changeset = Auth.change_user(%User{})
    render(conn, "new.html", changeset: changeset)
  end

  def create(conn, %{"user" => user_params}) do
    case Auth.create_user(user_params) do
      {:ok, user} ->
        conn
        |> put_flash(:info, "#{user.name} created!")
        |> redirect(to: Routes.user_path(conn, :show, user))

      {:error, changeset} ->
        render(conn, "new.html", changeset: changeset)
    end
  end

  def edit(conn, %{"id" => id}) do
    user = Auth.get_user!(id)
    changeset = Auth.change_user(user)
    render(conn, "edit.html", user: user, changeset: changeset)
  end

  def update(conn, %{"id" => id, "user" => user_params}) do
    user = Auth.get_user!(id)

    user_params = Map.merge(%{"authority_id" => nil}, user_params)

    case Auth.update_user(user, user_params) do
      {:ok, user} ->
        conn
        |> put_flash(:info, "User updated successfully.")
        |> redirect(to: Routes.user_path(conn, :show, user))

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "edit.html", user: user, changeset: changeset)
    end
  end

Most of these are more or less the default things that ``mix phx.gen.html`` creates. 
One thing that may seem a strange here is the ``user_params = Map.merge(%{"authority_id" => nil}, user_params)``
line of ``update``. What happens here is that I want to be able to clear the authority of a user (I'll
explain how in the next sections). If I do
that then the ``user_params`` that is passed to ``update`` will *not* contain an ``authority_id`` key thus 
the ``authority_id`` won't be changed at all (so even though I cleared it, it will keep its previous value after
I save it). To fix that I set a default value of ``nil`` to ``authority_id``; if the user has actually selected
an authority from the form this will be overriden when merging the two maps. So the resulting ``user_params`` will
*always* contain an ``authority_id`` key, either set to nil or to the selected authority.

Beyond that I wont' go into detail explaining the above functions,  but if something seems strange feel free to ask. I
also won't explain the ``Auth.*`` functions; all these are created by phoenix in the context module.

The view
--------

The ``UserView`` module contains a simple but very important function:

.. code-block:: elixir

  def get_select_value(changeset, attr) do
    case changeset.changes[attr] do
      nil -> Map.get(changeset.data, attr)
      z -> z
    end
  end

This functions gets two parameters: The changeset and the name of the attribute (``:authority_id`` in our case). What
it does is to first check if this attribute is contained in the changeset.changes; if yes it will return that value. If
it isn't contained in the changeset.changes then it will return the value of changeset.data for that attribute.

This is a little complex but let's try to understand its logic: When you start editing a ``User`` you want to display 
the current authority of that instance. However, when you submit an edited user and retrieve an errored form (for example
because you forgot to fill the username) you want to display the authority that *was submitted* in the form. So the
``changeset.changes`` contains the changes that were submitted just before while the ``changeset.data`` contain the
initial value of the struct. 

**Update 02/07/2019:** Please notice that instead of using the 
``get_select_value`` I presented before you can use the 
``Ecto.Changeset.get_field`` function that does exactly this! So
``get_select_value`` could be defined like this:

.. code-block:: elixir

  def get_select_value(changeset, attr) do
    changeset |> Ecto.Changeset.get_field(attr)
  end

The form template
-----------------

Both the ``:new`` and ``:edit`` actions include a common form.html.eex template: 

.. code-block:: html

  <%= form_for @changeset, @action, fn f -> %>
    <%= if @changeset.action do %>
    <div class="alert alert-danger">
      <p><%= gettext("Problems while saving") %></p>
    </div>
    <% end %>
    <div class='row'>
      <div class='column'>
        <%= label f, :username %>
        <%= text_input f, :username %>
        <%= error_tag f, :username %>
      </div>
      <div class='column'>
        <%= label f, :email %>
        <%= text_input f, :email %>
        <%= error_tag f, :email %>
      </div>
    </div>

    <div class='row'>
      <div class='column'>
        <%= label f, :authority %>
        <%= select(f,
          :authority_id, [
            (with sv when not is_nil(sv) <- get_select_value(@changeset, :authority_id), 
                                       a <- Phxcrd.Auth.get_authority!(sv), do: {a.name, a.id})
          ],
          style: "width: 100%")
          %>
        <%= error_tag f, :authority_id %>
      </div>

    </div>

    <div>
      <%= submit gettext("Save") %>
    </div>
  <% end %>
  
This is a custom Phoenix form but it has the following addition which is more or less the meat of this article
(along with the ``get_select_value`` function I explained before):

.. code-block:: elixir

    select(f, :authority_id, [
            (with sv when not is_nil(sv) <- get_select_value(@changeset, :authority_id), 
                                       a <- Phxcrd.Auth.get_authority!(sv), do: {a.name, a.id})
          ],
          style: "width: 100%")
          
So this will create an html select element which will contain a single value (the array in the third
parameter of ``select``): The authority of that object or the authority that the user had submitted
in the form. For this it uses ``get_select_value`` to retrieve the :authority_id and if it's not nil
it passes it to ``get_authority!`` to retrieve the actual authority and return a tuple with its name and id.

By default when you create a ``select`` element you'll pass an array of all options in the third
parameter, for example: 

.. code-block:: elixir

    select(f, :authority_id, Phxcrd.Auth.list_authorities |> Enum.map(&{&1.name, &1.id}))
    
Of course this beats the purpose of using ajax since all options will be rendered.

The final step is to add the required custom javascript to convert that select to select2-with-ajax:

.. code-block:: javascript

    $(function () {
        $('#user_authority_id').select2({
          allowClear: true,
          placeholder: 'Select authority',
          ajax: {
            url: '<%= Routes.api_path(@conn, :search_authorities) %>',
            dataType: 'json',
            delay: 150,
            minimumInputLength: 2
          }
        });
    })

The JS very rather simple; the ``allowClear`` option will display an ``x`` so that you can clear the
selected authority while the ajax url will be that of the ``:search_authorities``. 

Conclusion
----------

Although this article may seem a little long, as I've already mentioned the most important thing 
to keep is how to properly set the value that should be displayed in your ``select2`` widget. Beyond
that everything is a walk in the park by following the docs.


.. _`Elixir`: https://elixir-lang.org/
.. _`Phoenix framework`: https://phoenixframework.org/
.. _`select2`: https://select2.org/
.. _`Phonix Forms`: https://hexdocs.pm/phoenix_html/Phoenix.HTML.Form.html
.. _`this project`: https://github.com/nico-amsterdam/phoenix_form_awesomplete