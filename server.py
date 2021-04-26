import socket
import pickle
import asyncio

from settings import HOSTNAME, PORT, MAX_CONNECTIONS
from database import Database
from utils import get_current_time


class ChatServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.socket = self.get_socket()
        self.users = []
        self.messages = "chat.txt"
        self.database = Database()
        self.log = self.database.get_log()
        self.main_loop = asyncio.new_event_loop()
        print(self.log)

    def get_socket(self):
        server_socket = socket.socket()
        server_socket.bind((self.hostname, self.port))
        server_socket.listen(MAX_CONNECTIONS)
        server_socket.setblocking(False)
        print("server has started")
        return server_socket

    def write_to_log(self, data):
        with open(self.messages, "a") as log:
            log.write(data + '\n')

    def create_response(self, **kwargs):
        response = {}
        for key, value in kwargs.items():
            response[key] = value
        return pickle.dumps(response)

    async def handling_new_messages(self, username, message):
        self.database.create_message(username, message)
        current_time = get_current_time()
        message = f"{current_time}  {message}"
        self.write_to_log(message)

        message = bytes(message, "utf-8")
        for user in self.users:
            await self.main_loop.sock_sendall(user, message)

    def register_to_db(self, _client, data):
        username = data["username"]
        password = data["password"]
        try:
            self.database.register_user(username, password)

            message = "You successfully registered. You can login to  chat"
            response = self.create_response(message=message)
            _client.send(response)

        except Exception as _err:
            print(f"{_err}\n")
            response = self.create_response(message="Username is already taken. Try another one")
            _client.send(response)

    async def authenticate_user(self, _client, data):
        _id = None

        username = data["username"].replace('"', "'")
        password = data["password"]

        try:
            _id = self.database.validate_user_data(username, password)

            if not _id:
                response = self.create_response(status="Error", message="Wrong username or password")
                await self.main_loop.sock_sendall(_client, response)
                return

            response = self.create_response(
                    status="OK",
                    message=f"You successfully joined chat, welcome, {username}!",
                    id=_id,
                    username=username,
                    log=self.log
            )
            print(response)
            await self.main_loop.sock_sendall(_client, response)
            self.users.append(_client)

        except Exception as _err:
            print(f"{_err}\n")
            response = self.create_response(status="Error", message=_err)
            await self.main_loop.sock_sendall(_client, response)

    async def accept_connection(self):
        while True:
            conn, address = await self.main_loop.sock_accept(self.socket)
            if conn and address:
                print(f"connected {address}")
                self.main_loop.create_task(self.serve_connection(conn))

    async def serve_connection(self, conn):
        print("Listening user")
        while True:
            try:
                recv_data = await self.main_loop.sock_recv(conn, 1024)
                recv_data = pickle.loads(recv_data)

                user_data = None
                if "username" in recv_data and "password" in recv_data:
                    user_data = {
                        "username": recv_data["username"],
                        "password": recv_data["password"]
                    }

                if "command" in recv_data:
                    command = recv_data["command"]
                    if command == "register":
                        self.register_to_db(conn, user_data)
                    if command == "login":
                        await self.authenticate_user(conn, user_data)

                if "message" in recv_data:
                    message = recv_data["message"]
                    username = recv_data["username"]
                    await self.main_loop.create_task(self.handling_new_messages(username, message))

            except Exception as error:
                print(error)

    async def main(self):
        await self.main_loop.create_task(self.accept_connection())


if __name__ == '__main__':
    server = ChatServer(HOSTNAME, PORT)
    while True:
        try:
            server.main_loop.run_until_complete(server.main())
        except KeyboardInterrupt:
            server.socket.close()
