Client module documentation
=================================================

A client application for messaging. Supports
sending messages to users who are online, messages are encrypted
using the RSA algorithm with a key length of 2048 bits.

Supports command line arguments:

``python client.py {server} {port} -n or --name {username} -p or -password {password}``

1. {server} is the address of the message server.
2. {port} - the port on which connections are accepted
3. -n or --name - the name of the user with whom the login will occur.
4. -p or --password - the user's password.

All command line options are optional, but the username and password must be used in pairs.

Usage examples:

* ``python client.py``

*Launch the application with default settings.*

* ``python client.py ip_address some_port``

*Launch the application with instructions to connect to the server at ip_address:port*

* ``python -n test1 -p 123``

*Launching the application with user test1 and password 123*

* ``python client.py ip_address some_port -n test1 -p 123``

*Launch the application with user test1 and password 123 and instructions to connect to the server at ip_address:port*
client.py
~~~~~~~~~

The module being launched contains a command-line argument parser and application initialization functionality.
client. **parse_args** ()
    Command line argument parser, returns a tuple of 4 elements:

	* server address
	* port
	* user name
	* password

    Performs a check for the correctness of the port number.


database.py
~~~~~~~~~~~~~~

.. autoclass:: client.database.ClientDatabase
	:members:

transport.py
~~~~~~~~~~~~~~

.. autoclass:: client.transport.ClientTransport
	:members:

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: client.main_window.ClientMainWindow
	:members:

start_dialog.py
~~~~~~~~~~~~~~~

.. autoclass:: client.start_dialog.UserNameDialog
	:members:


add_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.add_contact.AddContactDialog
	:members:


del_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.del_contact.DelContactDialog
	:members: