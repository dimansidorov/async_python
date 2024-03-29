from PyQt5.QtWidgets import QDialog, QPushButton, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


class StatWindow(QDialog):
    """
    Class - a window with user statistics
    """
    def __init__(self, database):
        super().__init__()

        self.database = database
        self.initUI()

    def initUI(self):
        """
        A method that initialize a UI
        :return:
        """
        self.setWindowTitle('Customer statistics')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.stat_table = QTableView(self)
        self.stat_table.move(10, 10)
        self.stat_table.setFixedSize(580, 620)

        self.create_stat_model()

    def create_stat_model(self):
        """
        A method that implements filling the table with message statistics.
        :return:
        """
        stat_list = self.database.message_history()

        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(
            ['Username', 'Last login', 'Messages sent', 'Messages received'])
        for row in stat_list:
            user, last_seen, sent, recvd = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            recvd = QStandardItem(str(recvd))
            recvd.setEditable(False)
            list.appendRow([user, last_seen, sent, recvd])
        self.stat_table.setModel(list)
        self.stat_table.resizeColumnsToContents()
        self.stat_table.resizeRowsToContents()
