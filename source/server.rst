Server module
=================================================

Messenger server module. Processes message dictionaries, stores clients' public keys.

Usage:

The module supports command line arguments:

1. -p - Port on which connections are accepted
2. -a is the address from which connections are received.
3. --no_gui Launching only basic functions, without a graphical shell.

* Only 1 command is supported in this mode: exit - shutdown.

Usage examples:

``python server.py -p 8080``

*Starting the server on port 8080*

``python server.py -a localhost``

*Starting a server accepting only connections with localhost*

``python server.py --no-gui``

*Launch without a graphical shell*

server.py
~~~~~~~~~

The module being launched contains a command-line argument parser and application initialization functionality.

server. **parse_args** ()
    Command line argument parser, returns a tuple of 3 elements:

	* the address from which to accept connections
	* port
    * GUI startup flag

server. **config_load** ()
    The function of loading configuration parameters from the ini file.
    If there is no file, the default parameters are set.

core.py
~~~~~~~~~~~

.. autoclass:: server.core.MessageProcessor
	:members:

database.py
~~~~~~~~~~~

.. autoclass:: server.database.ServerStorage
	:members:

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: server.main_window.MainWindow
	:members:

add_user.py
~~~~~~~~~~~

.. autoclass:: server.add_user.RegisterUser
	:members:

remove_user.py
~~~~~~~~~~~~~~

.. autoclass:: server.remove_user.DelUserDialog
	:members:

config_window.py
~~~~~~~~~~~~~~~~

.. autoclass:: server.config_window.ConfigWindow
	:members:

stat_window.py
~~~~~~~~~~~~~~~~

.. autoclass:: server.stat_window.StatWindow
	:members: