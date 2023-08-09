import binascii
import hmac
import json
import logging
import os
import socket as s
import threading

import select

from commons.decorators import login_required
from commons.descriptiors import Port
from commons.utils import send_message, get_message
from commons.variables import DESTINATION, ACTION, PRESENCE, USER, TIME, MESSAGE_TEXT, SENDER, MESSAGE, RESPONSE_200, \
    RESPONSE_400, ERROR, EXIT, ACCOUNT_NAME, GET_CONTACTS, RESPONSE_202, LIST_INFO, ADD_CONTACT, REMOVE_CONTACT, \
    USERS_REQUEST, PUBLIC_KEY_REQUEST, DATA, RESPONSE_511, PUBLIC_KEY, RESPONSE, RESPONSE_205

logger = logging.getLogger('server')


class MessageProcessor(threading.Thread):
    """
    The main class of the server. Accepts connections, dictionaries - packages
    from clients, processes incoming messages.
    Works as a separate thread.
    """
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.sock = None
        self.clients = []
        self.listen_sockets = None
        self.error_sockets = None
        self.running = True
        self.names = {}
        super().__init__()

    def run(self):
        """
        The main flow cycle method
        :return:
        """
        self.init_socket()

        while self.running:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'The connection to the PC is established {client_address}')
                client.settimeout(5)
                self.clients.append(client)
            recv_data_lst = []
            try:
                if self.clients:
                    recv_data_lst, self.listen_sockets, self.error_sockets = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                logger.error(f'Error working with sockets: {err.errno}')

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(
                            get_message(client_with_message), client_with_message)
                    except (OSError, json.JSONDecodeError, TypeError) as err:
                        logger.debug(f'Getting data from client exception.', exc_info=err)
                        self.remove_client(client_with_message)

    def remove_client(self, client):
        """
        The handler method of the client with which the connection was interrupted.
        Searches for a client and removes it from the lists and database
        :param client:
        :return:
        """
        logger.info(f'Client {client.getpeername()} disconnected from the server.')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def init_socket(self):
        """
        Socket Initializer method
        :return:
        """
        transport = s.socket(s.AF_INET, s.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)
        self.sock = transport
        self.sock.listen()

    def process_message(self, message):
        """
        The method of sending the message to the client.
        :param message:
        :return:
        """
        if all([
            message[DESTINATION] in self.names,
            self.names[message[DESTINATION]] in self.listen_sockets
        ]):
            try:
                send_message(self.names[message[DESTINATION]], message)
            except OSError:
                self.remove_client(message[DESTINATION])

        elif all([
            message[DESTINATION] in self.names,
            self.names[message[DESTINATION]] not in self.listen_sockets
        ]):
            logger.error(f'Communication with the client {message[DESTINATION]} was lost.')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            logger.error(f'User {message[DESTINATION]} is not registered on the server.')

    @login_required
    def process_client_message(self, message, client):
        """
        The method is a handler for incoming messages.
        :param message:
        :param client:
        :return:
        """
        if all([
            ACTION in message,
            message[ACTION] == PRESENCE,
            TIME in message,
            USER in message
        ]):
            self.autorise_user(message, client)

        elif all([
            ACTION in message,
            message[ACTION] == MESSAGE,
            DESTINATION in message, TIME in message,
            SENDER in message,
            MESSAGE_TEXT in message,
            self.names[message[SENDER]] == client
        ]):
            if message[DESTINATION] in self.names:
                self.database.process_message(
                    message[SENDER], message[DESTINATION])
                self.process_message(message)
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'The user is not registered on the server.'
                try:
                    send_message(client, response)
                except OSError:
                    pass

        elif all([
            ACTION in message,
            message[ACTION] == EXIT,
            ACCOUNT_NAME in message,
            self.names[message[ACCOUNT_NAME]] == client
        ]):
            self.remove_client(client)

        elif all([
            ACTION in message,
            message[ACTION] == GET_CONTACTS,
            USER in message,
            self.names[message[USER]] == client
        ]):
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

        elif all([
            ACTION in message,
            message[ACTION] == ADD_CONTACT,
            ACCOUNT_NAME in message,
            USER in message,
            self.names[message[USER]] == client
        ]):
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        elif all([
            ACTION in message,
            message[ACTION] == REMOVE_CONTACT,
            ACCOUNT_NAME in message,
            USER in message,
            self.names[message[USER]] == client
        ]):
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        elif all([
            ACTION in message,
            message[ACTION] == USERS_REQUEST,
            ACCOUNT_NAME in message,
            self.names[message[ACCOUNT_NAME]] == client
        ]):
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.database.users_list()]
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

        elif all([
            ACTION in message,
            message[ACTION] == PUBLIC_KEY_REQUEST,
            ACCOUNT_NAME in message
        ]):
            response = RESPONSE_511
            response[DATA] = self.database.get_pubkey(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'There is no public key for this user'
                try:
                    send_message(client, response)
                except OSError:
                    self.remove_client(client)

        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect request'
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

    def autorise_user(self, message, sock):
        """
        A method that implements user authorization
        :param message:
        :param sock:
        :return:
        """
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'The username is already taken.'
            try:
                send_message(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        elif not self.database.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'The user is not registered.'
            try:
                send_message(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            message_auth = RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_str.decode('ascii')
            hash_ = hmac.new(self.database.get_hash(message[USER][ACCOUNT_NAME]), random_str, 'MD5')
            digest = hash_.digest()
            logger.debug(f'Auth message = {message_auth}')
            try:
                send_message(sock, message_auth)
                ans = get_message(sock)
            except OSError as err:
                logger.debug('Error in auth, data:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            if RESPONSE in ans and ans[RESPONSE] == 511 and hmac.compare_digest(
                    digest, client_digest):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_message(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                self.database.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Invalid password.'
                try:
                    send_message(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def service_update_lists(self):
        """
        A method that implements sending a service message to 205 clients.
        :return:
        """
        for client in self.names:
            try:
                send_message(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])
