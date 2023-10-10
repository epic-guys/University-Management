from functools import wraps
from typing import Callable, Any


class RoleMixin:
    pass


class RoleException(Exception):
    pass


class RoleManager:
    def __init__(self,
                 role_loader: Callable[[], RoleMixin],
                 default_unauthorized_callback: Callable = None,
                 other_decorator: Callable[[Callable], Any] = None
                 ):
        self.role_loader = role_loader
        self.default_unauthorized_callback = default_unauthorized_callback
        self.other_decorator = other_decorator

    def roles(self, *roles: type[RoleMixin], unauthorized_callback: Callable = None):
        if self.role_loader is None:
            raise RoleException('Role loader not defined')

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if isinstance(self.role_loader(), roles):
                    return func(*args, **kwargs)
                if unauthorized_callback is not None:
                    return unauthorized_callback(*args, **kwargs)
                if self.default_unauthorized_callback is not None:
                    return self.default_unauthorized_callback(*args, **kwargs)

            # Per unire eventualmente altri decoratori
            if self.other_decorator is not None:
                wrapper = self.other_decorator(wrapper)

            return wrapper

        return decorator
