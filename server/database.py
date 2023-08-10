import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base

BASE = declarative_base()


class ServerStorage:
    """
    Wrapper class for working with the server database.
    Uses SQLite database, implemented with
    SQLAlchemy ORM and uses a declarative approach.
    """
    class AllUsers(BASE):
        """
        All users table
        """
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        last_login = Column(TIMESTAMP)
        passwd_hash = Column(String)
        pubkey = Column(Text)

        def __init__(self, username, passwd_hash):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None
            self.id = None

    class ActiveUsers(BASE):
        """
        Active users table
        """
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        ip_address = Column(String)
        port = Column(Integer)
        last_login = Column(TIMESTAMP)

        def __init__(self, user_id, ip_address, port, last_login):
            self.id = None
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.last_login = last_login

    class LoginHistory(BASE):
        """
        Login history table
        """
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        date_time = Column(TIMESTAMP)
        ip = Column(String)
        port = Column(Integer)

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    class UsersContacts(BASE):
        """
        Users contacts table
        """

        __tablename__ = 'users_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        contact = Column(ForeignKey('users.id'))

        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UsersHistory(BASE):
        """
        Users history table
        """
        __tablename__ = 'users_history'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        self.base = BASE
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})
        self.base.metadata.create_all(self.database_engine)
        session = sessionmaker(bind=self.database_engine)
        self.session = session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port, key=""):
        """
        The method executed when the user logs in records the fact of logging in to the database
        Updates the user's public key when it changes.
        :param username:
        :param ip_address:
        :param port:
        :param key:
        :return:
        """
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        else:
            raise ValueError('The user is not registered.')

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        self.session.commit()

    def add_user(self, name, passwd_hash):
        """
        User registration method.
        Accepts the name and password hash, creates an entry in the statistics table.
        :param name:
        :param passwd_hash:
        :return:
        """
        user_row = self.AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        """
        The method that removes the user from the database.
        :param name:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(
            self.UsersContacts).filter_by(
            contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        """
        The method of obtaining the hash of the user's password.
        :param name:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        """
        The method of obtaining the hash of the user's pubkey.
        :param name:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        """
        A method that verifies the existence of a user
        :param name:
        :return:
        """
        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, username):
        """
        A method that fixes user disconnections
        :param username:
        :return:
        """
        user = self.session.query(
            self.AllUsers).filter_by(
            name=username).first()

        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        self.session.commit()

    def process_message(self, sender, recipient):
        """
        A method that records the fact of message transmission in the statistics table
        :param sender:
        :param recipient:
        :return:
        """
        sender = self.session.query(
            self.AllUsers).filter_by(
            name=sender).first().id
        recipient = self.session.query(
            self.AllUsers).filter_by(
            name=recipient).first().id
        sender_row = self.session.query(
            self.UsersHistory).filter_by(
            user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(
            self.UsersHistory).filter_by(
            user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def add_contact(self, user, contact):
        """
        Method of adding a contact for the user
        :param user:
        :param contact:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(
            self.AllUsers).filter_by(
            name=contact).first()

        if not contact or self.session.query(
                self.UsersContacts).filter_by(
                user=user.id,
                contact=contact.id).count():
            return

        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        """
        Method of deleting a user's contact
        :param user:
        :param contact:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(
            self.AllUsers).filter_by(
            name=contact).first()

        if not contact:
            return

        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    def users_list(self):
        """
        A method that returns a list of known users with the time of the last login
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        """
        Method that returns a list of active users
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        """
        Method that returns the history of inputs
        :param username:
        :return:
        """
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def get_contacts(self, username):
        """
        Method that returns the user's contact list
        :param username:
        :return:
        """
        user = self.session.query(self.AllUsers).filter_by(name=username).one()

        query = (self.session.query(
            self.UsersContacts, self.AllUsers.name
        ).filter_by(user=user.id).join(
            self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)
        )

        return [contact[1] for contact in query.all()]

    def message_history(self):
        """
        A method that returns message statistics.
        :return:
        """
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage('../server_database.db3')
    test_db.user_login('test1', '192.168.1.113', 8080)
    test_db.user_login('test2', '192.168.1.113', 8081)
    print(test_db.users_list())
    # print(test_db.active_users_list())
    # test_db.user_logout('McG')
    # print(test_db.login_history('re'))
    # test_db.add_contact('test2', 'test1')
    # test_db.add_contact('test1', 'test3')
    # test_db.add_contact('test1', 'test6')
    # test_db.remove_contact('test1', 'test3')
    test_db.process_message('test1', 'test2')
    print(test_db.message_history())
