from functools import wraps
from typing import Callable


class Role:
    pass


class RoleException(Exception):
    pass


class RoleManager:
    def __init__(self, role_loader: Callable[[], Role] = None, default_unauthorized_callback: Callable = None):
        self.role_loader = role_loader
        self.default_unauthorized_callback = default_unauthorized_callback

    def set_role_loader(self, role_loader: Callable[[], Role]):
        self.role_loader = role_loader

    def set_default_unauthorized_callback(self, default_unauthorized_callback: Callable = None):
        self.default_unauthorized_callback = default_unauthorized_callback

    def roles(self, *roles: type[Role], unauthorized_callback: Callable = None):
        if self.role_loader is None:
            raise RoleException('Role loader not defined, use set_role_loader to define one')

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if isinstance(self.role_loader(), roles):
                    return func(*args, *kwargs)
                if unauthorized_callback is not None:
                    return unauthorized_callback(*args, **kwargs)

            return wrapper

        return decorator
