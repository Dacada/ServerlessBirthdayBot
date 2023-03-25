from enum import IntEnum


class TablePermissionType(IntEnum):
    Read = 1
    ReadWrite = 2


perm_r_usr = {
    "users": TablePermissionType.Read,
}
perm_rw_usr = {
    "users": TablePermissionType.ReadWrite,
}
perm_r_srvr = {
    "servers": TablePermissionType.Read,
}
perm_rw_srvr = {
    "servers": TablePermissionType.ReadWrite,
}
