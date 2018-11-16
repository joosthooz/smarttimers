#!/usr/bin/env python3

"""SmartTimer

SmartTimer is a cross-platform library for measuring runtime of running
processes using a simple and flexible API.

Classes:

    Timer

Functions:

    custom_time() -> float
"""


import time


__all__ = ['Timer']


def custom_time(*args, **kwargs):
    """Example of a custom time measurement function.

    Note:
        Function can contain arbitrary positional and/or keyword arguments or
        no argments.

    Args:
        args (tuple, optional): Arbitrary positional arguments.
        kwargs (dict, optional): Arbitrary keyword arguments.

    Returns:
        float: Time measured in fractional seconds.
    """
    # Measure time ...
    time_in_some_unit = 0.

    # Convert time to fractional seconds ...
    time_seconds = 0.
    return time_seconds


class Timer:
    """Class for representing a Timer.

    Attributes:
        id (str, optional): Timer identifier.
        seconds (float, optional): Time in fractional seconds.
        minutes (float): Time in fractional minutes (read-only).
        mode (int, optional): Time mode, selectc a time measurement function.
        DEFAULT_TIME_MODE (int): Default time mode.
        TIME_MODES (dict): Map of time modes and time measurement functions.

    Notes:
        * `minutes` is read-only to maintain consistency of time values.

    Register time measurement function, 'custom_time()', to mode value of '5':
        $ Timer.TIME_MODES[5] = custom_time
        or
        $ Timer.TIME_MODES[len(Timer.TIME_MODES)] = custom_time

    Time measurement functions included:
        time.perf_counter():
            Return the value (in fractional seconds) of a performance counter,
            i.e. a clock with the highest available resolution to measure a
            short duration. It does include time elapsed during sleep and is
            system-wide. The reference point of the returned value is
            undefined, so that only the difference between the results of
            consecutive calls is valid. New in version 3.3.

        time.process_time():
            Return the value (in fractional seconds) of the sum of the system
            and user CPU time of the current process. It does not include time
            elapsed during sleep. It is process-wide by definition. The
            reference point of the returned value is undefined, so that only
            the difference between the results of consecutive calls is valid.
            New in version 3.3.

        time.clock():
            On Unix, return the current processor time as a floating point
            number expressed in seconds. The precision, and in fact the very
            definition of the meaning of 'processor time', depends on that of
            the C function of the same name. On Windows, this function returns
            wall-clock seconds elapsed since the first call to this function,
            as a floating point number, based on the Win32 function
            QueryPerformanceCounter(). The resolution is typically better than
            one microsecond. Deprecated since version 3.3: The behaviour of
            this function depends on the platform: use perf_counter() or
            process_time() instead, depending on your requirements, to have a
            well defined behaviour.

        time.monotonic():
            Return the value (in fractional seconds) of a monotonic clock, i.e.
            a clock that cannot go backwards. The clock is not affected by
            system clock updates. The reference point of the returned value is
            undefined, so that only the difference between the results of
            consecutive calls is valid. On Windows versions older than Vista,
            monotonic() detects GetTickCount() integer overflow (32 bits,
            roll-over after 49.7 days). It increases an internal epoch
            (reference time) by 232 each time that an overflow is detected. The
            epoch is stored in the process-local state and so the value of
            monotonic() may be different in two Python processes running for
            more than 49 days. On more recent versions of Windows and on other
            operating systems, monotonic() is system-wide. New in version 3.3.
            Changed in version 3.5: The function is now always available.

        time.time():
            Return the time in seconds since the epoch as a floating point
            number. The specific date of the epoch and the handling of leap
            seconds is platform dependent. On Windows and most Unix systems,
            the epoch is January 1, 1970, 00:00:00 (UTC) and leap seconds are
            not counted towards the time in seconds since the epoch. This is
            commonly referred to as Unix time.

    Todo:
        * Extend to support additional stats besides time (e.g. psutil).
        * Unit tests.
    """

    DEFAULT_TIME_MODE = 0
    TIME_MODES = {
        0: time.perf_counter,
        1: time.process_time,
        2: time.clock,
        3: time.monotonic,
        4: time.time
    }

    def __init__(self, id='', seconds=0., mode=-1):
        """Constructor for Timer class.

        The `seconds` argument is used as the initial time measured.
        The attribute `minutes` is set automatically by the `seconds` setter
        method.
        """
        self.id = id
        self.seconds = seconds
        self.mode = mode

    def show_modes(self):
        """Print available time modes and time measurement functions."""
        for k, v in type(self).TIME_MODES.items():
            print(k,v)
        print("Default mode is {}".format(type(self).DEFAULT_TIME_MODE))
        print("Current mode is {}".format(self.mode))

    @property
    def mode(self):
        """Get or set the time mode.

        The time `mode` indexes the `TIME_MODES` mapping to select a time
        measurement function. If `mode` is set to a negative value then
        `DEFAULT_TIME_MODE` is used.

        To find the timing function that is enabled for a given Timer instance:
            $ t = Timer()
            $ Timer.TIME_MODES[t.mode]
            or
            $ t.show_modes()

        To change the time mode for a Timer:
            $ t = Timer()
            $ t.mode = 3

        Args:
            mode (int): Time mode used to select a time measurement function.

        Returns:
            int: Time mode.

        Raises:
            TypeError: If `mode` is not an integer.
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        if not isinstance(mode, int):
            raise TypeError("Invalid data type for 'mode' attribute, '{}', "
                            "requires an integer.".format(type(mode)))
        self._mode = mode if mode >= 0 else type(self).DEFAULT_TIME_MODE
        self._time_func = type(self).TIME_MODES[self._mode]

    @property
    def id(self):
        """Get or set the Timer identifier.

        Args:
            id (str): Timer identifier.

        Returns:
            str: Timer identifier.

        Raises:
            TypeError: If `id` is not a string.
        """
        return self._id

    @id.setter
    def id(self, id):
        if not isinstance(id, str):
            raise TypeError("Invalid data type for 'id' attribute, '{}', "
                            "requires a string.".format(type(id)))
        self._id = id

    @property
    def seconds(self):
        """Get or set time measured in seconds.

        Setting the time in seconds also updates the time in minutes.
        The setting value has to be numeric and non-negative.

        Args:
            seconds (float): Time in fractional seconds.

        Returns:
            float: Time in seconds.

        Raises:
            TypeError: If `seconds` is not numeric (int or float).
            ValueError: If `seconds` is a negative number.
        """
        return self._seconds

    @seconds.setter
    def seconds(self, seconds):
        if not isinstance(seconds, (int, float)):
            raise TypeError("Invalid data type for 'seconds' attribute, '{}', "
                            "requires a number".format(type(seconds)))
        if seconds < 0.:
            raise ValueError("Invalid value for 'seconds' attribute, '{}', "
                             "requires a non-negative number".format(seconds))
        self._seconds = seconds
        self._minutes = seconds / 60.

    @property
    def minutes(self):
        """Get time measured in minutes.

        Returns:
            float: time in minutes.
        """
        return self._minutes

    def __str__(self):
        """String representation of a Timer.

        Returns:
            str: comma delimited string, format is `seconds`, `minutes`, `id`.
        """
        return "{:.4f}, {:.4f}, {}".format(self.seconds, self.minutes, self.id)

    def time(self, *args, **kwargs):
        """Invoke time measurement function and record measured time.

        Calls timing function currently configured via time `mode`.
        This method accepts arbitrary positional and/or keyword arguments to
        enable support for arbitrary signatures of timing functions.

        Args:
            args (tuple, optional): Positional arguments for time function.
            kwargs (dict, optional): Keyword arguments for time function.

        Returns:
            float: Time measured in fractional seconds.
        """
        self.seconds = self._time_func(*args, **kwargs)
        return self.seconds

    def __sub__(self, other):
        """Compute the absolute time difference of Timer pair.

        The `id` of the resulting Timer contains a combination of the input
        Timer `ids`.

        Args:
            other (:obj:`Timer`): Timer for subtracting its time values.

        Returns:
            :obj:`Timer`: Timer with absolute time difference of Timer pair.

        Raises:
            ValueError: If Timer pair does not have the same time `mode`.
        """
        if self.mode != other.mode:
            raise ValueError("Incompatible Timers, time modes differ")
        new_id = '-'.join(filter(None, [self.id, other.id]))
        return Timer(new_id, abs(self.seconds - other.seconds))

    def __add__(self, other):
        """Compute the time sum of Timer pair.

        The `id` of the resulting Timer contains a combination of the input
        Timer `ids`. Raises a ValueError exception if Timer pair does not have
        the same time `mode`.

        Args:
            other (:obj:`Timer`): Timer for adding its time values.

        Returns:
            :obj:`Timer`: Timer with time sum of Timer pair.

        Raises:
            ValueError: If Timer pair does not have the same time `mode`.
        """
        if self.mode != other.mode:
            raise ValueError("Incompatible Timers, time modes differ")
        new_id = '+'.join(filter(None, [self.id, other.id]))
        return Timer(new_id, self.seconds + other.seconds)
