from enum import IntEnum
from collections import namedtuple
from birthday_discord_bot.data.table_permissions import *

_BotCommand = namedtuple(
    "_BotOption", ["name", "table_perms", "subcommands"], defaults=[None, None]
)

_wishing_enable = _BotCommand(
    name="enable",
    table_perms=perm_rw_srvr,
)
_wishing_disable = _BotCommand(
    name="disable",
    table_perms=perm_rw_srvr,
)
_wishing_period = _BotCommand(
    name="period",
    table_perms=perm_rw_srvr,
)
_wishing_reminder = _BotCommand(
    name="reminder",
    table_perms=perm_rw_srvr,
)
_wishing_set = _BotCommand(
    name="set",
    table_perms=perm_rw_usr,
)

_set = _BotCommand(
    name="set",
    table_perms=perm_rw_usr,
)
_get = _BotCommand(
    name="get",
    table_perms=perm_r_usr,
)
_retrieve = _BotCommand(
    name="retrieve",
    table_perms=perm_r_usr,
)
_channel = _BotCommand(
    name="channel",
    table_perms=perm_rw_srvr,
)
_greeting = _BotCommand(
    name="greeting",
    table_perms=perm_rw_srvr,
)
_wishing = _BotCommand(
    name="wishing",
    subcommands=[
        _wishing_enable,
        _wishing_disable,
        _wishing_period,
        _wishing_reminder,
        _wishing_set,
    ],
)
_status = _BotCommand(
    name="status",
    table_perms=perm_r_srvr,
)

commands = [_set, _get, _retrieve, _channel, _greeting, _wishing, _status]
