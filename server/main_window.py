from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QTableView

from server.add_user import RegisterUser
from server.config_window import ConfigWindow
from server.remove_user import DelUserDialog
from server.stat_window import StatWindow


class MainWindow(QMainWindow):
    """
    Class - the main server window
    """
    def __init__(self, database, server, config):
        super().__init__()

        self.database = database

        self.server_thread = server
        self.config = config
        self.exitAction = QAction('Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Update the list', self)

        self.config_btn = QAction('Server settings', self)

        self.register_btn = QAction('User Registration', self)

        self.remove_btn = QAction('Deleting a user', self)

        self.show_history_button = QAction('Customer history', self)

        self.statusBar()
        self.statusBar().showMessage('Server Working')

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.register_btn)
        self.toolbar.addAction(self.remove_btn)

        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server alpha release')

        self.label = QLabel('List of connected clients:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        self.timer = QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)

        self.refresh_button.triggered.connect(self.create_users_model)
        self.show_history_button.triggered.connect(self.show_statistics)
        self.config_btn.triggered.connect(self.server_config)
        self.register_btn.triggered.connect(self.reg_user)
        self.remove_btn.triggered.connect(self.rem_user)

        self.show()

    def create_users_model(self):
        """
        Method that fills in the table of active users
        :return:
        """
        list_users = self.database.active_users_list()
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(
            ['Username', 'IP-address', 'Port', 'Connection time'])
        for row in list_users:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            list.appendRow([user, ip, port, time])
        self.active_clients_table.setModel(list)
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()

    def show_statistics(self):
        """
        A method that creates a window with customer statistics
        :return:
        """
        global stat_window
        stat_window = StatWindow(self.database)
        stat_window.show()

    def server_config(self):
        """
        A method that creates a window with server settings.
        :return:
        """
        global config_window
        config_window = ConfigWindow(self.config)

    def reg_user(self):
        """
        A method that creates a user registration window
        :return:
        """
        global reg_window
        reg_window = RegisterUser(self.database, self.server_thread)
        reg_window.show()

    def rem_user(self):
        """
        A method that creates a user deletion window
        :return:
        """
        global rem_window
        rem_window = DelUserDialog(self.database, self.server_thread)
        rem_window.show()
