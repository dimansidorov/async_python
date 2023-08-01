import logging
import logs.config_client_logs
import argparse
import sys
from PyQt5.QtWidgets import QApplication

from commons.variables import *
from commons.errors import ServerError
from commons.decorators import log
from commons.utils import check_port
from client.database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

LOGGER = logging.getLogger('client')


@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not check_port(server_port):
        LOGGER.critical(
            f'Invalid port -  {server_port}.')
        sys.exit(1)

    return server_address, server_port, client_mode


if __name__ == '__main__':
    server_address, server_port, client_name = parse_args()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    LOGGER.info(
        f'The client is running with the following parameters: server address: {server_address} , port: {server_port}, user name: {client_name}')

    database = ClientDatabase(client_name)

    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Chat alpha release - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()
