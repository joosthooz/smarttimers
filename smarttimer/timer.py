#!/usr/bin/env python3

"""Utilities to measure time from system and custom clocks/counters.

Classes:
    * Timer
"""


import time


__all__ = ['Timer']


class ClockInfo:
    def __init__(self, **kwargs):
        self.adjustable = kwargs.get('adjustable', None)
        self.implementation = kwargs.get('implementation', None)
        self.resolution = kwargs.get('resolution', None)
        self.monotonic = kwargs.get('monotonic', None)


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
        seconds (float, optional): Time measured in fractional seconds.
        minutes (float, read-only): Time measured in fractional minutes.
        clock_name (str, optional): Clock name used to index the **CLOCKS**
                                    map to select a time measurement function.
        DEFAULT_CLOCK_NAME (str): Default clock name.
        CLOCKS (dict of str -> func): Map of clock names and time measurement
                                      functions.

    Note:
        * **minutes** is read-only and set automatically when **seconds** is
          modified. This ensures consistency between timing values.
        * When registering a new timing function to **CLOCKS**, it is
          recommended to use a unique clock name to prevent overwriting over an
          existing one.

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
                # Measure time
                time_in_some_unit = ...

                # Convert time to fractional seconds
                time_seconds = time_in_some_unit ...
                return time_seconds

            # Register custom_time_function() with clock name 'custom_time'
            >>> Timer.CLOCKS['custom_time'] = custom_time_function
    """

    DEFAULT_CLOCK_NAME = 'perf_counter'
    CLOCKS = {
        'perf_counter': time.perf_counter,
        'process_time': time.process_time,
        'clock': time.clock,
        'monotonic': time.monotonic,
        'time': time.time
    }

    def __init__(self, id='', **kwargs):
        """Constructor for Timer class.

        The **seconds** argument is used as the initial time measured.
        The attribute **minutes** is set automatically by the **seconds**
        setter method.
        """
        self.id = id
        self.seconds = kwargs.get('seconds', 0.)
        self.clock_name = kwargs.get('clock_name', '')

    @classmethod
    def show_clocks(cls):
        """Print info of available clocks.

        For **clock_names** that can be queried with *time.get_clock_info*,
        detailed attributes are printed. All other cases only print the
        corresponding timing function.
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

    @property
    def clock_name(self):
        """Get or set the clock name.

        **clock_name** indexes the **CLOCKS** map to select a time measurement
        function. If **clock_name** is set to the empty string then
        **DEFAULT_CLOCK_NAME** is used.

        **Example**::

            # Find the timing function of a Timer
            >>> t = Timer()
            >>> Timer.CLOCKS[t.mode]
            # or
            >>> Timer.show_clocks()
            >>> t.clock_name

            # Change the current clock of a Timer
            >>> t = Timer()
            >>> t.clock_name = 'process_time'

        Args:
            clock_name (str): Clock name used to select a timing function.

        Returns:
            str: Current clock name.

        Raises:
            TypeError: If **clock_name** is not a string.
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
            raise TypeError("Invalid type for 'id' attribute, '{}', requires "
                            "a string.".format(type(id)))
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
            raise TypeError("Invalid type for 'seconds' attribute, '{}', "
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
            str: Comma delimited string, format is **seconds**, **minutes**,
                 **id**. If **id** is empty it is ignored.
        """
        if self.id:
            return "{:>10.4f}, {:>10.4f}, {:>10}".format(self.seconds,
                                                         self.minutes,
                                                         self.id)
        else:
            return "{:>10.4f}, {:>10.4f}".format(self.seconds, self.minutes)

    def time(self, *args, **kwargs):
        """Invoke time measurement function and record measured time.

        Calls timing function currently configured via **clock_name**.
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
    def are_compatible(cls, t1, t2):
        """Check if Timer pair have same attributes.

        For **clock_names** that can be queried with *time.get_clock_info*,
        compatibility requires that all attributes are identical. All other
        cases require that the timing functions are the same function.

        Args:
            t1 (Timer): First Timer.
            t2 (Timer): Second Timer.

        Returns:
            bool: True if Timer pair are compatible, else False
        """
        try:
            return time.get_clock_info(t1.clock_name) == \
                       time.get_clock_info(t2.clock_name)
        except (TypeError, ValueError):
            return cls.CLOCKS[t1.clock_name] is cls.CLOCKS[t2.clock_name]

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
        return Timer(new_id, seconds=abs(t1.seconds - t2.seconds))

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
        return Timer(new_id, seconds=t1.seconds + t2.seconds)

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
