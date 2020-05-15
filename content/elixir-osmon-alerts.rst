Getting alerts from OS Mon in your Elixir application
#####################################################

:date: 2020-05-15 14:20
:tags: elixir, osmon, phoenix, erlang, os-monitoring
:category: elixir
:slug: elixir-osmon-alerts
:author: Serafeim Papastefanos
:summary: How to receive alerts from the Erlang osmon (OS Monitoring) application in your elixir/phoenix application

When I upgraded my `Phoenix template application`_ to Phoenix 1.5.1 I also enabled the new 
`Phoenix LiveDashboard`_ and its "OS Data" tab. To enable that OS Data tab you have to
enable the ``:os_mon`` erlang application by adding it (along with ``:logger`` and ``:runtime_tools``) to
your ``extra_applications`` setting `as described here`_.

When I enabled the ``os_mon`` application I immediately saw a warning in my logs that one of disks is almost full (which is 
a fact). I knew that I wanted to understand how these warniings are generated and if I could handle them with
some custom code to send an email for example.

This journey lead me to an interesting erlang rabit hole which I'll describe in this small post.

The os_mon erlang application
-----------------------------

os_mon_ is an erlang application that, when started will run 4 processes for monitoring
CPU load, disk, memory and some OS settings. These don't work for all operating systems
but memory and disk which are the most interesting to me do work on both unix and Windows.

The disk and memory monitoring processes are called ``memsup`` and ``disksup`` and run a periodic
configurable check that checks if the  memory or disk space usage is above a (configurable)
threshold. If the usage is over the threashold then an error will be reported to the 
`SASL alarm handler`_ (SASL is erlang's System Architecture Support Libraries). 

The alarm handler situation
---------------------------

The SASL alarm handler is a process that implements the gen_event_ behavior. It must
be noted that this behavior is `rather controversial`_ and should not be used
for your own event handling (you can use your own gen server solution or gen stage).
A ``gen_event`` process is an event manager. This event manager keeps a list of 
event handlers; when an event happens the event manager will notify each of the
event handlers. Each event handler is just a module so when an event occurs all
event handlers will be run in the same process one after the other (that's the 
actual reason of why gen_event is not very loved).

The SASL alarm handler (the gen_event event manager) 
is implemented in a module named ``:alarm_handler``. A rather
unfortunate decision is that the default simple alarm handler 
(the gen_event eevent handler) is *also* implemented
in the same module so in the following you'll see ``:alarm_handler`` twice!

The default simple alarm handler can be exchanged with your own custom implementation or 
you can even add additional alarm handlers so they'll be called one after the other. 

To add another custom event handler for alarms, you'll use the add_handler_ method of gen_event. To change it 
with your own, you'll use the swap_handler_ of gen_event. When the default simple alarm handler
is swapped it will return a list of the existing alarms in the system which will the be passed to
the new alarm handler. 


A simple alarm handler implementation
-------------------------------------

As noted in the docs, an alarm handler implementation must handle the following two events:

``{:set_alarm, {alarm_id, alarm_description}}`` and 
``{:clear_alarm, alarm_id}``. The first one will be called from the event manager when a new alarm 
is created and the send one when the cause of the alarm not longer exists.

Let's see a simple implementation of an alarm event handler:

.. code-block:: elixir

    defmodule Phxcrd.AlarmHandler do
    import Bamboo.Email
    require Logger

    def init({_args, {:alarm_handler, alarms}}) do
      Logger.debug  "Custom alarm handler init!"
      for {alarm_id, alarm_description} <- alarms, do: handle_alarm(alarm_id, alarm_description)
      {:ok, []}
    end

    def handle_event({:set_alarm, {alarm_id, alarm_description}}, state) do
      Logger.warn  "Got an alarm " <> Atom.to_string(alarm_id) <> " " <> alarm_description
      handle_alarm(alarm_id, alarm_description)
      {:ok, state}
    end

    def handle_event({:clear_alarm, alarm_id}, state) do
      Logger.debug  "Clearing the alarm  " <>  Atom.to_string(alarm_id)
      state |> IO.inspect
      {:ok, state}
    end

    def handle_alarm(alarm_id, alarm_description) do
      Logger.debug  "Handling alarm " <>  Atom.to_string(alarm_id)

      new_email(
        to: "foo@foo.com",
        from: "bar@bar.gr",
        subject: "New alarm!",
        html_body: "<strong>Alert:"  <>  Atom.to_string(alarm_id) <> " " <> alarm_description <>  "</strong>",
        text_body: "Alert:" <>  Atom.to_string(alarm_id) <> " " <> alarm_description
      )
      |> Phxcrd.Mailer.deliver_later()

      Logger.debug  "End handling alarm " <> Atom.to_string(alarm_id)
    end

  end

This implementation also has an ``init`` function that is called when the handler
is first started. Notice that it receives a list of the existing alarms; for each
one of them I'll calle the handle_alarm function. This is needed to handle any
existing alarms when the application is starting. The ``:set_alarm`` handler also
calls ``handle_alarm`` passing the ``alarm_id`` and ``alarm_description`` it received.

The ``clear_alarm`` doesn't do anything (it would be useful if this module used state to
keep a list of the current alarms). Finally, the ``handle_alarm`` will just send an
email using bamboo_smtp_. Notice that I use deliver_later() to send the mail asynchronously.

As you can see this is a very simple example. You can do more things here but I think that
getting the Alarm email should be enough for most situations!

Integrating the alarm handler into your elixir app 
--------------------------------------------------

To use the above mentioned custom alarm event handler I've added the following line to
the start of my  ``Application.start`` function:

.. code-block:: elixir

    :gen_event.swap_handler(:alarm_handler, {:alarm_handler, :swap}, {Phxcrd.AlarmHandler, :ok})

Please notice that the ``:alarm_handler`` atom is encountered twice: The first is the event manager
module (for which we want to swich the event handler) while the second is the event handler module 
(which is the one we want to replace). 

os_mon configuration
--------------------

The are a number of options you can configure for `os_mon`. You can find them all at the manual page.
For example, just add the following to your ``config.exs``:

.. code-block:: elixir

  config :os_mon,
    disk_space_check_interval: 1,
    memory_check_interval: 5,
    disk_almost_full_threshold: 0.90,
    start_cpu_sup: false

This will set the interval for disk space check to 1 minute, for memory check to 5 minutes, the
disk usage threshold to 90% and will not start the cpu_sup process to get CPU info.

Testing with the terminal
-------------------------

If no alerts are active in your systemm, you can test your custom event handler using something like this
from an ``iex -S mix`` terminal:

.. code-block:: elixir
  
  :alarm_handler.set_alarm({:koko, "ZZZZZZZZZ"}
  # or 
  :alarm_handler.clear_alarm(:koko)

Also you can see some of the current data or configuration options:

.. code-block:: elixir

  iex(4)> :disksup.get_disk_data
  [{'C:\\', 234195964, 55}, {'E:\\', 822396924, 2}]

  # or 
  iex(7)> :disksup.get_check_interval
  60000

Please notice that the check interval is in seconds when you set it, in ms when you retrieve it.

Conclusion
----------

The above should help you if you also want to better understand alert_handler, os_mon and 
how to configure it to run your own custom alert handlers. Of course in a production server
you should have proper monitoring tools for the health of your server but since os_mon is more
or less free thanks to erlang, why not add another safety valve?

If you want to take a look at an application that has everything configured, take a 
look at my `Phoenix template application`_.


.. _`Phoenix template application`: https://github.com/spapas/phxcrd/
.. _`Phoenix LiveDashboard`: https://github.com/phoenixframework/phoenix_live_dashboard
.. _`as described here`: https://hexdocs.pm/phoenix_live_dashboard/os_mon.html#enabling-os_mon
.. _os_mon: http://erlang.org/doc/man/os_mon_app.html
.. _`SASL alarm handler`: http://erlang.org/doc/man/alarm_handler.html
.. _gen_event: http://erlang.org/doc/man/gen_event.html
.. _`rather controversial`: https://pattern-match.com/blog/2018/08/31/what-is-wrong-with-gen-event-an-update/
.. _add_handler: http://erlang.org/doc/man/gen_event.html#add_handler-3
.. _swap_handler: http://erlang.org/doc/man/gen_event.html#swap_handler-3
.. _bamboo_smtp: https://github.com/fewlinesco/bamboo_smtp