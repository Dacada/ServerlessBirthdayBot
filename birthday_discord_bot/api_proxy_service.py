import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_apigateway, aws_lambda
from . import lambda_code


class BotAPIService(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        handler = aws_lambda.Function(
            self,
            "Handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=lambda_code.lambda_code,
            handler="proxy_lambda.handler",
            environment={
                "DISCORD_PUBLIC_KEY": os.environ["DISCORD_PUBLIC_KEY"],
            },
        )
        api = aws_apigateway.RestApi(
            self,
            "bot-api",
            rest_api_name="Bot API Service",
            description="Handles requests from Discord for the bot",
        )
        integration = aws_apigateway.LambdaIntegration(
            handler, request_templates={"application/json": '{ "statusCode": "200" }'}
        )
        api.root.add_method("POST", integration)
