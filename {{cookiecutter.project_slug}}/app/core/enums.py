from enum import Enum


class UserPermissionEnum(str, Enum):
    """The UserPermissionEnum class defines the user permission types.

    Args:
        str (_type_): The user permission type.
        Enum (_type_): The user permission enum type.
    """

    ADMINISTRATOR = "Administrator"
    USER = "User"
