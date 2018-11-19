"""Utilities to measure time from system and custom clocks/counters.

Classes:
    * Timer
    * TimerDict

Todo:
    * Extend to support additional stats besides time (e.g. psutil).
    * Support timing concurrent processes, use time.thread_time() from Python
      3.7?
    * Complete unit tests.
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


class TimerDict(dict):
    """Map between label identifier and callable entity.

        Raises:
            TypeError: If key is not a string.
            TypeError: If value is not a callable entity.
    """
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Invalid type for '{}' attribute, "
                            "{}, requires a string"
                            .format(self.__class__.__name__, key))
        if not callable(value):
            raise TypeError("Invalid type for {}['{}'] attribute, '{}', "
                            "requires a callable entity"
                            .format(self.__class__.__name__, key, value))
        super(type(self), self).__setitem__(key, value)


class MetaTimerProperty(type):
    """Metaclass for Timer class variables."""
    @property
    def DEFAULT_CLOCK_NAME(cls):
        return cls._DEFAULT_CLOCK_NAME

    @DEFAULT_CLOCK_NAME.setter
    def DEFAULT_CLOCK_NAME(cls, value):
        if not isinstance(value, str):
            raise TypeError("Invalid type for 'DEFAULT_CLOCK_NAME' attribute, "
                            "{}, requires a string".format(value))
        cls._DEFAULT_CLOCK_NAME = value

    @property
    def CLOCKS(cls):
        return cls._CLOCKS

    @CLOCKS.setter
    def CLOCKS(cls, value):
        if not isinstance(value, TimerDict):
            raise TypeError("Invalid type for 'CLOCKS' attribute, {}, "
                            "requires a dictionary".format(value))
        cls._CLOCKS = value


class Timer(metaclass=MetaTimerProperty):
    """Read current time from a clock/counter.

    Args:
        id (str): Label identifier. Default is empty string.

        seconds (float): Time measured in fractional seconds. Default is 0.0.

        clock_name (str): Clock name used to select a time measurement
            function. Default is empty string.

    A :py:class:`Timer` allows recording the current time measured by a
    registered timing function. Time is recorded in fractional seconds and
    fractional minutes. :py:class:`Timer` supports addition, difference, and
    logical operators. :py:class:`Timer` uses a simple and extensible API which
    allows registering new timing functions. A timing function is compliant if
    it returns a time measured in fractional seconds. The function can contain
    arbitrary positional and/or keyword arguments or no arguments.

    .. literalinclude:: ../examples/timer_example.py
        :language: python
        :linenos:
        :name: Timer_API
        :caption: Timer API examples.

    .. _`time.get_clock_info`:
        https://docs.python.org/3/library/time.html#time.get_clock_info
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

    Available time measurement functions in :py:attr:`CLOCKS`
        * 'perf_counter' -> `time.perf_counter()`_
        * 'process_time' -> `time.process_time()`_
        * 'clock'        -> `time.clock()`_
        * 'monotonic'    -> `time.monotonic()`_
        * 'time'         -> `time.time()`_

    .. code-block:: python
        :emphasize-lines: 9,10
        :name: register_time_function
        :caption: Registering a new time measurement function.

        def custom_time_function(*args, **kwargs):
            # Measure time
            time_in_some_unit = ...

            # Convert time to fractional seconds
            time_seconds = time_in_some_unit ...
            return time_seconds

        # Register custom_time_function() as 'custom_time'
        Timer.CLOCKS['custom_time'] = custom_time_function

    .. _`time`: https://docs.python.org/3/library/time.html

    Note:
        * New timing functions need to have a compliant interface. If a user
          wants to register a non-compliant timing function, a compliant
          wrapper function can be used. The available timing functions are
          built-ins from the standard `time`_ library.
        * Only Timers with compatible clocks support arithmetic and logical
          operators.

    Warning:
        When registering a new timing function to :py:attr:`CLOCKS`, it is
        recommended to use a unique clock name to prevent overwriting over an
        existing one.

    Attributes:
        DEFAULT_CLOCK_NAME (str): Default clock name, used when
            :py:attr:`clock_name` is empty string.

        CLOCKS (:py:class:`TimerDict` of str -> func): Map between clock name
            and time measurement functions.

            Raises:
                TypeError: If not a :py:class:`TimerDict`.

        id (str): Label identifier.

            Raises:
                TypeError: If not a string.

        seconds (float): Time measured in fractional seconds.

            Automatically sets :py:attr:`minutes` when is modified. This
            ensures consistency between recorded times.

            Raises:
                TypeError: If not numeric (*int* or *float*).
                ValueError: If negative number.

        minutes (float): Time measured in minutes (read-only).

            Automatically set when :py:attr:`seconds` is modified. This ensures
            consistency between recorded times.

        clock_name (str): Clock name used to select a time measurement
            function.

            Indexes the :py:attr:`CLOCKS` map to select a time function. If
            set to the empty string then :py:attr:`DEFAULT_CLOCK_NAME` is used.
            When set to a new clock name, the current time (:py:attr:`seconds`
            and :py:attr:`minutes`) are set to 0.0.

            Raises:
                TypeError: If not a string.
   """

    _DEFAULT_CLOCK_NAME = 'perf_counter'

    _CLOCKS = TimerDict({
        'perf_counter': time.perf_counter,
        'process_time': time.process_time,
        'clock': time.clock,
        'monotonic': time.monotonic,
        'time': time.time
    })

    def __init__(self, id='', **kwargs):
        # Create attributes before invoking properties
        self._id = None
        self._seconds = None
        self._minutes = None
        self._clock_name = None

        # Initialize via properties
        self.id = id
        self.seconds = kwargs.get('seconds', 0.)
        self.clock_name = kwargs.get('clock_name', '')

    def __repr__(self):
        """string representation.

        if :py:attr:`id` is not empty string, then format is
        ':py:attr:`seconds`, :py:attr:`minutes`, :py:attr:`id`'. otherwise,
        :py:attr:`id` is ignored.

        returns:
            str: comma delimited string.
        """
        if self.id:
            return "{:>12.6f}, {:>12.6f}, {:>12}".format(self.seconds,
                                                         self.minutes,
                                                         self.id)
        else:
            return "{:>12.6f}, {:>12.6f}".format(self.seconds, self.minutes)

    def __str__(self):
        return repr(self)

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
        return self._id

    @id.setter
    def id(self, id):
        if not isinstance(id, str):
            raise TypeError("Invalid type for 'id' attribute, '{}', requires "
                            "a string.".format(type(id)))
        self._id = id

    @property
    def seconds(self):
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
        return self._minutes

    @property
    def clock_name(self):
        return self._clock_name

    @clock_name.setter
    def clock_name(self, clock_name):
        if not isinstance(clock_name, str):
            raise TypeError("Invalid type for 'clock_name' attribute, '{}', "
                            "requires a string.".format(type(clock_name)))

        # Clear time if new clock is incompatible with previous one
        if not type(self).compatible(self._clock_name, clock_name):
            self.seconds = 0.

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

    def print_clock(self):
        """Print info of clock.

        For :py:attr:`clock_name` that can be queried with
        `time.get_clock_info`_, print clock details. Otherwise print
        the corresponding timing function.
        """
        n = self.clock_name
        f = type(self).CLOCKS[self.clock_name]
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

    @classmethod
    def print_clocks(cls):
        """Print info of available clocks."""
        for n in cls.CLOCKS.keys():
            Timer(clock_name=n).print_clock()
        print("Default clock is {}".format(cls.DEFAULT_CLOCK_NAME))

    @classmethod
    def compatible(cls, t1, t2):
        """Return truth of compatibility between either a :py:class:`Timer`
        pair or clock name pair.

        For :py:attr:`clock_name` that can be queried with
        `time.get_clock_info`_, compatibility requires that all attributes are
        identical. All other cases require that the timing functions are the
        same function.

        Args:
            t1 (Timer | str): First :py:class:`Timer` (or
                :py:attr:`clock_name`).
            t2 (Timer | str): Second :py:class:`Timer`(or
                :py:attr:`clock_name`).

        Returns:
            bool: True if compatible, else False
        """
        clock_name1 = t1.clock_name if isinstance(t1, Timer) else t1
        clock_name2 = t2.clock_name if isinstance(t2, Timer) else t2
        try:
            return time.get_clock_info(clock_name1) == \
                       time.get_clock_info(clock_name2)
        except (TypeError, ValueError):
            try:
                return cls.CLOCKS[clock_name1] is cls.CLOCKS[clock_name2]
            except KeyError:
                return False

    @classmethod
    def compatibility_test(cls, t1, t2):
        """Check compatibility between a :py:class:`Timer` pair.

        Args:
            t1 (Timer): First :py:class:`Timer`.
            t2 (Timer): Second :py:class:`Timer`.

        Raises:
            ValueError: If :py:class:`Timer` pair is not compatible.
        """
        if not cls.compatible(t1, t2):
            raise ValueError("Incompatible Timer clocks")
        pass

    @classmethod
    def add(cls, t1, t2):
        """Sum the times of a :py:class:`Timer` pair.

        The :py:attr:`id` of the resulting :py:class:`Timer` contains a
        combination of the input :py:class:`Timer` :py:attr:`id`. The addition
        operator is an alias to :py:meth:`add`.

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

        Args:
            t1 (Timer): First :py:class:`Timer`.
            t2 (Timer): Second :py:class:`Timer`.

        Returns:
            Timer: :py:class:`Timer` with absolute time difference.
        """
        cls.compatibility_test(t1, t2)
        new_id = '-'.join(filter(None, [t1.id, t2.id]))
        return Timer(new_id, seconds=abs(t1.seconds - t2.seconds))
