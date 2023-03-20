from aws_cdk import Stack
from constructs import Construct
from . import (
    api_proxy_service,
    create_command_trigger,
    command_handling_service,
    data_layer,
    periodic_tasks,
)


class BirthdayDiscordBotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        data = data_layer.DataLayer(self, "DataLayer")
        command_handling = command_handling_service.CommandHandlingService(
            self, "CommandHandling", data.users, data.servers
        )
        api_proxy_service.BotAPIService(self, "BotAPI", command_handling.topic)
        periodic_tasks.PeriodicTasks(self, "PeriodicTasks", data.users, data.servers)
        create_command_trigger.CreateCommandTrigger(self, "CreateCommandTrigger")
