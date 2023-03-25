#!/usr/bin/env python3

import os
import aws_cdk as cdk
from birthday_discord_bot import BirthdayDiscordBot

app = cdk.App()
birthday_bot_prod = BirthdayDiscordBot(app, "BirthdayDiscordBot")
app.synth()
