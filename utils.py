from asyncio import AbstractEventLoop
import time
import pickle


async def get_user_credentials(event_loop: AbstractEventLoop):
    username = await event_loop.run_in_executor(None, input, "Enter your username \n")
    password = await event_loop.run_in_executor(None, input, "Enter your password \n")

    credentials = {
        "username": username,
        "password": password
    }

    return credentials


async def get_user_command(event_loop: AbstractEventLoop):
    condition = 'Welcome to the main menu!\nPlease, enter the command \n(\'reg\' if you want to register or ' \
                '\'login\' to login)\n'

    command = await event_loop.run_in_executor(
        None,
        input,
        condition
    )

    return command


def get_current_time():
    _time = time.localtime()
    hours = _time[3] if len(f"{_time[3]}") == 2 else f"0{_time[3]}"
    minutes = _time[4] if len(f"{_time[4]}") == 2 else f"0{_time[4]}"
    current_time = f"{hours}:{minutes}"
    return current_time


def create_response(**kwargs):
    response = {}
    for key, value in kwargs.items():
        response[key] = value
    return pickle.dumps(response)