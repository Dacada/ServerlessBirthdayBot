import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import triggers, aws_lambda


class CreateCommandTrigger(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)
        trigger = triggers.TriggerFunction(
            self,
            "Handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(
                "resources",
                bundling=cdk.BundlingOptions(
                    image=aws_lambda.Runtime.PYTHON_3_8.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
                    ],
                ),
            ),
            handler="create_command.handler",
            environment={
                "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
            },
        )
