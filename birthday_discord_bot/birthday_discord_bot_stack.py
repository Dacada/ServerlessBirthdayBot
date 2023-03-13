from aws_cdk import Stack
from constructs import Construct
from . import api_proxy_service, create_command_trigger


class BirthdayDiscordBotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        api_proxy_service.BotAPIService(self, "BotAPI")
        create_command_trigger.CreateCommandTrigger(self, "CreateCommandTrigger")
