import asyncio
import os
import socket
import pickle

from settings import HOSTNAME, PORT
from utils import get_user_credentials, get_user_command


class Client:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect((HOSTNAME, PORT))
        self.socket.setblocking(False)

        self.main_loop = asyncio.new_event_loop()
        self.user = None
        self.chat = ''

    async def send_message(self):
        while True:
            os.system('clear')
            print(self.chat)
            username = self.user["username"]
            user_input = await self.main_loop.run_in_executor(None, input)
            if user_input:
                message = {"message": user_input, "username": username}
                message = pickle.dumps(message)
                await self.main_loop.sock_sendall(self.socket, message)

    async def main_menu(self):
        command = await get_user_command(self.main_loop)
        if not command:
            return

        user_credentials = await get_user_credentials(self.main_loop)
        if command == 'reg':
            await self.register_user(user_credentials)
        if command == 'login':
            self.user = await self.login_user(user_credentials)

    async def listen_server(self):
        while True:
            message = await self.main_loop.sock_recv(self.socket, 1024)
            message = message.decode()
            self.chat += f"{message}\n"
            print(f"{message}\n")

    async def register_user(self, credentials):
        data = {}

        if credentials:
            data.update(credentials)

        if data:
            data["command"] = "register"
            data = pickle.dumps(data)

        try:
            await self.main_loop.sock_sendall(self.socket, data)
            response = await self.main_loop.sock_recv(self.socket, 1024)
            response = pickle.loads(response)

            message = response["message"]

            print(message)

        except OSError as _err:
            print(f"{_err}\n")

        finally:
            await self.main_menu()

    async def login_user(self, credentials):
        data = {}
        chat_log = []

        if credentials:
            data.update(credentials)

        if data:
            data["command"] = "login"
            data = pickle.dumps(data)

        try:
            await self.main_loop.sock_sendall(self.socket, data)
            response = await self.main_loop.sock_recv(self.socket, 1024)
            response = pickle.loads(response)
            print(response)

            res_status = response["status"]
            res_message = response["message"]

            if "log" in response:
                chat_log = response["log"]

            if res_status == "Error":
                print(res_message)
                await self.main_menu()

            self.chat += f"{res_message}\n"
            for message in chat_log:
                sender = message[0]
                body = message[1]
                _datetime = message[2]
                self.chat += f"{_datetime} {sender}: {body}\n"

            user = {
                "id": response["id"],
                "username": response["username"]
            }
            return user

        except OSError as _err:
            print(f"{_err}\n")
            await self.main_menu()

    async def main(self):
        await asyncio.gather(
            self.main_loop.create_task(self.send_message()),
            self.main_loop.create_task(self.listen_server())
        )


if __name__ == "__main__":
    client = Client()

    while not client.user:
        client.main_loop.run_until_complete(client.main_menu())

    while True:
        client.main_loop.run_until_complete(client.main())
