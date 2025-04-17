from pymysql import connect

try:
    from ....init.resolver import __resolver
except ImportError:
    from lib.init.resolver import __resolver
    
MYSQL = __resolver("mysql")
HOST = __resolver("mysql", "host")
PORT = __resolver("mysql", "port")
DB = __resolver("mysql", "db")

USER = MYSQL['user']
PASSWORD = MYSQL['password']


class Connector:

    def __init__(self, database=DB):
        self.__conn = connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=database,
            autocommit=True
        )
        self.__cursor = self.__conn.cursor()

    def __call__(self, *args, **kwargs):
        return "Hello World!"

    def getconn(self):
        return self.__conn

    def getcursor(self):
        return self.__cursor

    def close(self):
        self.__conn.close()
        self.__cursor.close()
