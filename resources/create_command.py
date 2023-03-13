import os
import requests
import bot_commands

ENDPOINT = (
    "https://discord.com/api/v10/applications/" + os.environ["DISCORD_APPLICATION_ID"]
)


def handler(event, context):
    headers = {"Authorization": "Bot " + os.environ["DISCORD_BOT_TOKEN"]}

    # Retrieve current existing commands
    url = ENDPOINT + "/commands"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    print(f"Existing commands: {data}")

    # Retrieve commands we should have
    names = set(command["name"] for command in bot_commands.all_commands)
    print(f"Commands we should have: {names}")

    # Delete commands we don't have
    for command in data:
        if command["name"] not in names:
            print(f"Delete command {command['name']}")
            url = ENDPOINT + "/commands/" + command["id"]
            requests.delete(url, headers=headers)

    # Add all commands we do have, overwriting them
    url = ENDPOINT + "/commands"
    for command in bot_commands.all_commands:
        print(f"Create/update command {command['name']}")
        json = {
            "type": 1,
            "name": command["name"],
            "description": command["description"],
        }
        r = requests.post(url, headers=headers, json=json)
        r.raise_for_status()
