import os
import functools
import json
import time
import requests
from enum import Enum, IntEnum
from dataclasses import dataclass, asdict
from typing import Optional, Union, Dict


def request_wrapper(method, *args, **kwargs):
    print(
        f"doing a {method.__name__} request with parameters args={args} kwargs={kwargs}"
    )

    r = method(*args, **kwargs)
    print(f"status code = {r.status_code}")
    print(f"headers = {r.headers}")

    try:
        text = r.text
    except:
        text = None
    print(f"content = {text}")

    if r.status_code == 429:
        data = r.json()
        print(
            f"rate limit encountered: '{data['message']}', sleeping for {data['retry_after']} seconds and retrying"
        )
        time.sleep(data["retry_after"])
        request_wrapper(method, *args, **kwargs)
        return

    r.raise_for_status()

    remaining = int(r.headers["X-RateLimit-Remaining"])
    print(f"Rate limit remaining: {remaining}")
    if remaining == 0:
        reset_after = float(r.headers["X-RateLimit-Reset-After"])
        print(
            f"Remaining is zero. Sleeping for {reset_after} seconds before continuing"
        )
        time.sleep(reset_after)

    return r


def command_handler(fun):
    @functools.wraps(fun)
    def wrapper(event, context):
        print(f"event: {event}")
        headers = {"Authorization": "Bot " + os.environ["DISCORD_BOT_TOKEN"]}
        for record in event["Records"]:
            message = json.loads(record["Sns"]["Message"])
            token = message["token"]
            url = f"https://discord.com/api/v10/webhooks/{os.environ['DISCORD_APPLICATION_ID']}/{token}/messages/@original"

            options = {}
            for option in message["data"].get("options", ()):
                if option["type"] > 2:
                    options[option["name"]] = option["value"]
                else:
                    for option2 in option.get("options", ()):
                        if option2["type"] > 2:
                            options[option2["name"]] = option2["value"]
            options["_caller"] = message["member"]["user"]

            payload = fun(**options)
            r = request_wrapper(requests.patch, url, headers=headers, json=payload)
            r.raise_for_status()

    return wrapper


@command_handler
def set_handler(day, month, **kwargs):
    return {
        "content": f"This command would set up your birthday. It would set it to {day} {month}"
    }


@command_handler
def get_handler(_caller, user=None, **kwargs):
    user_id = user or _caller["id"]
    return {
        "content": f"This command would show you the birthday and wish of a user. The user would be <@{user_id}>"
    }


@command_handler
def retrieve_handler(**kwargs):
    return {
        "content": "This command would show you the birthdays and wishes of all users in the server."
    }


@command_handler
def channel_handler(channel, **kwargs):
    return {
        "content": f"This command would set the channel the bot sends greetings to. It would set it to <#{channel}>"
    }


@command_handler
def greeting_handler(message, **kwargs):
    return {
        "content": f"This command would set the greeting the bot sends. It would set it to {message}",
        "allowed_mentions": {"parse": []},
    }


@command_handler
def wishing_enable_handler(**kwargs):
    return {"content": "This command would enable wishing system"}


@command_handler
def wishing_disable_handler(**kwargs):
    return {"content": "This command would disable wishing system"}


@command_handler
def wishing_remind_handler(**kwargs):
    return {"content": "This command would enable wish reminding"}


@command_handler
def wishing_noremind_handler(**kwargs):
    return {"content": "This command would disable wish reminding"}


@command_handler
def wishing_period_handler(days, **kwargs):
    return {"content": f"This command would set the wish period to {days}"}


@command_handler
def wishing_message_handler(message, **kwargs):
    return {
        "content": f"This command would set the wish message to {message}",
        "allowed_mentions": {"parse": []},
    }


@command_handler
def wishing_wish_handler(wish, _caller, **kwargs):
    user_id = _caller["id"]
    return {
        "content": f"This command would set the user's wish to {wish} for the user <@{user_id}>",
        "allowed_mentions": {
            "users": [user_id],
        },
    }


@command_handler
def status_handler(**kwargs):
    return {"content": "This command would show you the bot's status"}


class OptionType(IntEnum):
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9  # includes users and roles
    NUMBER = 10  # floating point


class PermissionType(Enum):
    Read = 1
    ReadWrite = 2


@dataclass
class BotOption:
    type: OptionType
    description: str
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None

    def asdict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class BotCommand:
    description: str
    handler: Optional[str] = None  # either handler or subcommands must be set
    subcommands: Optional[
        Dict[str, "BotCommand"]
    ] = None  # subcommands cannot be nested (e.g., all these should have handlers)
    arguments: Optional[Dict[str, "BotOption"]] = None  # mandatory arguments
    options: Optional[Dict[str, "BotOption"]] = None  # optional options
    user_data: Optional[PermissionType] = None
    server_data: Optional[PermissionType] = None


all_commands = {
    "set": BotCommand(
        description="Set user's birthday",
        arguments={
            "day": BotOption(
                type=OptionType.INTEGER,
                description="Birthday day of the month",
                min_value=1,
                max_value=31,
            ),
            "month": BotOption(
                type=OptionType.INTEGER,
                description="Birthday month",
                min_value=1,
                max_value=12,
            ),
        },
        handler=set_handler.__name__,
        user_data=PermissionType.ReadWrite,
        server_data=None,
    ),
    "get": BotCommand(
        description="Retrieve a user's birthday and whether they have a wish set.",
        options={
            "user": BotOption(
                type=OptionType.USER,
                description="User to retrieve the birthday of. If not given, return your own.",
            )
        },
        handler=get_handler.__name__,
        user_data=PermissionType.Read,
        server_data=None,
    ),
    "retrieve": BotCommand(
        description="Retrieve the birthdays and wishes of all users in the server.",
        handler=retrieve_handler.__name__,
        user_data=PermissionType.Read,
        server_data=None,
    ),
    "channel": BotCommand(
        description="Set the channel where the bot will send birthday greetings",
        arguments={
            "channel": BotOption(
                type=OptionType.CHANNEL,
                description="Channel to set this to",
            )
        },
        handler=channel_handler.__name__,
        user_data=None,
        server_data=PermissionType.ReadWrite,
    ),
    "greeting": BotCommand(
        description="Set the greeting that the bot will use when greeting users for their birthday.",
        arguments={
            "message": BotOption(
                type=OptionType.STRING,
                description="Message to set the greeting to",
            )
        },
        handler=greeting_handler.__name__,
        user_data=None,
        server_data=PermissionType.ReadWrite,
    ),
    "wishing": BotCommand(
        description="Commands relating to seeing/adding/configuring birthday wishes",
        subcommands={
            "enable": BotCommand(
                description="Enable wishing system",
                handler=wishing_enable_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "disable": BotCommand(
                description="Disable wishing system",
                handler=wishing_disable_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "remind": BotCommand(
                description="Enable reminding users to set a wish before their birthday",
                handler=wishing_remind_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "noremind": BotCommand(
                description="Disable reminding users to set a wish before their birthday",
                handler=wishing_noremind_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "period": BotCommand(
                description="Users without a wish will get a DM these many days before their birthday.",
                arguments={
                    "days": BotOption(
                        type=OptionType.INTEGER,
                        description="Days for the period",
                        min_value=1,
                        max_value=300,
                    ),
                },
                handler=wishing_period_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "message": BotCommand(
                description="Set the message that the bot will DM to remind to set a wish for people's birthdays.",
                arguments={
                    "message": BotOption(
                        type=OptionType.STRING,
                        description="The message the bot will send",
                    ),
                },
                handler=wishing_message_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "set": BotCommand(
                description="Set your birthday wish",
                arguments={
                    "wish": BotOption(
                        type=OptionType.STRING,
                        description="What do you wish for?",
                    ),
                },
                handler=wishing_wish_handler.__name__,
                user_data=PermissionType.ReadWrite,
                server_data=None,
            ),
        },
    ),
    "status": BotCommand(
        description="See the bot's status and configuration",
        handler=status_handler.__name__,
        user_data=PermissionType.Read,
        server_data=PermissionType.Read,
    ),
}
