import binascii
import hashlib
import hmac
import json
import socket as s
import time
import logging
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from commons.errors import ServerError
from commons.utils import send_message, get_message
from commons.variables import ACTION, PRESENCE, USER, TIME, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE_TEXT, MESSAGE, \
    SENDER, DESTINATION, GET_CONTACTS, LIST_INFO, USERS_REQUEST, ADD_CONTACT, REMOVE_CONTACT, EXIT, RESPONSE_511, DATA, \
    PUBLIC_KEY

logger = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    """
    A class that implements the transport subsystem of the client
    module. Responsible for interacting with the server.
    """
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username, passwd, keys):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.password = passwd
        self.transport = None
        self.keys = keys
        self.connection_init(port, ip_address)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Connection to the server is lost.')
                raise ServerError('Connection to the server is lost!')
            logger.error('Connection timeout when updating user lists.')
        except json.JSONDecodeError:
            logger.critical(f'Connection to the server is lost.')
            raise ServerError('Connection to the server is lost!')
        self.running = True

    def connection_init(self, port, ip):
        """
        The method responsible for establishing a connection to the server.
        :param port:
        :param ip:
        :return:
        """
        self.transport = s.socket(s.AF_INET, s.SOCK_STREAM)

        self.transport.settimeout(5)

        connected = False
        for i in range(5):
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            logger.critical('Connection to the server is lost!')
            raise ServerError('Connection to the server is lost!')

        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        pubkey = self.keys.publickey().export_key().decode('ascii')

        with socket_lock:
            presense = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: pubkey
                }
            }
            try:
                send_message(self.transport, presense)
                ans = get_message(self.transport)
                if RESPONSE in ans:
                    if ans[RESPONSE] == 400:
                        raise ServerError(ans[ERROR])
                    elif ans[RESPONSE] == 511:
                        ans_data = ans[DATA]
                        hash_ = hmac.new(
                            passwd_hash_string, ans_data.encode('utf-8'))
                        digest = hash_.digest()
                        my_ans = RESPONSE_511
                        my_ans[DATA] = binascii.b2a_base64(
                            digest).decode('ascii')
                        send_message(self.transport, my_ans)
                        self.process_server_ans(get_message(self.transport))
            except (OSError, json.JSONDecodeError):
                raise ServerError('Connection to the server is lost!')

    def create_presence(self):
        """
        The method is a handler for incoming messages from the server
        :return:
        """
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        logger.debug(f'A {PRESENCE} message has been generated for the user {self.username}')
        return out

    def process_server_ans(self, message):
        """
        The method is a handler for incoming messages from the server
        :param message:
        :return:
        """
        logger.debug(f'Parsing a message from the server: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                logger.debug(f'Unknown confirmation code received {message[RESPONSE]}')

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        """A method that updates the contact list from the server"""
        logger.debug(f'Request a contact sheet for the user {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            logger.error('The contact list could not be updated.')

    def user_list_update(self):
        """
        A method that updates the list of users from the server
        :return:
        """
        logger.debug(f'Requesting a list of known users {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            logger.error('Failed to update the list of known users.')

    def add_contact(self, contact):
        """
        A method that sends information about adding a contact to the server
        :param contact:
        :return:
        """
        logger.debug(f'Creating a contact {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def remove_contact(self, contact):
        logger.debug(f'Deleting a contact {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def transport_shutdown(self):
        """
        A method that sends information about deleting a contact to the server.
        :return:
        """
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        time.sleep(0.5)

    def send_message(self, to, message):
        """
        A method that sends messages to the server for the user
        :param to:
        :param message:
        :return:
        """
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }

        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            logger.info(f'A message has been sent to the user {to}')

    def run(self):
        """
        A method containing the main cycle of the transport flow.
        :return:
        """
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Connection to the server is lost.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'Connection to the server is lost.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)
