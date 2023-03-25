import os
from constructs import Construct
from aws_cdk import Stack, aws_lambda, aws_apigateway
from birthday_discord_bot.util import get_lambda_args


class ProxyLambda(Stack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        self.proxy = aws_lambda.Function(
            self,
            "Proxy",
            handler="proxy_lambda.handler",
            environment={
                "DISCORD_PUBLIC_KEY": os.environ["DISCORD_PUBLIC_KEY"],
                "SNS_TOPIC_ARN": scope.command_handling.sns_topic.topic_arn,
            },
            **get_lambda_args("resources")
        )
        self.api = aws_apigateway.RestApi(
            self,
            "API",
            rest_api_name="Bot API Service",
            description="Handles requests from Discord for the bot",
        )
        integration = aws_apigateway.LambdaIntegration(
            self.proxy,
            request_templates={"application/json": '{ "statusCode": "200" }'},
        )
        self.api.root.add_method("POST", integration)
        scope.command_handling.sns_topic.grant_publish(self.proxy)
