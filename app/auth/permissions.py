from functools import wraps

from flask import abort
from flask_login import current_user


def roles_permitidas(*roles):
    """
    Permite acesso somente aos perfis informados.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(401)

            if not current_user.ativo:
                abort(403)

            if current_user.tipo_usuario not in roles:
                abort(403)

            return func(*args, **kwargs)

        return wrapper

    return decorator