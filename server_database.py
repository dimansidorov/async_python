from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base

from commons.variables import *
import datetime

BASE = declarative_base()


class ServerStorage:
    class AllUsers(BASE):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        last_login = Column(TIMESTAMP)

        def __init__(self, name):
            self.name = name
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers(BASE):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey('users.id'))
        ip_address = Column(String)
        port = Column(Integer)
        last_login = Column(TIMESTAMP)

        def __init__(self, user_id, ip_address, port, last_login):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.last_login = last_login
            self.id = None

    class LoginHistory(BASE):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        users_id = Column(ForeignKey('users.id'))
        date_time = Column(TIMESTAMP)
        ip = Column(String)
        port = Column(Integer)

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    def __init__(self):
        self.base = BASE
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
        self.base.metadata.create_all(self.database_engine)
        session = sessionmaker(bind=self.database_engine)
        self.session = session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.last_login
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('client_1', '192.168.1.4', 8888)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    print(test_db.active_users_list())

    test_db.user_logout('client_1')
    print(test_db.active_users_list())

    test_db.login_history('client_1')
    print(test_db.users_list())
