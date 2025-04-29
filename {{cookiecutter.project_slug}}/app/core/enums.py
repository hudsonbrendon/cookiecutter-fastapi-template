from enum import Enum


class EnumPermissaoUsuario(str, Enum):
    """A classe EnumPermissaoUsuario define os tipos de permissão do usuário.

    Args:
        str (_type_): O tipo de permissão do usuário.
        Enum (_type_): O tipo de enumeração de permissão do usuário.
    """

    ADMINISTRADOR = "Administrador"
    USUARIO = "Usuario"
