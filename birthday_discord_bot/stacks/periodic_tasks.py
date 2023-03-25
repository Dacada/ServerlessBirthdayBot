import os
import aws_cdk as cdk
from aws_cdk import Stack, aws_events, aws_lambda, aws_events_targets
from constructs import Construct
from birthday_discord_bot.data import periodic_tasks
from birthday_discord_bot.util import get_lambda_args
from birthday_discord_bot.util import grant_permission
from birthday_discord_bot.util import get_table_details_for_lambda_env


class PeriodicTasks(Stack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        self.schedule_rule = aws_events.Rule(
            self,
            "ScheduleRule",
            schedule=aws_events.Schedule.cron(minute="0", hour="12"),
        )

        self.tasks = []
        for task in periodic_tasks:
            function = aws_lambda.Function(
                self,
                task.name.capitalize(),
                handler=f"periodic.{task.name}_handler",
                environment={
                    "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                    "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
                    **get_table_details_for_lambda_env(
                        scope.data_layer.tables,
                        task.table_perms.keys(),
                        os.environ["AWS_DEFAULT_REGION"],
                    ),
                },
                timeout=cdk.Duration.minutes(5),
                **get_lambda_args("resources"),
            )

            for table_name, permission in task.table_perms.items():
                grant_permission(
                    scope.data_layer.tables[table_name], function, permission
                )

            self.schedule_rule.add_target(aws_events_targets.LambdaFunction(function))

            self.tasks.append(function)
