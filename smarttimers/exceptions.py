"""SmartTimers custom exceptions.

Classes:
    * :py:class:`TimerError`
    * :py:class:`TimerCompatibilityError`
"""


__all__ = ['TimerError', 'TimerCompatibilityError']


class TimerError(Exception):
    """Base exception for :py:class:`Timer`."""
    pass


class TimerCompatibilityError(TimerError):
    """Exception for incompatible :py:class:`Timer` instances."""
    def __init__(self, msg="incompatible clocks"):
        super().__init__(msg)
