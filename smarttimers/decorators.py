"""SmartTimer decorators

Functions:
    :func:`time`
"""


from functools import (partial, wraps)
from .smarttimer import SmartTimer


__all__ = ['time']


# Global instance for all decorators
_timer = SmartTimer('SmartTimer Decorator')


def time(func=None, *, timer=None):
    """Measure runtime for functions/methods.

    Args:
        timer (SmartTimer, optional): Instance to use to measure time. If None,
            then global SmartTimer instance, *_timer*, is used.
    """
    if timer is None:
        timer = _timer
    if func is None:
        return partial(time, timer=timer)

    @wraps(func)
    def wrapper(*args, **kwargs):
        timer.tic(func.__qualname__)
        ret = func(*args, **kwargs)
        timer.toc()
        return ret
    return wrapper
