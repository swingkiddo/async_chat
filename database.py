import psycopg2
from collections import namedtuple


class Database:
    def __init__(
            self,
            host="localhost",
            database="chat",
            user="postgres",
            password="postgres"
    ):

        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.cursor = self.connection.cursor()

    def register_user(self, username, password):
        try:
            self.cursor.execute(
                f"INSERT INTO users (username, password) VALUES ('{username}', '{password}');"
            )
            self.connection.commit()

        except:
            pass

    def validate_user_data(self, username, password):
        try:
            self.cursor.execute(
                f"SELECT * FROM users WHERE username = '{username}'"
            )
            _id, _username, _password = self.cursor.fetchone()
            if _username == username and _password == password:
                return _id
            return False

        except:
            return False

    def create_message(self, username, message):
        self.cursor.execute(
            f"SELECT id FROM users WHERE username = '{username}'"
        )
        _id = self.cursor.fetchone()[0]

        self.cursor.execute(
            f"INSERT INTO messages (sender, body) VALUES ('{_id}', '{message}')"
        )
        self.connection.commit()

    def get_log(self, quantity=10):
        self.cursor.execute(
            f"SELECT u.username, m.body, to_char(m.when_sent, 'HH24:MI') FROM users u, messages m \
            WHERE u.id = m.sender ORDER BY m.body DESC LIMIT {quantity};"
        )
        log = [(sender, body, datetime) for sender, body, datetime in self.cursor.fetchall()]
        return log
