"""SmartTimers custom exceptions.

Classes:
    * :py:class:`TimerCompatibilityError`
    * :py:class:`TimerError`
"""


__all__ = ['TimerCompatibilityError', 'TimerError']


class TimerError(Exception):
    """Base exception for :py:class:`Timer`."""
    pass


class TimerCompatibilityError(TimerError):
    """Exception for incompatible :py:class:`Timer` instances."""
    pass
