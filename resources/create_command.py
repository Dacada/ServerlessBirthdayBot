import os
import requests
import bot_commands

ENDPOINT = (
    "https://discord.com/api/v10/applications/" + os.environ["DISCORD_APPLICATION_ID"]
)


def get_arguments(data):
    options = []
    if data.arguments is not None:
        for name, argdata in data.arguments.items():
            options.append({"name": name, "required": True, **argdata.asdict()})
    return options


def get_options(data):
    options = []
    if data.options is not None:
        for name, argdata in data.options.items():
            options.append({"name": name, "required": False, **argdata.asdict()})
    return options


def get_subcommands(data):
    options = []
    if data.subcommands is not None:
        for name, argdata in data.subcommands.items():
            options.append(
                {
                    "name": name,
                    "type": 1,
                    "description": argdata.description,
                    "options": get_arguments(argdata) + get_options(argdata),
                }
            )
    return options


def handler(event, context):
    headers = {"Authorization": "Bot " + os.environ["DISCORD_BOT_TOKEN"]}

    # Retrieve current existing commands
    url = ENDPOINT + "/commands"
    r = bot_commands.request_wrapper(requests.get, url, headers=headers)
    data = r.json()
    print(f"Existing commands: {data}")

    # Retrieve commands we should have
    names = set(bot_commands.all_commands.keys())
    print(f"Commands we should have: {names}")

    # Delete commands we don't have
    for command in data:
        if command["name"] not in names:
            print(f"Delete command {command['name']}")
            url = ENDPOINT + "/commands/" + command["id"]
            bot_commands.request_wrapper(requests.delete, url, headers=headers)

    # Add all commands we do have, overwriting them
    url = ENDPOINT + "/commands"
    for name, data in bot_commands.all_commands.items():
        print(f"Create/update command {name}")
        json = {
            "type": 1,
            "name": name,
            "description": data.description,
            "options": get_arguments(data) + get_subcommands(data) + get_options(data),
        }
        r = bot_commands.request_wrapper(requests.post, url, headers=headers, json=json)
