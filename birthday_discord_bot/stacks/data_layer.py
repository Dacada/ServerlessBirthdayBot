from aws_cdk import Stack, aws_dynamodb
from constructs import Construct
from birthday_discord_bot.data import table_definitions


class DataLayer(Stack):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.tables = {}
        for table in table_definitions:
            args = {}
            args["partition_key"] = aws_dynamodb.Attribute(
                name=table.hash_key.name, type=table.hash_key.type
            )
            if table.sort_key is not None:
                args["sort_key"] = aws_dynamodb.Attribute(
                    name=table.sort_key.name, type=table.sort_key.type
                )

            dyndb_table = aws_dynamodb.Table(
                self,
                table.name,
                billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
                **args
            )

            if table.gsi is not None:
                gsi_args = {}
                gsi_args["partition_key"] = aws_dynamodb.Attribute(
                    name=table.gsi.hash_key.name, type=table.gsi.hash_key.type
                )
                if table.gsi.sort_key is not None:
                    gsi_args["sort_key"] = aws_dynamodb.Attribute(
                        name=table.gsi.sort_key.name, type=table.gsi.sort_key.type
                    )

                dyndb_table.add_global_secondary_index(
                    index_name=table.gsi.name, **gsi_args
                )

            self.tables[table.name] = dyndb_table
