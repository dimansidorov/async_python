from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, Qt
import logging

from client.main_window_conv import Ui_MainClientWindow
from client.add_contact import AddContactDialog
from client.del_contact import DelContactDialog
from commons.errors import ServerError

logger = logging.getLogger('client')


class ClientMainWindow(QMainWindow):
    """The class is the main user window.
    Contains all the basic logic of the client module.
    The window configuration is created in QT Designer and loaded from
    the converted file main_window_conv.py
    """

    def __init__(self, database, transport):
        super().__init__()
        self.database = database
        self.transport = transport

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        self.ui.menu_exit.triggered.connect(qApp.exit)

        self.ui.btn_send.clicked.connect(self.send_message)

        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        """A method that makes input fields inactive"""
        self.ui.label_new_message.setText('To select a recipient, double-click on it in the contacts window.')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

    def history_list_update(self):
        """A method that updates a history list"""
        lst = sorted(self.database.get_history(self.current_chat), key=lambda x: x[3])
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        self.history_model.clear()
        length = len(lst)
        start_index = 0
        if length > 20:
            start_index = length - 20
        for i in range(start_index, length):
            item = list[i]
            if item[1] == 'in':
                mess = QStandardItem(f'Incoming from {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Coming from {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.list_messages.scrollToBottom()

    def select_active_user(self):
        """Method handler for the double click event on the contact list"""
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        """The method of activating the chat with the interlocutor"""
        self.ui.label_new_message.setText(f'Enter the message for {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        self.history_list_update()

    def clients_list_update(self):
        """Method that updates the contact list"""
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        """The method that creates the window is the dialog for adding a contact"""
        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        """
        The handler method for clicking the "Add" button
        :param item:
        :return:
        """
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        """
        A method that adds a contact to the server and client BD.
        After updating the databases, it also updates the contents of the window.
        :param new_contact:
        :return:
        """
        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Server error!', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error!', 'Connection to the server is lost!')
                self.close()
            self.messages.critical(self, 'Error!', 'Connection timeout!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Successfully added contact {new_contact}')
            self.messages.information(self, 'Success', 'Successfully added contact.')

    def delete_contact_window(self):
        """Method that creates a window for deleting a contact"""
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        """
        A method that removes a contact from the server and client BD.
        After updating the databases, it also updates the contents of the window.
        :param item:
        :return:
        """
        selected = item.selector.currentText()
        try:
            self.transport.remove_contact(selected)
        except ServerError as err:
            self.messages.critical(self, 'Server error!', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error!', 'Connection to the server is lost!')
                self.close()
            self.messages.critical(self, 'Error!', 'Connection timeout!')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            logger.info(f'Successfully deleted contact {selected}')
            self.messages.information(self, 'Success', 'Successfully deleted contact.')
            item.close()
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        """
        The function of sending a message to the current interlocutor.
        Implements message encryption and sending.
        """
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        try:
            self.transport.send_message(self.current_chat, message_text)
            pass
        except ServerError as err:
            self.messages.critical(self, 'Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Connection to the server is lost!')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Error', 'Connection to the server is lost!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            logger.debug(f'A message has been sent for {self.current_chat}: {message_text}')
            self.history_list_update()

    @pyqtSlot(str)
    def message(self, sender):
        """
        Slot handler of incoming messages, performs decryption
        incoming messages and their saving in the message history.
        Requests the user if the message is not from the current one
        the interlocutor. If necessary, changes the interlocutor.
        :param sender:
        :return:
        """
        if sender == self.current_chat:
            self.history_list_update()
        else:
            if self.database.check_contact(sender):
                if self.messages.question(
                        self,
                        'New message',
                        f'Received a new message from {sender}, open a chat with him?',
                        QMessageBox.Yes,
                        QMessageBox.No
                ) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                if self.messages.question(
                        self,
                        'New message',
                        f'A new message has been received from {sender}.\n This user is not in your contact list.\n Add to contacts and open a chat with him?',
                        QMessageBox.Yes,
                        QMessageBox.No
                ) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        """
        Slot handler for loss of connection to the server.
        Issues a warning window and shuts down the application.
        """
        self.messages.warning(self, 'Connection failure', 'Connection to the server is lost!')
        self.close()

    def make_connection(self, trans_obj):
        """
        A method for connecting signals and slots
        :param trans_obj:
        :return:
        """
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)
