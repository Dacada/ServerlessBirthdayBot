import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_sns, aws_lambda, aws_sns_subscriptions, aws_logs, aws_dynamodb
from . import lambda_code
from resources import bot_commands


def grant_permissions(
    function: aws_lambda.Function,
    perm: bot_commands.PermissionType,
    table: aws_dynamodb.Table,
):
    if perm == bot_commands.PermissionType.Read:
        table.grant_read_data(function)
    elif perm == bot_commands.PermissionType.ReadWrite:
        table.grant_read_write_data(function)


class CommandHandlingService(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        users_table: aws_dynamodb.Table,
        servers_table: aws_dynamodb.Table,
    ) -> None:
        super().__init__(scope, id)

        self.users_table = users_table
        self.servers_table = servers_table

        self.topic = aws_sns.Topic(
            self,
            "BotCommandTopic",
        )

        for name, data in bot_commands.all_commands.items():
            if data.subcommands is None:
                self.create_command_lambda(
                    name, data.handler, data.user_data, data.server_data
                )
            else:
                for second_name, second_data in data.subcommands.items():
                    self.create_command_lambda(
                        name + " " + second_name,
                        second_data.handler,
                        second_data.user_data,
                        second_data.server_data,
                    )

    def create_command_lambda(
        self,
        command_name: str,
        handler: str,
        user_perm: bot_commands.PermissionType,
        server_perm: bot_commands.PermissionType,
    ):
        function = aws_lambda.Function(
            self,
            f"Command{''.join([n.capitalize() for n in command_name.split()])}Handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=lambda_code.lambda_code,
            handler="bot_commands." + handler,
            environment={
                "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
            },
            log_retention=aws_logs.RetentionDays.ONE_MONTH,
        )

        self.topic.add_subscription(
            aws_sns_subscriptions.LambdaSubscription(
                function,
                filter_policy={
                    "command": aws_sns.SubscriptionFilter.string_filter(
                        allowlist=[command_name]
                    ),
                },
            )
        )

        grant_permissions(function, user_perm, self.users_table)
        grant_permissions(function, server_perm, self.servers_table)
