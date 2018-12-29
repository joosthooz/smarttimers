"""SmartTimer decorators

Functions:
    :func:`time`
"""


__all__ = ['time', '_timer']


from functools import (partial, wraps)
from .smarttimer import SmartTimer


# Global instance for all decorators
_timer = SmartTimer('Function decorator')


def time(func=None, *, timer=None):
    """Measure runtime for functions/methods.

    Args:
        timer (SmartTimer, optional): Instance to use to measure time. If None,
            then global SmartTimer instance, *_timer*, is used.
    """
    if not timer:
        timer = _timer
    if not func:
        return partial(time, timer=timer)

    @wraps(func)
    def wrapper(*args, **kwargs):
        timer.tic(func.__qualname__)
        ret = func(*args, **kwargs)
        timer.toc()
        return ret
    return wrapper
