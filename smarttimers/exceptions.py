"""Exceptions for timing utilities.

Classes:
    * :py:class:`TimerCompatibilityError`
    * :py:class:`TimerError`
    * :py:class:`TimerKeyError`
    * :py:class:`TimerTypeError`
    * :py:class:`TimerValueError`
"""


__all__ = ['TimerCompatibilityError', 'TimerError', 'TimerKeyError',
           'TimerTypeError', 'TimerValueError']


class TimerError(Exception):
    """Base exception for invalid data in :py:class:`Timer`."""
    pass


class TimerCompatibilityError(TimerError):
    """Exception for incompatible :py:class:`Timer` instances."""
    pass


class TimerKeyError(TimerError):
    """Exception for invalid key indexing in :py:class:`TimerDict`."""
    pass


class TimerTypeError(TimerError):
    """Exception for invalid data type assigment in :py:class:`Timer`."""
    pass


class TimerValueError(TimerError):
    """Exception for invalid values in :py:class:`Timer`."""
    pass
