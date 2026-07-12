from functools import wraps
from typing import Callable


def require_graph(error_message: str = "Граф не создан") -> Callable:
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._graph is None:
                raise ValueError(error_message)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
