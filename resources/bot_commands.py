import os
import functools
import json
import time
import datetime
import requests
from enum import Enum, IntEnum
from dataclasses import dataclass, asdict
from typing import Optional, Union, Dict
from pynamodb.exceptions import DoesNotExist

try:
    from resources import db
    from resources import default
    from resources.request_wrapper import request_wrapper
except ModuleNotFoundError:
    import db
    import default
    from request_wrapper import request_wrapper


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
            options["_current_server_id"] = message["guild_id"]

            try:
                payload = fun(**options)
            except Exception as e:
                payload = {
                    "content": f"An error occurred while trying to run this command: {e}"
                }

            request_wrapper(requests.patch, url, headers=headers, json=payload)

    return wrapper


@command_handler
def set_handler(day, month, _caller, _current_server_id, **kwargs):
    user_id = _caller["id"]
    server_id = _current_server_id

    try:
        item = db.Users.get(user_id, server_id)
    except DoesNotExist:
        item = db.Users(user_id, server_id, birthday_day=day, birthday_month=month)
        item.save()
    else:
        try:
            datetime.date(2000, month, day)
        except ValueError as e:
            return {"content": f"Could not set birthday: {e}"}

        item.update(
            actions=[
                db.Users.birthday_day.set(day),
                db.Users.birthday_month.set(month),
            ]
        )

    return {"content": f"Your birthday has been set to {day}/{month}"}


@command_handler
def get_handler(_caller, _current_server_id, user=None, **kwargs):
    user_id = user or _caller["id"]
    server_id = _current_server_id

    result = {
        "content": f"The user <@{user_id}> does not have a birthday nor wish assigned."
    }

    try:
        item = db.Users.get(user_id, server_id)
    except DoesNotExist:
        return result

    no_birthday = item.birthday_day is None or item.birthday_month is None
    no_wish = item.wish is None

    if no_birthday and no_wish:
        return result

    if no_birthday:
        birthday_str = f"The user <@{user_id}> does not have a birthday set."
    else:
        birthday_str = f"The birthday for <@{user_id}> is {item.birthday_day}/{item.birthday_month}."

    if no_wish:
        wish_str = "No birthday wish is set for this user."
    else:
        wish_str = f'The birthday wish for this user is "{item.wish}".'

    return {
        "content": f"{birthday_str} {wish_str}",
        "allowed_mentions": {"parse": []},
    }


@command_handler
def retrieve_handler(_current_server_id, **kwargs):
    today = datetime.date.today()
    server_id = _current_server_id

    result = []
    for item in db.Users.users_by_server_index.query(server_id):
        user_id = item.user_id

        day = item.birthday_day
        month = item.birthday_month
        if day is None or month is None:
            birthday = "No birthday set."
        else:
            birthday = f"{day}/{month}"

        wish = item.wish
        if wish is None:
            wish = "No wish set."
        else:
            wish = f'"{wish}"'

        try:
            next_bday = datetime.date(today.year, month, day)
        except ValueError:
            # Cursed 29th of feburary birthday
            next_bday = datetime.date(today.year + 1, month, day)  # uwu
        else:
            if next_bday < today:
                next_bday = datetime.date(today.year + 1, month, day)

        result.append((next_bday, f"<@{user_id}> - {birthday} - {wish}"))

    result.sort()
    result = [x[1] for x in result]

    if not result:
        return {
            "content": "No birthdays or wishes set up for any users in this server."
        }

    return {
        "content": "\n".join(result),
        "allowed_mentions": {"parse": []},
    }


@command_handler
def channel_handler(channel, _current_server_id, **kwargs):
    channel_id = channel
    server_id = _current_server_id

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        item = db.Servers(server_id, channel_id=channel_id)
        item.save()
    else:
        item.update(
            actions=[
                db.Servers.channel_id.set(channel_id),
            ]
        )

    return {
        "content": f"The channel where greetings will be posted has been set to <#{channel}>"
    }


@command_handler
def greeting_handler(message, _current_server_id, **kwargs):
    server_id = _current_server_id
    greeting = message

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        item = db.Servers(server_id, greeting=greeting)
        item.save()
    else:
        item.update(
            actions=[
                db.Servers.greeting.set(greeting),
            ]
        )

    return {
        "content": f"The greeting the bot sends has been set to:\n{message}",
        "allowed_mentions": {"parse": []},
    }


@command_handler
def wishing_enable_handler(_current_server_id, **kwargs):
    server_id = _current_server_id

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        item = db.Servers(server_id, wish_reminder_enabled=True)
        item.save()
    else:
        item.update(
            actions=[
                db.Servers.wish_reminder_enabled.set(True),
            ]
        )

    return {"content": "Wish reminder is enabled"}


@command_handler
def wishing_disable_handler(_current_server_id, **kwargs):
    server_id = _current_server_id

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        item = db.Servers(server_id, wish_reminder_enabled=False)
        item.save()
    else:
        item.update(
            actions=[
                db.Servers.wish_reminder_enabled.set(False),
            ]
        )

    return {"content": "Wish reminder is disabled"}


@command_handler
def wishing_period_handler(days, _current_server_id, **kwargs):
    server_id = _current_server_id
    wish_reminder_period = days

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        item = db.Servers(server_id, wish_reminder_period=wish_reminder_period)
        item.save()
    else:
        item.update(
            actions=[
                db.Servers.wish_reminder_period.set(wish_reminder_period),
            ]
        )

    return {"content": f"Wish reminder period is set to {wish_reminder_period} days"}


@command_handler
def wishing_reminder_handler(message, _current_server_id, **kwargs):
    server_id = _current_server_id
    wish_reminder_message = message

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        item = db.Servers(server_id, wish_reminder_message=wish_reminder_message)
        item.save()
    else:
        item.update(
            actions=[
                db.Servers.wish_reminder_message.set(wish_reminder_message),
            ]
        )

    return {"content": f"Wish reminder message is set to:\n{wish_reminder_message}"}


@command_handler
def wishing_set_handler(wish, _caller, _current_server_id, **kwargs):
    user_id = _caller["id"]
    server_id = _current_server_id

    try:
        item = db.Users.get(user_id, server_id)
    except DoesNotExist:
        item = db.Users(user_id, server_id, wish=wish)
        item.save()
    else:
        item.update(
            actions=[
                db.Users.wish.set(wish),
            ]
        )

    return {"content": f"Your birthday wish has been set to:\n{wish}"}


@command_handler
def status_handler(_current_server_id, **kwargs):
    server_id = _current_server_id

    no_channel = "No channel set."
    reminders_enabled = "Enabled."
    reminders_disabled = "Disabled."

    try:
        item = db.Servers.get(server_id)
    except DoesNotExist:
        channel = no_channel
        reminders = reminders_enabled
        period = default.WISH_PERIOD
        wish_msg = default.WISH_MESSAGE
        greet_msg = default.GREETING_MESSAGE
    else:
        if item.channel_id is None:
            channel = no_channel
        else:
            channel = f"<#{item.channel_id}>"

        if item.greeting is None:
            greet_msg = default.GREETING_MESSAGE
        else:
            greet_msg = item.greeting

        if item.wish_reminder_enabled is None or item.wish_reminder_enabled:
            reminders = reminders_enabled
        else:
            reminders = reminders_disabled

        if item.wish_reminder_period is None:
            period = default.WISH_PERIOD
        else:
            period = item.wish_reminder_period

        if item.wish_reminder_message is None:
            wish_msg = default.WISH_MESSAGE
        else:
            wish_msg = item.wish_reminder_message

    return {
        "content": f"Greetings channel: {channel}\nWish remainders: {reminders}\nWish period: {period} days\nWish message:\n{wish_msg}\nGreeting:\n{greet_msg}\n\nUse the retrieve command to get a list of all wishes in the server by user."
    }


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
        description="Set the channel where the bot will send birthday greetings and reminders to set a wish",
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
                description="Enable reminding users to set a wish before their birthday",
                handler=wishing_enable_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "disable": BotCommand(
                description="Disable reminding users to set a wish before their birthday",
                handler=wishing_disable_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "period": BotCommand(
                description="Users without a wish will get a mention these many days before their birthday.",
                arguments={
                    "days": BotOption(
                        type=OptionType.INTEGER,
                        description="Days for the period",
                        min_value=1,
                        max_value=30,
                    ),
                },
                handler=wishing_period_handler.__name__,
                user_data=None,
                server_data=PermissionType.ReadWrite,
            ),
            "reminder": BotCommand(
                description="Set the message that the bot will send to remind to set a wish for people's birthdays.",
                arguments={
                    "message": BotOption(
                        type=OptionType.STRING,
                        description="The message the bot will send",
                    ),
                },
                handler=wishing_reminder_handler.__name__,
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
                handler=wishing_set_handler.__name__,
                user_data=PermissionType.ReadWrite,
                server_data=None,
            ),
        },
    ),
    "status": BotCommand(
        description="See the bot's status and configuration",
        handler=status_handler.__name__,
        user_data=None,
        server_data=PermissionType.Read,
    ),
}
