"""SmartTimer decorators."""


__all__ = [
    'smarttime',
    'decorator_timer'
    ]


from .smarttimer import SmartTimer
from functools import wraps, partial


# Global instance for all decorators
decorator_timer = SmartTimer("Function decorator")


def smarttime(func=None, *, timer=None):
    """Measure runtime for functions/methods.

    Args:
        timer (SmartTimer, optional): Instance to use to measure time. If None,
            then global SmartTimer instance, *_timer*, is used.
    """
    if not timer:
        timer = decorator_timer
    if not func:
        return partial(time, timer=timer)

    @wraps(func)
    def wrapper(*args, **kwargs):
        timer.tic(func.__qualname__)
        ret = func(*args, **kwargs)
        timer.toc()
        return ret
    return wrapper
