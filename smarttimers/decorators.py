"""SmartTimer decorators."""


__all__ = [
    'smarttime',
    'decorator_timer'
    ]


from .smarttimer import SmartTimer
from functools import wraps, partial


# Global instance for all decorators
decorator_timer = SmartTimer("Function decorator")


def smarttime(func=None, *, timer=decorator_timer):
    """Measure runtime for functions/methods.

    Args:
        timer (SmartTimer, optional): Instance to use to measure time. If None,
            then global SmartTimer instance, 'decorator_timer', is used.
    """
    if not func:
        return partial(smarttime, timer=timer)

    @wraps(func)
    def wrapper(*args, **kwargs):
        timer.tic(func.__qualname__)
        ret = func(*args, **kwargs)
        timer.toc()
        return ret
    return wrapper
