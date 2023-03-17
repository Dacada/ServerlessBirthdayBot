import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_dynamodb


class DataLayer(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.users = aws_dynamodb.Table(
            self,
            "users",
            partition_key=aws_dynamodb.Attribute(
                name="user_id", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="server_id", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        self.servers = aws_dynamodb.Table(
            self,
            "servers",
            partition_key=aws_dynamodb.Attribute(
                name="server_id", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )
