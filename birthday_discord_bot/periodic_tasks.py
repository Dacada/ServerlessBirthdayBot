import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_lambda, aws_events, aws_dynamodb, aws_logs, aws_events_targets
from . import lambda_code


class PeriodicTasks(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        users_table: aws_dynamodb.Table,
        servers_table: aws_dynamodb.Table,
    ) -> None:
        super().__init__(scope, id)

        functions = []
        for handler in ["reminder", "greeting", "cleanup"]:
            fun = aws_lambda.Function(
                self,
                handler.capitalize(),
                runtime=aws_lambda.Runtime.PYTHON_3_8,
                code=lambda_code.lambda_code,
                handler=f"periodic.{handler}_handler",
                environment={
                    "DISCORD_APPLICATION_ID": os.environ["DISCORD_APPLICATION_ID"],
                    "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
                    "USERS_TABLE_REGION": os.environ["AWS_DEFAULT_REGION"],
                    "USERS_TABLE_NAME": users_table.table_name,
                    "SERVERS_TABLE_REGION": os.environ["AWS_DEFAULT_REGION"],
                    "SERVERS_TABLE_NAME": servers_table.table_name,
                },
                log_retention=aws_logs.RetentionDays.ONE_MONTH,
                timeout=cdk.Duration.minutes(5),
            )
            servers_table.grant_read_data(fun)
            if handler == "cleanup":
                users_table.grant_read_write_data(fun)
            else:
                users_table.grant_read_data(fun)
            functions.append(fun)

        rule = aws_events.Rule(
            self,
            "ScheduleRule",
            schedule=aws_events.Schedule.cron(minute="0", hour="12"),
        )

        for fun in functions:
            rule.add_target(aws_events_targets.LambdaFunction(fun))
