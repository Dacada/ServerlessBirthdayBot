from typing import Dict, Sequence
import aws_cdk as cdk
from aws_cdk import aws_lambda, aws_logs, aws_dynamodb
from birthday_discord_bot.data import TablePermissionType


def get_lambda_args(code_asset):
    return {
        "runtime": aws_lambda.Runtime.PYTHON_3_11,
        "code": aws_lambda.Code.from_asset(
            code_asset,
            bundling=cdk.BundlingOptions(
                image=aws_lambda.Runtime.PYTHON_3_11.bundling_image,
                command=[
                    "bash",
                    "-c",
                    "pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output",
                ],
            ),
        ),
        "log_retention": aws_logs.RetentionDays.ONE_MONTH,
    }


def grant_permission(
    table: aws_dynamodb.Table,
    function: aws_lambda.Function,
    permission: TablePermissionType,
):
    if permission == TablePermissionType.Read:
        table.grant_read_data(function)
    elif permission == TablePermissionType.ReadWrite:
        table.grant_read_write_data(function)
    else:
        raise TypeError(
            f"Invalid permission {permission} for table {table_name} for function {function}"
        )


def get_table_details_for_lambda_env(
    tables: Dict[str, aws_dynamodb.Table], table_names: Sequence[str], region: str
):
    details = {}
    for name in table_names:
        details[f"{name.upper()}_TABLE_REGION"] = region
        details[f"{name.upper()}_TABLE_NAME"] = tables[name].table_name
    return details
