Commons package
=================================================

A package of common utilities used in different modules of the project.

Script decorators.py
---------------

.. automodule:: common.decos
	:members:

Script descriptors.py
---------------------

.. autoclass:: common.descryptors.Port
    :members:

Script errors.py
---------------------

.. autoclass:: common.errors.ServerError
   :members:

Script metaclasses.py
-----------------------

.. autoclass:: common.metaclasses.ServerVerifier
   :members:

.. autoclass:: common.metaclasses.ClientVerifier
   :members:

Script utils.py
---------------------

common.utils. **get_message** (client)


	The function of receiving messages from remote computers. Accepts JSON messages,
    decodes the received message and verifies that a dictionary has been received.

common.utils. **send_message** (sock, message)


	The function of sending dictionaries via socket. Encodes the dictionary in JSON format and sends it via socket.


Script variables.py
---------------------

Contains global project variables.