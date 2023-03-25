import os
from typing import Dict
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import Stack, triggers, aws_lambda, aws_sns, aws_sns_subscriptions
from birthday_discord_bot.data import sns_topic_name
from birthday_discord_bot.data import commands, TablePermissionType
from birthday_discord_bot.util import get_lambda_args
from birthday_discord_bot.util import grant_permission
from birthday_discord_bot.util import get_table_details_for_lambda_env


class CommandHandling(Stack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        self.lambda_args = get_lambda_args("resources")

        self.trigger = triggers.TriggerFunction(
            self,
            "CreateCommand",
            handler="create_command.handler",
            environment={
                "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
            },
            timeout=cdk.Duration.seconds(30),
            **self.lambda_args,
        )

        self._scope = scope
        self.sns_topic = aws_sns.Topic(self, sns_topic_name)

        self.handler_functions = {}
        for command in commands:
            if command.subcommands is None:
                handler = f"{command.name}_handler"
                self.handler_functions[command.name] = self.create_command_lambda(
                    command.name, handler, command.table_perms
                )
            else:
                for subcommand in command.subcommands:
                    name = command.name + " " + subcommand.name
                    handler = f"{command.name}_{subcommand.name}"
                    self.handler_functions[name] = self.create_command_lambda(
                        name, handler, subcommand.table_perms
                    )

    def create_command_lambda(
        self, name: str, handler: str, permissions: Dict[str, TablePermissionType]
    ):
        function = aws_lambda.Function(
            self,
            f"Command{''.join([n.capitalize() for n in name.split()])}Handler",
            handler="bot_commands." + handler,
            environment={
                "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
                **get_table_details_for_lambda_env(
                    self._scope.data_layer.tables,
                    permissions.keys(),
                    os.environ["AWS_DEFAULT_REGION"],
                ),
            },
            **self.lambda_args,
        )

        self.sns_topic.add_subscription(
            aws_sns_subscriptions.LambdaSubscription(
                function,
                filter_policy={
                    "command": aws_sns.SubscriptionFilter.string_filter(
                        allowlist=[name]
                    ),
                },
            )
        )

        for table_name, permission in permissions.items():
            grant_permission(
                self._scope.data_layer.tables[table_name], function, permission
            )

        return function
