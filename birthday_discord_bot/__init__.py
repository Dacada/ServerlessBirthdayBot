from constructs import Construct
from birthday_discord_bot.stacks import (
    DataLayer,
    CommandHandling,
    ProxyLambda,
    PeriodicTasks,
)


class BirthdayDiscordBot(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        self.data_layer = DataLayer(self, "DataLayer")
        self.command_handling = CommandHandling(self, "CommandHandling")
        self.proxy_lambda = ProxyLambda(self, "ProxyLambda")
        self.periodic_tasks = PeriodicTasks(self, "PeriodicTasks")
