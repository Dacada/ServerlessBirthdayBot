import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_sns, aws_lambda, aws_sns_subscriptions
from . import lambda_code
from resources import bot_commands


class CommandHandlingService(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.topic = aws_sns.Topic(
            self,
            "BotCommandTopic",
        )

        for name, data in bot_commands.all_commands.items():
            function = aws_lambda.Function(
                self,
                f"Command{name.capitalize()}Handler",
                runtime=aws_lambda.Runtime.PYTHON_3_8,
                code=lambda_code.lambda_code,
                handler="bot_commands." + data["handler"],
                environment={
                    "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                    "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
                },
            )
            self.topic.add_subscription(
                aws_sns_subscriptions.LambdaSubscription(
                    function,
                    filter_policy={
                        "command": aws_sns.SubscriptionFilter.string_filter(
                            allowlist=[name]
                        ),
                    },
                )
            )
