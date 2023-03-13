from aws_cdk import Stack
from constructs import Construct
from . import api_proxy_service, create_command_trigger, command_handling_service


class BirthdayDiscordBotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        command_handling = command_handling_service.CommandHandlingService(
            self, "CommandHandling"
        )
        api_proxy_service.BotAPIService(self, "BotAPI", command_handling.topic)
        create_command_trigger.CreateCommandTrigger(self, "CreateCommandTrigger")
