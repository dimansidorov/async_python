Launcher module
=================================================

The module runs multiple clients at the same time.

Usage:

After the launch, you will be prompted to enter a command.
Supported commands:

1. s - Run the server

* Starts the server with default settings.

2. k - Launch clients

* A query will be displayed for the number of test clients to run.
* * Clients will be launched with names like **test1 - test** and passwords **123**
* Test users must first be manually registered on the server with a password **123** .
* If clients are being launched for the first time, the startup time may be quite long due to the generation of new RSA keys.

3. x - Close all windows

* * Closes all active windows that were launched from this module.

4. q - Shut down the module

* Shuts down the module
