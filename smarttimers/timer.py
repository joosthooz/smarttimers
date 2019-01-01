"""Utilities to measure time from system and custom clocks/counters.

Classes:
    * :class:`Timer`

Todo:
    * How to handle if default clock is unregistered? Also, when a clock
      is unregistered, instances may have the old clock, error is
      triggered.
"""


__all__ = ['Timer']


import os
import time
import types


class Timer:
    """Read current time from a clock/counter.

    Args:
        label (str, None, optional): Timer identifier. Default is None.

        seconds (float, optional): Time measured in fractional seconds.
                                   Default is 0.0.

        clock_name (str, optional): Clock name used to select a time
                                    measurement function. Default is
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
    .. _`time.clock()`:
        https://docs.python.org/3/library/time.html#time.clock
    .. _`time.monotonic()`:
        https://docs.python.org/3/library/time.html#time.monotonic
    .. _`time.time()`:
        https://docs.python.org/3/library/time.html#time.time

    Available time measurement functions in :attr:`CLOCKS`:
        * 'perf_counter' -> `time.perf_counter()`_
        * 'process_time' -> `time.process_time()`_
        * 'clock'        -> `time.clock()`_ (deprecated)
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
        * Custom timing functions need to have a compliant interface. If
          a custom timing function is non-compliant, then wrap it inside
          a compliant wrapper function. The available timing functions
          are built-ins from the standard `time`_ library.
        * Only Timers with compatible clocks support arithmetic and
          logical operators. Compatible Timers use the same
          implementation function in the backend, see
          :meth:`print_clocks`.

    .. _`types.SimpleNamespace`:
        https://docs.python.org/3/library/types.html?highlight=types#types.SimpleNamespace
    .. _`time.get_clock_info`:
        https://docs.python.org/3/library/time.html#time.get_clock_info

    Attributes:
        DEFAULT_CLOCK_NAME (str): Clock name used when
                                  :attr:`clock_name` is empty string or
                                  None.

        CLOCKS (dict): Map between clock names and time measurement
                       functions.

        label (str): Timer identifier.

        seconds (float): Time measured in fractional seconds.

            Set internally either during initialization or when
            recording time.

        minutes (float): Time measured in minutes.

        clock_name (str, None): Clock name used to select a time
                                measurement function.

            Indexes the :attr:`CLOCKS` map to select a timing function.
            An instance time is cleared when a new and incompatible
            clock name is set.

        info (`types.SimpleNamespace`_): Namespace with clock info.
    """

    DEFAULT_CLOCK_NAME = "perf_counter"

    CLOCKS = {
        "perf_counter": time.perf_counter,
        "process_time": time.process_time,
        "clock": time.clock,
        "monotonic": time.monotonic,
        "time": time.time
        }

    # Internal storage for attributes of non-built-in clocks
    _CLOCKS_INFO = {}

    def __init__(self, label=None, seconds=0., clock_name=DEFAULT_CLOCK_NAME,
                 timer=None, **kwargs):
        self._seconds = None
        self._minutes = None
        self._clock_name = None
        self._clock = None

        if timer:
            self.label = label if label else timer.label
            self.seconds = timer.seconds
            self.clock_name = timer.clock_name
        else:
            self.label = label
            self.seconds = seconds
            self.clock_name = clock_name

    def __repr__(self):
        return "{cls}(label={label}, " \
               "seconds={seconds}, " \
               "clock_name={clock_name}, " \
               "function='{func}', " \
               "adjustable={info.adjustable}, " \
               "implementation='{info.implementation}', " \
               "monotonic={info.monotonic}, " \
               "resolution={info.resolution})" \
               .format(cls=type(self).__qualname__,
                       label=repr(self.label),
                       seconds=self.seconds,
                       clock_name=repr(self.clock_name),
                       func=type(self).CLOCKS[self.clock_name],
                       info=self.info)

    def __str__(self):
        ffmt = "{lw}.{pr}f".format(lw=12, pr=6)
        fmt = "{}" + 2 * (" {:" + ffmt + "}")
        return fmt.format(self.label, self.seconds, self.minutes)

    def __add__(self, other):
        if not type(self).is_compatible(self, other):
            raise Exception("timers are not compatible")
        return Timer(label='+'.join(filter(None, [self.label, other.label])),
                     seconds=self.seconds + other.seconds,
                     clock_name=self.clock_name)

    def __sub__(self, other):
        if not type(self).is_compatible(self, other):
            raise Exception("timers are not compatible")
        return Timer(label='-'.join(filter(None, [self.label, other.label])),
                     seconds=self.seconds - other.seconds,
                     clock_name=self.clock_name)

    def __eq__(self, other):
        if type(self).is_compatible(self, other):
            return self.seconds == other.seconds
        return NotImplemented

    __hash__ = None

    def __lt__(self, other):
        if type(self).is_compatible(self, other):
            return self.seconds < other.seconds
        return NotImplemented

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
        if clock_name not in type(self).CLOCKS:
            raise ValueError("name '{}' is not registered".format(clock_name))

        # Clear time if new clock is incompatible with previous one.
        if self._clock_name and not type(self).is_compatible(self, clock_name):
            self.clear()

        self._clock_name = clock_name
        self._clock = type(self).CLOCKS[self._clock_name]

    @property
    def info(self):
        if self.clock_name in vars(time):
            info = time.get_clock_info(self.clock_name)
        else:
            info = type(self)._CLOCKS_INFO[self.clock_name]
        info.name = self.clock_name
        info.function = type(self).CLOCKS[self.clock_name]
        return info

    def time(self, *args, **kwargs):
        """Record time.

        Args:
            args (tuple, optional): Positional arguments for time
                                    function.
            kwargs (dict, optional): Keyword arguments for time
                                     function.

        Returns:
            float: Time measured in fractional seconds.
        """
        self.seconds = self._clock(*args, **kwargs)
        return self.seconds

    def clear(self):
        self.seconds = 0.

    def reset(self):
        self.label = None
        self.clock_name = type(self).DEFAULT_CLOCK_NAME
        self.clear()

    def print_info(self):
        """Pretty print clock information."""
        print("{info.name}:{lsep}"
              "    function      : {info.function}{lsep}"
              "    adjustable    : {info.adjustable}{lsep}"
              "    implementation: {info.implementation}{lsep}"
              "    monotonic     : {info.monotonic}{lsep}"
              "    resolution    : {info.resolution}"
              .format(info=self.info, lsep=os.linesep))

    @classmethod
    def is_compatible(cls, timer1, timer2):
        """Return truth of compatibility between a :class:`Timer` pair.

        If *timers* correspond to built-in functions, use
        `time.get_clock_info`_ and compatibility requires that all
        attributes are identical. For custom *timers*, the timing
        functions have to be the same.

        Args:
            timer1 (Timer, str): Timer or clock name.
            timer2 (Timer, str): Timer or clock name.

        Returns:
            bool: True if compatible, else False.
        """
        clock1 = timer1.clock_name if isinstance(timer1, Timer) else timer1
        clock2 = timer2.clock_name if isinstance(timer2, Timer) else timer2
        if clock1 in vars(time) and clock2 in vars(time):
            return time.get_clock_info(clock1) == time.get_clock_info(clock2)
        else:
            return cls.CLOCKS[clock1] is cls.CLOCKS[clock2]

    @classmethod
    def register_clock(cls, name, func, **kwargs):
        """Registers a time function to :attr:`CLOCKS` map.

        Args:
            name (str): Clock name.
            func (callable): Time measurement function.
            kwargs (dict, optional): Attributes of clock.
        """
        cls.CLOCKS[name] = func
        if name not in vars(time):
            cls._CLOCKS_INFO[name] = types.SimpleNamespace(
                adjustable=kwargs.get('adjustable', None),
                implementation=kwargs.get('implementation', func),
                monotonic=kwargs.get('monotonic', None),
                resolution=kwargs.get('resolution', None))

    @classmethod
    def unregister_clock(cls, name):
        """Remove a registered clock from :attr:`CLOCKS` map.

        Args:
            name (str): Clock name.
        """
        del cls.CLOCKS[name]
        if name in cls._CLOCKS_INFO:
            del cls._CLOCKS_INFO[name]

    @classmethod
    def print_clocks(cls):
        """Pretty print information of registered clocks."""
        print("Default clock: {}".format(cls.DEFAULT_CLOCK_NAME))
        timer = Timer()
        for name in cls.CLOCKS:
            print()
            timer.clock_name = name
            timer.print_info()

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)
