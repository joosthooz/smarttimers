"""Timer module used as building block for timing libraries."""


__all__ = ['Timer']


import time as std_time
from .clocks import CLOCKS, print_clock, get_clock_info, are_clocks_compatible


class Timer:
    """Read current time from a clock/counter.

    Args:
        label (str, None, optional): Timer identifier. Default is None.
        seconds (float, optional): Time measured in fractional seconds.
            Default is 0.0.
        clock_name (str, optional): Name to select a time measurement
            function from :attr:`CLOCKS` map.  Default is
            :attr:`DEFAULT_CLOCK_NAME`.
        timer (Timer, optional): Instance to copy properties from.
            Default is None.

    A :class:`Timer` allows recording the current time measured by a
    registered timing function. Time is recorded in fractional seconds
    and fractional minutes. :class:`Timer` supports addition,
    difference, and logical operators. :class:`Timer` uses a simple and
    extensible API which allows registering new timing functions. A
    timing function is compliant if it returns a time measured in
    fractional seconds. The function can contain arbitrary positional
    and/or keyword arguments or no arguments.

    .. literalinclude:: ../examples/example_Timer.py
        :language: python
        :linenos:
        :name: Timer_API
        :caption: Timer API examples.

    .. _`time.perf_counter()`:
        https://docs.python.org/3/library/time.html#time.perf_counter
    .. _`time.process_time()`:
        https://docs.python.org/3/library/time.html#time.process_time
    .. _`time.monotonic()`:
        https://docs.python.org/3/library/time.html#time.monotonic
    .. _`time.time()`:
        https://docs.python.org/3/library/time.html#time.time

    Available time measurement functions in :attr:`CLOCKS`:
        * 'perf_counter' -> `time.perf_counter()`_
        * 'process_time' -> `time.process_time()`_
        * 'monotonic'    -> `time.monotonic()`_
        * 'time'         -> `time.time()`_ (deprecated)

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
        Timer.register_clock('custom_time', custom_time_function)

    .. _`time`: https://docs.python.org/3/library/time.html

    Note:
        * The available timing functions are built-ins from the standard
          `time`_ library.
        * Custom timing functions need to have a compliant interface. If
          a custom timing function is non-compliant, then place it
          inside a compliant wrapper function.
        * Only Timers with compatible clocks support arithmetic and
          logical operators. Compatible Timers use the same
          implementation function in the backend, see
          :meth:`print_clocks`.

    .. _`namedtuple`:
        https://docs.python.org/3.3/library/collections.html#collections.namedtuple

    Attributes:
        DEFAULT_CLOCK_NAME (str): Default clock name.
        CLOCKS (dict): Map between clock names and timing functions.
        label (str): Identifier.
        clock_name (str, None): Name to select a timing function from
            :attr:`CLOCKS` map.
        seconds (float): Time measured in fractional seconds.
        minutes (float): Time measured in minutes.
        info (ClockInfo): Clock attributes (`namedtuple`_).
    """
    DEFAULT_CLOCK_NAME = 'perf_counter'

    def __init__(self, label=None, **kwargs):
        self._seconds = None
        self._minutes = None
        self._clock_name = None
        self._clock = None

        timer = kwargs.get('timer')
        if timer:
            self.label = label if label else timer.label
            self.seconds = timer.seconds
            self.clock_name = timer.clock_name
        else:
            self.label = label
            self.seconds = kwargs.get('seconds', 0.)
            self.clock_name = kwargs.get('clock_name',
                                         type(self).DEFAULT_CLOCK_NAME)

    def __repr__(self):
        return "{cls}(label={label},"\
               " seconds={seconds},"\
               " clock_name={clock_name},"\
               " function='{info.function}',"\
               " adjustable={info.adjustable},"\
               " implementation='{info.implementation}',"\
               " monotonic={info.monotonic},"\
               " resolution={info.resolution})"\
               .format(cls=type(self).__qualname__,
                       label=repr(self.label),
                       seconds=self.seconds,
                       clock_name=repr(self.clock_name),
                       info=self.info)

    def __str__(self):
        ffmt = "{lw}.{pr}f".format(lw=12, pr=6)
        fmt = "{}" + 2 * (" {:" + ffmt + "}")
        return fmt.format(self.label, self.seconds, self.minutes)

    def __add__(self, other):
        if not are_clocks_compatible(self.clock_name, other.clock_name):
            raise Exception("Timers are not compatible")
        return type(self)(label='+'.join(filter(None, [self.label, other.label])),
                          seconds=self.seconds + other.seconds,
                          clock_name=self.clock_name)

    def __sub__(self, other):
        if not are_clocks_compatible(self.clock_name, other.clock_name):
            raise Exception("Timers are not compatible")
        return type(self)(label='-'.join(filter(None, [self.label, other.label])),
                     seconds=self.seconds - other.seconds,
                     clock_name=self.clock_name)

    def __eq__(self, other):
        if not are_clocks_compatible(self.clock_name, other.clock_name):
            raise Exception("Timers are not compatible")
        return self.seconds == other.seconds

    __hash__ = None

    def __lt__(self, other):
        if not are_clocks_compatible(self.clock_name, other.clock_name):
            raise Exception("Timers are not compatible")
        return self.seconds < other.seconds

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, seconds):
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
        if self._clock_name \
                and not are_clocks_compatible(self.clock_name, clock_name):
            self.clear()
        # Set function first to catch key error before setting clock name.
        self._clock = CLOCKS[clock_name]
        self._clock_name = clock_name

    @property
    def info(self):
        return get_clock_info(self.clock_name)

    def print_info(self):
        print_clock(self.clock_name)

    def time(self, *args, **kwargs):
        self.seconds = self._clock(*args, **kwargs)
        return self.seconds

    def clear(self):
        self.seconds = 0.

    def reset(self):
        self.label = None
        self.clock_name = type(self).DEFAULT_CLOCK_NAME
        self.clear()

    sleep = std_time.sleep
