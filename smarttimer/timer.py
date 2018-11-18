#!/usr/bin/env python3

"""Utilities to measure time from system and custom clocks/counters.

Classes:
    * Timer

Todo:
    * Extend to support additional stats besides time (e.g. psutil).
    * Support timings in concurrent processes.
    * Unit tests.
"""


import time


__all__ = ['Timer']


class ClockInfo:
    """Store clock information."""
    def __init__(self, **kwargs):
        self.adjustable = kwargs.get('adjustable', None)
        self.implementation = kwargs.get('implementation', None)
        self.resolution = kwargs.get('resolution', None)
        self.monotonic = kwargs.get('monotonic', None)


class Timer:
    """Read current time from a clock/counter.

    .. _time: https://docs.python.org/3/library/time.html

    A :py:class:`Timer` allows recording the current time measured by a
    registered timing function. Time is recorded in fractional seconds and
    fractional minutes. :py:class:`Timer` supports addition, difference, and
    logical operators. :py:class:`Timer` uses a simple and extensible API
    which allows registering new timing functions.

    Note:
        New timing functions need to have a compliant interface. If a user
        wants to register a non-compliant timing function, a compliant wrapper
        function can be used. The default timing functions are built-ins from
        the standard time_ library.

    Args:
        id (str): Label identifier. Default is empty string.
        seconds (float): Time in fractional seconds. Default is 0.0.
        clock_name (str): Clock name used to select a time measurement
            function. Default is empty string.

    Example::

        # Find the current time function of a Timer
        >>> t1 = Timer('timer 1')
        >>> Timer.CLOCKS[t1.mode]
        # or
        >>> Timer.print_clocks()
        >>> t1.clock_name

        # Change current time function
        >>> t1.clock_name = 'process_time'

        # Record a time measurement
        >>> t1.time()

        # Create another Timer
        >>> t2 = Timer('timer 2')
        >>> t2.time()

        # Add/subtract Timers
        >>> t3 = t1 + t2
        >>> t4 = t2 - t1

        # Compare Timers
        >>> t1 == t2  # False
        >>> t2 > t1   # True
        >>> t1 <= t2  # True
   """

    DEFAULT_CLOCK_NAME = 'perf_counter'
    """str: Default clock name, used when :py:attr:`clock_name` is empty
    string."""

    CLOCKS = {
        'perf_counter': time.perf_counter,
        'process_time': time.process_time,
        'clock': time.clock,
        'monotonic': time.monotonic,
        'time': time.time
    }
    """dict of str -> func: Map between clock name and time measurement
    functions.

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

    Registering a new time measurement function
        A timing function is compliant if it returns a time measured in
        fractional seconds. The function can contain arbitrary positional
        and/or keyword arguments or no arguments.

        Example::

            def custom_time_function(*args, **kwargs):
                # Measure time
                time_in_some_unit = ...

                # Convert time to fractional seconds
                time_seconds = time_in_some_unit ...
                return time_seconds

            # Register custom_time_function() with clock name 'custom_time'
            >>> Timer.CLOCKS['custom_time'] = custom_time_function

    Warning:
        When registering a new timing function to :py:attr:`CLOCKS`, it is
        recommended to use a unique clock name to prevent overwriting over an
        existing one.
    """

    def __init__(self, id='', **kwargs):
        self.id = id
        self.seconds = kwargs.get('seconds', 0.)
        self.clock_name = kwargs.get('clock_name', '')

    def __str__(self):
        """String representation.

        If :py:attr:`id` is not empty string, then format is
        ':py:attr:`seconds`, :py:attr:`minutes`, :py:attr:`id`'. Otherwise,
        :py:attr:`id` is ignored.

        Returns:
            str: Comma delimited string.
        """
        if self.id:
            return "{:>10.4f}, {:>10.4f}, {:>10}".format(self.seconds,
                                                         self.minutes,
                                                         self.id)
        else:
            return "{:>10.4f}, {:>10.4f}".format(self.seconds, self.minutes)

    def __add__(self, other):
        return type(self).add(self, other)

    def __sub__(self, other):
        return type(self).diff(self, other)

    def __eq__(self, other):
        type(self).compatibility_test(self, other)
        return self.seconds == other.seconds

    def __lt__(self, other):
        type(self).compatibility_test(self, other)
        return self.seconds < other.seconds

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    @property
    def id(self):
        """str: Label identifier.

        Raises:
            TypeError: If not a string.
        """
        return self._id

    @id.setter
    def id(self, id):
        if not isinstance(id, str):
            raise TypeError("Invalid type for 'id' attribute, '{}', requires "
                            "a string.".format(type(id)))
        self._id = id

    @property
    def seconds(self):
        """float: Time measured in seconds.

        Raises:
            TypeError: If not numeric (*int* or *float*).
            ValueError: If negative number.
        """
        return self._seconds

    @seconds.setter
    def seconds(self, seconds):
        if not isinstance(seconds, (int, float)):
            raise TypeError("Invalid type for 'seconds' attribute, '{}', "
                            "requires a number".format(type(seconds)))
        if seconds < 0.:
            raise ValueError("Invalid value for 'seconds' attribute, '{}', "
                             "requires a non-negative number".format(seconds))
        self._seconds = float(seconds)
        self._minutes = seconds / 60.

    @property
    def minutes(self):
        """float: Time measured in minutes (read-only).

        Automatically set when :py:attr:`seconds` is modified. This ensures
        consistency between time values.
        """
        return self._minutes

    @property
    def clock_name(self):
        """str: Clock name used to select a timing function.

        Indexes the :py:attr:`CLOCKS` map to select a time function. If
        :py:attr:`clock_name` is set to the empty string then
        :py:attr:`DEFAULT_CLOCK_NAME` is used.

        Raises:
            TypeError: If not a string.
        """
        return self._clock_name

    @clock_name.setter
    def clock_name(self, clock_name):
        if not isinstance(clock_name, str):
            raise TypeError("Invalid type for 'clock_name' attribute, '{}', "
                            "requires a string.".format(type(clock_name)))
        self._clock_name = clock_name if clock_name \
            else type(self).DEFAULT_CLOCK_NAME
        self._clock = type(self).CLOCKS[self._clock_name]

    def time(self, *args, **kwargs):
        """Invoke time measurement function and record measured time.

        Calls timing function currently configured via :py:attr:`clock_name`.
        This method accepts arbitrary positional and/or keyword arguments to
        enable support for arbitrary signatures of timing functions.

        Args:
            args (tuple, optional): Positional arguments for time function.
            kwargs (dict, optional): Keyword arguments for time function.

        Returns:
            float: Time measured in fractional seconds.
        """
        self.seconds = self._clock(*args, **kwargs)
        return self.seconds

    @classmethod
    def print_clocks(cls):
        """Print info of available clocks.

        For :py:attr:`clock_name` that can be queried with
        :py:meth:`time.get_clock_info`, detailed attributes are printed. All
        other cases only print the corresponding timing function.
        """
        for n, f in cls.CLOCKS.items():
            try:
                info = time.get_clock_info(n)
            except (TypeError, ValueError):
                info = ClockInfo(implementation=f.__name__ + '()')

            print("{name}:\n"
                  "   function      : {func}\n"
                  "   adjustable    : {info.adjustable}\n"
                  "   implementation: {info.implementation}\n"
                  "   monotonic     : {info.monotonic}\n"
                  "   resolution    : {info.resolution}\n"
                  .format(name=n, func=f, info=info))

        print("Default clock is {}".format(cls.DEFAULT_CLOCK_NAME))

    @classmethod
    def are_compatible(cls, t1, t2):
        """Return truth of compatibility between a :py:class:`Timer` pair.

        For :py:attr:`clock_name` that can be queried with
        :py:meth:`time.get_clock_info`, compatibility requires that all
        attributes are identical. All other cases require that the timing
        functions are the same function.

        Args:
            t1 (Timer): First :py:class:`Timer`.
            t2 (Timer): Second :py:class:`Timer`.

        Returns:
            bool: True if :py:class:`Timer` pair is compatible, else False
        """
        try:
            return time.get_clock_info(t1.clock_name) == \
                       time.get_clock_info(t2.clock_name)
        except (TypeError, ValueError):
            return cls.CLOCKS[t1.clock_name] is cls.CLOCKS[t2.clock_name]

    @classmethod
    def compatibility_test(cls, t1, t2):
        """Check compatibility between a :py:class:`Timer` pair.

        Args:
            t1 (Timer): First :py:class:`Timer`.
            t2 (Timer): Second :py:class:`Timer`.

        Raises:
            ValueError: If :py:class:`Timer` pair is not compatible.
        """
        if not cls.are_compatible(t1, t2):
            raise ValueError("Incompatible Timers, time modes differ")
        pass

    @classmethod
    def add(cls, t1, t2):
        """Sum the times of a :py:class:`Timer` pair.

        The :py:attr:`id` of the resulting :py:class:`Timer` contains a
        combination of the input :py:class:`Timer` :py:attr:`id`. The addition
        operator is an alias to :py:meth:`add`.

        **Example**::

            >>> dt = Timer.add(t1, t2)
            # or
            >>> dt = t1 + t2
            # or
            >>> dt = t2 + t1

        Args:
            t1 (Timer): First :py:class:`Timer`.
            t2 (Timer): Second :py:class:`Timer`.

        Returns:
            Timer: :py:class:`Timer` with time sum.
        """
        cls.compatibility_test(t1, t2)
        new_id = '+'.join(filter(None, [t1.id, t2.id]))
        return Timer(new_id, seconds=t1.seconds + t2.seconds)

    @classmethod
    def diff(cls, t1, t2):
        """Compute the absolute time difference of a :py:class:`Timer` pair.

        The :py:attr:`id` of the resulting :py:class:`Timer` contains a
        combination of the input :py:class:`Timer` :py:attr:`id`. The subtract
        operator is an alias to :py:meth:`diff`.

        **Example**::

            >>> dt = Timer.diff(t1, t2)
            # or
            >>> dt = t2 - t1
            # or
            >>> dt = t1 - t2

        Args:
            t1 (Timer): First :py:class:`Timer`.
            t2 (Timer): Second :py:class:`Timer`.

        Returns:
            Timer: :py:class:`Timer` with absolute time difference.
        """
        cls.compatibility_test(t1, t2)
        new_id = '-'.join(filter(None, [t1.id, t2.id]))
        return Timer(new_id, seconds=abs(t1.seconds - t2.seconds))
