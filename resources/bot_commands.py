import os
import functools
import json
import requests


def command_handler(fun):
    @functools.wraps(fun)
    def wrapper(event, context):
        print(f"event: {event}")
        headers = {"Authorization": "Bot " + os.environ["DISCORD_BOT_TOKEN"]}
        for record in event["Records"]:
            message = json.loads(record["Sns"]["Message"])
            token = message["token"]
            url = f"https://discord.com/api/v10/webhooks/{os.environ['DISCORD_APPLICATION_ID']}/{token}/messages/@original"
            payload = {"content": fun(**message)}
            r = requests.patch(url, headers=headers, json=payload)
            r.raise_for_status()

    return wrapper


@command_handler
def hello_handler(**kwargs):
    return "Hello world!"


all_commands = {
    "hello": {"description": "Test command", "handler": hello_handler.__name__}
}
