import argparse
import os
import sys
import logging

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

from client.database import ClientDatabase
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog
from client.transport import ClientTransport
from commons.decorators import log
from commons.errors import ServerError
from commons.utils import check_port
from commons.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT

LOGGER = logging.getLogger('client')


@log
def parse_args():
    """
    Command line argument parser, returns a tuple of 4 elements
    server address, port, username, password.
    Performs a check for the correctness of the port number.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_password = namespace.password

    if not check_port(server_port):
        LOGGER.critical(
            f'Invalid port -  {server_port}.')
        sys.exit(1)

    return server_address, server_port, client_name, client_password


@log
def main():
    """
    Main function
    :return:
    """
    server_address, server_port, client_name, client_passwd = parse_args()
    client_app = QApplication(sys.argv)

    start_dialog = UserNameDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
        else:
            sys.exit(0)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    keys.publickey().export_key()
    database = ClientDatabase(client_name)
    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_passwd,
            keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Server error', error.text)
        sys.exit(1)
    transport.setDaemon(True)
    transport.start()

    del start_dialog

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Chat alpha release - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()


if __name__ == '__main__':
    main()
