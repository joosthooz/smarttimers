#!/usr/bin/env python3

"""Utilities to measure time from system and custom clocks/counters.

Classes:
    * Timer
"""


import time


__all__ = ['Timer']


class Timer:
    """Class to read current time from a supported clock/counter.

    .. _time: https://docs.python.org/3/library/time.html

    A Timer allows reading the current time given by a registered timing
    function. Time is recorded in seconds and minutes along with an optional
    label. Default timing functions are from the time_ standard library module.
    Timer uses a simple and extensible API to allow registering new and custom
    timing functions (interface needs to be compliant). If a user wants to
    register a non-compliant timing function, a wrapper function can be used to
    fulfill interface requirements.

    Attributes:
        id (str, optional): Timer identifier.
        seconds (float, optional): Time in fractional seconds.
        minutes (float): Time in fractional minutes (read-only).
        mode (int, optional): Time mode used to index **TIME_MODES** map to
                              select a time measurement function.
        DEFAULT_TIME_MODE (int): Default time mode.
        TIME_MODES (dict of int -> function): Map of time modes and time
                                              measurement functions.

    Note:
        * **minutes** is read-only and set automatically when **seconds** is
          modified. This ensures consistency between time values.
        * When registering a new timing function, the user has freedom of which
          time mode to use (add new mode value or overwrite an existing mode).

    Todo:
        * Fix attributes and property documentation, attributes appear twice.
        * Order class methods.
        * Add documentation on support of logical operators for Timers.
        * Extend to support additional stats besides time (e.g. psutil).
        * Support timings in concurrent processes.
        * Unit tests.

    .. _`time.perf_counter()`:
        https://docs.python.org/3/library/time.html#time.perf_counter
    .. _`time.process_time()`:
        https://docs.python.org/3/library/time.html#time.process_time
    .. _`time.clock()`:
        https://docs.python.org/3/library/time.html#time.clock
    .. _`time.monotonic()`:
        https://docs.python.org/3/library/time.html#time.monotonic
    .. _`time.time()`:
        https://docs.python.org/3/library/time.html#time.time

    Time measurement functions
        * `time.perf_counter()`_
        * `time.process_time()`_
        * `time.clock()`_
        * `time.monotonic()`_
        * `time.time()`_

    Custom time measurement function
        A timing function is compliant if it returns a time measured in
        fractional seconds. The function can contain arbitrary positional
        and/or keyword arguments or no arguments.

        **Example**::

            def custom_time_function(*args, **kwargs):
                # Measure time ...
                time_in_some_unit = 0.

                # Convert time to fractional seconds ...
                time_seconds = 0.
                return time_seconds

            # Register custom_time_function() to mode 5
            >>> Timer.TIME_MODES[5] = custom_time_function
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

        The **seconds** argument is used as the initial time measured.
        The attribute **minutes** is set automatically by the **seconds** setter
        method.
        """
        self.id = id
        self.seconds = seconds
        self.mode = mode

    @classmethod
    def show_modes(cls):
        """Print available time modes and time measurement functions."""
        for k, v in cls.TIME_MODES.items():
            print(k,v)
        print("Default mode is {}".format(cls.DEFAULT_TIME_MODE))

    @property
    def mode(self):
        """Get or set the time mode.

        The time **mode** indexes the **TIME_MODES** mapping to select a time
        measurement function. If **mode** is set to a negative value then
        **DEFAULT_TIME_MODE** is used.

        **Example**::

            # Find the timing function of a Timer
            >>> t = Timer()
            >>> Timer.TIME_MODES[t.mode]
            # or
            >>> Timer.show_modes()
            >>> t.mode

            # Change the time mode of a Timer
            >>> t = Timer()
            >>> t.mode = 3

        Args:
            mode (int): Time mode used to select a time measurement function.

        Returns:
            int: Time mode.

        Raises:
            TypeError: If **mode** is not an integer.
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
            TypeError: If **id** is not a string.
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
            TypeError: If **seconds** is not numeric (*int* or *float*).
            ValueError: If **seconds** is a negative number.
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
            float: Time in minutes.
        """
        return self._minutes

    def __str__(self):
        """String representation of a Timer.

        Returns:
            str: comma delimited string, format is **seconds**, **minutes**,
                 **id**.
        """
        return "{:.4f}, {:.4f}, {}".format(self.seconds, self.minutes, self.id)

    def time(self, *args, **kwargs):
        """Invoke time measurement function and record measured time.

        Calls timing function currently configured via time **mode**.
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

    @classmethod
    def are_compatible(cls, t1, t2):
        """Check if Timer pair use the same timing function.

        Args:
            t1 (Timer): First Timer.
            t2 (Timer): Second Timer.

        Returns:
            bool: True if Timer pair are compatible, else False
        """
        return cls.TIME_MODES[t1.mode] is cls.TIME_MODES[t2.mode]

    @classmethod
    def compatibility_test(cls, t1, t2):
        """Check if Timer pair use the same timing function.

        Args:
            t1 (Timer): First Timer.
            t2 (Timer): Second Timer.

        Raises:
            ValueError: If timing function differs between Timer pair.
        """
        if not cls.are_compatible(t1, t2):
            raise ValueError("Incompatible Timers, time modes differ")
        pass

    @classmethod
    def diff(cls, t1, t2):
        """Compute the absolute time difference of Timer pair.

        The **id** of the resulting Timer contains a combination of the input
        Timer **ids**. The subtract operator is an alias to **diff**.

        **Example**::

            >>> dt = Timer.diff(t1, t2)
            # or
            >>> dt = t2 - t1
            # or
            >>> dt = t1 - t2

        Args:
            t1 (Timer): First Timer.
            t2 (Timer): Second Timer.

        Returns:
            Timer: Timer with absolute time difference of Timer pair.

        Raises:
            ValueError: If Timer pair are not compatible.
        """
        cls.compatibility_test(t1, t2)
        new_id = '-'.join(filter(None, [t1.id, t2.id]))
        return Timer(new_id, abs(t1.seconds - t2.seconds))

    @classmethod
    def add(cls, t1, t2):
        """Sums the times of Timer pair.

        The **id** of the resulting Timer contains a combination of the input
        Timer **ids**. The addition operator is an alias to **add**.

        **Example**::

            >>> dt = Timer.add(t1, t2)
            # or
            >>> dt = t1 + t2
            # or
            >>> dt = t2 + t1

        Args:
            t1 (Timer): First Timer.
            t2 (Timer): Second Timer.

        Returns:
            Timer: Timer with time sum of Timer pair.

        Raises:
            ValueError: If Timer pair are not compatible.
        """
        cls.compatibility_test(t1, t2)
        new_id = '+'.join(filter(None, [t1.id, t2.id]))
        return Timer(new_id, t1.seconds + t2.seconds)

    def __add__(self, other):
        """See **add()** method."""
        return type(self).add(self, other)

    def __sub__(self, other):
        """See **diff()** method."""
        return type(self).diff(self, other)

    def __eq__(self, other):
        """Equality operator.

        By default **__ne__()** inverts this result.
        """
        type(self).compatibility_test(self, other)
        return self.seconds == other.seconds

    def __lt__(self, other):
        """Less than."""
        type(self).compatibility_test(self, other)
        return self.seconds < other.seconds

    def __le__(self, other):
        """Less than or equal."""
        return self < other or self == other

    def __gt__(self, other):
        """Greater than."""
        return not (self <= other)

    def __ge__(self, other):
        """Greater than or equal."""
        return not (self < other)
