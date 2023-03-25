from collections import namedtuple
from aws_cdk.aws_dynamodb import AttributeType

_Table = namedtuple(
    "_Table", ["name", "hash_key", "sort_key", "gsi"], defaults=[None, None]
)
_TableGSI = namedtuple("_TableGSI", ["name", "hash_key", "sort_key"], defaults=[None])
_TableAttr = namedtuple("_TableAttr", ["name", "type"])

_user_id = _TableAttr(
    name="user_id",
    type=AttributeType.STRING,
)
_server_id = _TableAttr(
    name="server_id",
    type=AttributeType.STRING,
)

_users_gsi = _TableGSI(
    name="users_by_server_index",
    hash_key=_server_id,
)

_users_table = _Table(
    name="users",
    hash_key=_user_id,
    sort_key=_server_id,
    gsi=_users_gsi,
)
_servers_table = _Table(
    name="servers",
    hash_key=_server_id,
)

table_definitions = [_users_table, _servers_table]
