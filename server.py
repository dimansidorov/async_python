import argparse
import configparser
import logging
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from commons.decorators import log
from commons.variables import DEFAULT_PORT
from server.core import MessageProcessor
from server.database import ServerStorage
from server.main_window import MainWindow

logger = logging.getLogger('server')


@log
def parse_args(default_port, default_address):
    """
    Command Line Argument Parser
    :param default_port:
    :param default_address:
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    return listen_address, listen_port, gui_flag


@log
def config_load():
    """
    Configuration ini file parser
    :return:
    """
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


def main():
    """
    Main function
    :return:
    """
    config = config_load()
    listen_address, listen_port, gui_flag = parse_args(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    if gui_flag:
        while True:
            command = input('Enter "exit: or "q" to shut down the server.')
            if command in ('exit', 'q'):
                server.running = False
                server.join()
                break

    else:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)
        server_app.exec_()
        server.running = False


if __name__ == '__main__':
    main()
