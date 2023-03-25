from collections import namedtuple
from birthday_discord_bot.data.table_permissions import *

_Task = namedtuple("_Task", ["name", "table_perms"])

_reminder = _Task(name="reminder", table_perms={**perm_rw_usr, **perm_r_srvr})
_greeting = _Task(name="greeting", table_perms={**perm_rw_usr, **perm_r_srvr})
_cleanup = _Task(name="cleanup", table_perms={**perm_rw_usr, **perm_r_srvr})

periodic_tasks = [_reminder, _greeting, _cleanup]
