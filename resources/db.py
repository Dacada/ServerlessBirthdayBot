import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class UsersByServerIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "users_by_server_index"
        projection = AllProjection

    server_id = UnicodeAttribute(hash_key=True)


class Users(Model):
    class Meta:
        table_name = os.environ.get("USERS_TABLE_NAME")
        region = os.environ.get("USERS_TABLE_REGION")

    user_id = UnicodeAttribute(hash_key=True)
    server_id = UnicodeAttribute(range_key=True)
    birthday_day = NumberAttribute(null=True)
    birthday_month = NumberAttribute(null=True)
    wish = UnicodeAttribute(null=True)
    users_by_server_index = UsersByServerIndex()


class Servers(Model):
    class Meta:
        table_name = os.environ.get("SERVERS_TABLE_NAME")
        region = os.environ.get("SERVERS_TABLE_REGION")

    server_id = UnicodeAttribute(hash_key=True)
    channel_id = UnicodeAttribute(null=True)
    greeting = UnicodeAttribute(null=True)
    wish_reminder_enabled = BooleanAttribute(null=True)
    wish_reminder_period = NumberAttribute(null=True)
    wish_reminder_message = UnicodeAttribute(null=True)
