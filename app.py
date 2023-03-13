#!/usr/bin/env python3
import os

import aws_cdk as cdk

from birthday_discord_bot.birthday_discord_bot_stack import BirthdayDiscordBotStack


app = cdk.App()
BirthdayDiscordBotStack(
    app,
    "BirthdayDiscordBotStack",
)

app.synth()
