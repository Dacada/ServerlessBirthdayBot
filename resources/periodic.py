import os
import functools
from datetime import datetime, date
from pynamodb.exceptions import DoesNotExist
import jinja2
import requests
import db
import default
from request_wrapper import request_wrapper


def render_string(string, variables):
    template = jinja2.Environment().from_string(string)
    return template.render(**variables)


def periodic_task(fun):
    @functools.wraps(fun)
    def wrapper(event, context):
        print(f"event: {event}")
        for channel_id, message in fun(
            datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%SZ")
        ):
            if channel_id is None and message is None:
                break

            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            payload = {"content": message}
            headers = {"Authorization": "Bot " + os.environ["DISCORD_BOT_TOKEN"]}
            request_wrapper(requests.post, url, headers=headers, json=payload)

    return wrapper


@periodic_task
def greeting_handler(when):
    @functools.lru_cache
    def get_info(server_id):
        try:
            server_item = db.Servers.get(item.server_id)
        except DoesNotExist:
            return None
        else:
            if server_item.channel_id is None:
                return None
            return (
                server_item.greeting or default.GREETING_MESSAGE
            ), server_item.channel_id

    for item in db.Users.scan(
        (db.Users.birthday_day == when.day) & (db.Users.birthday_month == when.month)
    ):
        t = get_info(item.server_id)
        if t is None:
            continue
        greeting, channel_id = t

        yield channel_id, render_string(
            greeting,
            {
                "user": f"<@{item.user_id}>",
                "wish": item.wish,
                "day": item.birthday_day,
                "month": item.birthday_month,
                "daysleft": 0,
                "setwishcmd": "/wishing set",
            },
        )


@periodic_task
def reminder_handler(when):
    @functools.lru_cache
    def get_info(server_id):
        try:
            server_item = db.Servers.get(item.server_id)
        except DoesNotExist:
            return None
        else:
            if server_item.channel_id is None:
                return None
            return (
                (server_item.wish_reminder_period or default.WISH_PERIOD),
                (server_item.wish_reminder_message or default.WISH_MESSAGE),
                server_item.channel_id,
            )

    next_month = when.month + 1
    next_year = when.year
    if next_month > 12:
        next_month -= 12
        next_year += 1

    dms = {}
    for item in db.Users.scan(
        db.Users.wish.does_not_exist()
        & db.Users.birthday_month.between(when.month, next_month)
    ):
        t = get_info(item.server_id)
        if t is None:
            continue

        period, message, channel_id = t
        birth_date = date(next_year, item.birthday_month, item.birthday_day)

        delta = birth_date - when.date()
        if delta.days > period:
            continue

        yield channel_id, render_string(
            message,
            {
                "user": f"<@{item.user_id}>",
                "wish": item.wish,
                "day": item.birthday_day,
                "month": item.birthday_month,
                "daysleft": delta.days,
                "setwishcmd": "/wishing set",
            },
        )


@periodic_task
def cleanup_handler(when):
    prev_month = when.month - 1
    prev_year = when.year
    if prev_month < 1:
        prev_month += 12
        prev_year -= 1

    for item in db.Users.scan(
        db.Users.wish.exists() & db.Users.birthday_month.between(prev_month, when.month)
    ):
        item.update(actions=[db.Users.wish.remove()])

    yield None, None
