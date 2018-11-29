"""Utilities to measure time from system and custom clocks/counters.

Classes:
    * :class:`Timer`
    * :class:`TimerDict`

Todo:
    * Extend to support additional stats besides time (e.g., psutil).
    * Integrate PAPI counters.
    * Support timing concurrent processes (e.g., time.thread_time).
"""


import time
import types
from smarttimers.exceptions import (TimerCompatibilityError, TimerKeyError,
                                    TimerTypeError, TimerValueError)


__all__ = ['Timer', 'TimerDict']


class TimerDict(dict):
    """Map between label identifier and callable object.

    Args:
        tdict (dict, TimerDict, str -> callable, optional): Dictionary for
            initialization.

    Raises:
        TimerTypeError: If *tdict* is not derived from dict.
        TimerKeyError: If keys are not strings or does not exists.
        TimerValueError: If value is not a callable object.
    """
    def __init__(self, tdict=dict()):
        self.update(tdict)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TimerKeyError(str(type(self)) + "key", str)
        if not callable(value):
            raise TimerValueError(str(type(self)) + "[key]", "callable object")
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TimerKeyError(str(type(self)) + "key", str)
        if key not in self.keys():
            raise TimerKeyError(str(type(self)) + "[key]", "existing key")
        return super().__getitem__(key)

    def update(self, tdict):
        """Extends map with given dictionary.

        Only accepts *dict* or :class:`TimerDict` arguments.
        """
        if not isinstance(tdict, (dict, type(self))):
            raise TimerTypeError(type(self), [dict, type(self)])
        for k, v in tdict.items():
            self[k] = v


class MetaTimerProperty(type):
    """Metaclass for :class:`Timer` class variables.

    Requires :class:`TimerDict`.

    Raises:
        TimerTypeError: If set property uses an invalid type.
    """
    @property
    def DEFAULT_CLOCK_NAME(cls):
        return cls._DEFAULT_CLOCK_NAME

    @DEFAULT_CLOCK_NAME.setter
    def DEFAULT_CLOCK_NAME(cls, value):
        if not isinstance(value, str):
            raise TimerTypeError("DEFAULT_CLOCK_NAME", str)
        cls._DEFAULT_CLOCK_NAME = value

    @property
    def CLOCKS(cls):
        return cls._CLOCKS

    @CLOCKS.setter
    def CLOCKS(cls, value):
        if not isinstance(value, (dict, TimerDict)):
            raise TimerTypeError("CLOCKS", [dict, TimerDict])
        cls._CLOCKS = value if isinstance(value, TimerDict) \
            else TimerDict(value)


class Timer(metaclass=MetaTimerProperty):
    """Read current time from a clock/counter.

    Args:
        label (str, optional): Label identifier. Default is empty string.

        kwargs (dict, optional): Map of options. Valid options are
            :attr:`seconds`, :attr:`clock_name`, and :attr:`timer`.

        kwargs['seconds'] (float, optional): Time measured in fractional
            seconds. Default is 0.0.

        kwargs['clock_name'] (str, optional): Clock name used to select a time
            measurement function. Default is :attr:`DEFAULT_CLOCK_NAME`.

        kwargs['timer'] (Timer, optional): Reference instance to use as
            initialization.

    A :class:`Timer` allows recording the current time measured by a
    registered timing function. Time is recorded in fractional seconds and
    fractional minutes. :class:`Timer` supports addition, difference, and
    logical operators. :class:`Timer` uses a simple and extensible API which
    allows registering new timing functions. A timing function is compliant if
    it returns a time measured in fractional seconds. The function can contain
    arbitrary positional and/or keyword arguments or no arguments.

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
        Timer.register_clock('custom_time', custom_time_function)
        # or
        Timer.CLOCKS['custom_time'] = custom_time_function

    .. _`time`: https://docs.python.org/3/library/time.html

    Note:
        * New timing functions need to have a compliant interface. If a user
          wants to register a non-compliant timing function, a compliant
          wrapper function can be used. The available timing functions are
          built-ins from the standard `time`_ library.
        * Only Timers with compatible clocks support arithmetic and logical
          operators. Otherwise a :class:`TimerCompatibilityError` exception
          occurs.

    Warning:
        When registering a new timing function to :attr:`CLOCKS`, it is
        recommended to use a unique clock name to prevent overwriting over an
        existing one.

    Attributes:
        DEFAULT_CLOCK_NAME (str): Default clock name, used when
            :attr:`clock_name` is empty string.

            Raises:
                TimerTypeError: If not a string.

        CLOCKS (:class:`TimerDict`, str -> callable): Map between clock
            name and time measurement functions.

            Raises:
                TimerTypeError: If not assigned with dictionary.
                TimerKeyError: If key is not a string.
                TimerValueError: If assigned item is not callable.

        label (str): Label identifier.

            Raises:
                TimerTypeError: If not a string.

        seconds (float, read-only): Time measured in fractional seconds.

            Set internally either during initialization or when recording time.

            Raises:
                TimerTypeError: If not numeric.
                TimerValueError: If negative number.

        minutes (float, read-only): Time measured in minutes.

        clock_name (str): Clock name used to select a time measurement
            function.

            Indexes the :attr:`CLOCKS` map to select a time function. If
            set to the empty string then :attr:`DEFAULT_CLOCK_NAME` is used.
            An instance is reset when set to a new and incompatible clock name.

            Raises:
                TimerTypeError: If not a string.

    .. _`time.get_clock_info`:
        https://docs.python.org/3/library/time.html#time.get_clock_info
    """

    _DEFAULT_CLOCK_NAME = 'perf_counter'

    _CLOCKS = TimerDict({
        'perf_counter': time.perf_counter,
        'process_time': time.process_time,
        'clock': time.clock,
        'monotonic': time.monotonic,
        'time': time.time
    })

    def __init__(self, label='', **kwargs):
        self.label = label

        # Check if another Timer is provided for initialization
        other = kwargs.get('timer')
        if isinstance(other, Timer):
            self._set_time(other.seconds)
            self.clock_name = other.clock_name
        else:
            self._set_time(kwargs.get('seconds', 0.))
            self.clock_name = kwargs.get('clock_name',
                                         type(self).DEFAULT_CLOCK_NAME)

    def __str__(self):
        """String representation.

        Returns:
            str: Comma delimited string (:attr:`seconds`,
                :attr:`minutes`, :attr:`label`)
        """
        return "{}, {:.6f}, {:.6f}".format(self.label,
                                           self.seconds,
                                           self.minutes)

    def __add__(self, other):
        if not self.is_compatible(other):
            raise TimerCompatibilityError
        new_label = '+'.join(filter(None, [self.label, other.label]))
        return Timer(new_label,
                     seconds=self.seconds + other.seconds,
                     clock_name=self.clock_name)

    def __sub__(self, other):
        if not self.is_compatible(other):
            raise TimerCompatibilityError
        new_label = '-'.join(filter(None, [self.label, other.label]))
        return Timer(new_label,
                     seconds=abs(self.seconds - other.seconds),
                     clock_name=self.clock_name)

    def __eq__(self, other):
        # Return false if not compatible to allow index searches in Timer
        # iterables
        if not self.is_compatible(other):
            return False
        return self.seconds == other.seconds

    def __lt__(self, other):
        if not self.is_compatible(other):
            raise TimerCompatibilityError
        return self.seconds < other.seconds

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def _set_time(self, seconds):
        # Do checks here because attribute is read-only
        if not isinstance(seconds, (int, float)):
            raise TimerTypeError("seconds", float)
        if seconds < 0.:
            raise TimerValueError("seconds", "non-negative number")
        self._seconds = float(seconds)
        self._minutes = seconds / 60.

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        if not isinstance(label, str):
            raise TimerTypeError("label", str)
        self._label = label

    @property
    def seconds(self):
        return self._seconds

    @property
    def minutes(self):
        return self._minutes

    @property
    def clock_name(self):
        return self._clock_name

    @clock_name.setter
    def clock_name(self, clock_name):
        if not isinstance(clock_name, str):
            raise TimerTypeError("clock_name", str)

        # Clear time if new clock is incompatible with previous one. Skip
        # check if setting for the first time (e.g., __init__) to prevent
        # clearing time values that had been set previously.
        #
        # Note: can create an infinite loop if not careful. is_compatible() is
        # called which in turn creates a Timer object which calls this property
        # during initialization.
        if hasattr(self, '_clock_name') and not self.is_compatible(clock_name):
            self.clear()

        self._clock_name = clock_name if clock_name \
            else type(self).DEFAULT_CLOCK_NAME
        self._clock = type(self).CLOCKS[self._clock_name]

    def time(self, *args, **kwargs):
        """Invoke time measurement function and record measured time.

        Calls timing function currently configured via :attr:`clock_name`.
        This method accepts arbitrary positional and/or keyword arguments to
        enable support for arbitrary signatures of timing functions.

        Args:
            args (tuple, optional): Positional arguments for time function.
            kwargs (dict, optional): Keyword arguments for time function.

        Returns:
            float: Time measured in fractional seconds.
        """
        self._set_time(self._clock(*args, **kwargs))
        return self.seconds

    def clear(self):
        """Set time values to zero."""
        self._set_time(0.)

    def reset(self):
        """Clear, empty :attr:`label`, and reset clock to default value."""
        self.label = ''
        self.clock_name = type(self).DEFAULT_CLOCK_NAME
        self.clear()

    def get_info(self):
        """Return clock information.

        For :attr:`clock_name` that can be queried with
        `time.get_clock_info`_, forward the output namespace object. Otherwise
        create and populate a namespace with the timing function.

        .. _`types.SimpleNamespace`:
            https://docs.python.org/3/library/types.html?highlight=types#types.SimpleNamespace

        Returns:
            `types.SimpleNamespace`_: Namespace with clock info.
        """
        try:
            return time.get_clock_info(self.clock_name)
        except (TypeError, ValueError):
            clock_info = {
                'adjustable': None,
                'implementation': type(self).CLOCKS[self.clock_name].__name__,
                'monotonic': None,
                'resolution': None}
            return types.SimpleNamespace(**clock_info)

    def print_info(self):
        """Pretty print clock information."""
        print("{name}:\n"
              "    function      : {func}\n"
              "    adjustable    : {info.adjustable}\n"
              "    implementation: {info.implementation}\n"
              "    monotonic     : {info.monotonic}\n"
              "    resolution    : {info.resolution}"
              .format(name=self.clock_name,
                      func=type(self).CLOCKS[self.clock_name],
                      info=self.get_info()))

    def is_compatible(self, other):
        """Return truth of compatibility between a :class:`Timer` pair.

        For a :attr:`clock_name` that can be queried with
        `time.get_clock_info`_, compatibility requires that all attributes are
        identical. All other cases require that the timing functions are the
        same function.

        Args:
            other (Timer): Second instance.

        Returns:
            bool: True if compatible, else False.
        """
        if not isinstance(other, Timer):
            return False

        # Exception occurs when time.get_clock_info() receives an unknown clock
        try:
            return time.get_clock_info(self.clock_name) == \
                time.get_clock_info(other.clock_name)
        except Exception:
            return type(self).CLOCKS[self.clock_name] is \
                type(self).CLOCKS[other.clock_name]

    @classmethod
    def sum(cls, timer1, timer2):
        """Compute the time sum of a :class:`Timer` pair.

        This method wraps the addition operator between :class:`Timer`
        objects. The :attr:`label` of the resulting :class:`Timer`
        contains a combination of *timer1* and *timer2* :attr:`label`. The
        :attr:`clock_name` of the resulting :class:`Timer` is set to the
        clock name of *timer1*.

        Args:
            timer1 (Timer): First instance.
            timer2 (Timer): Second instance.

        Returns:
            Timer: Instance containing the time sum.

        Raises:
            TimerCompatibilityError: If timers are not compatible.
        """
        return timer1 + timer2

    @classmethod
    def diff(cls, timer1, timer2):
        """Compute the absolute time difference of a :class:`Timer` pair.

        This method wraps the difference operator between :class:`Timer`
        objects. The :attr:`label` of the resulting :class:`Timer`
        contains a combination of *timer1* and *timer2* :attr:`label`. The
        :attr:`clock_name` of the resulting :class:`Timer` is set to the
        clock name of *timer1*.

        Args:
            timer1 (Timer): First instance.
            timer2 (Timer): Second instance.

        Returns:
            Timer: Instance containing the absolute time difference.

        Raises:
            TimerCompatibilityError: If timers are not compatible.
        """
        return timer1 - timer2

    @classmethod
    def register_clock(cls, clock_name, clock_func):
        """Registers a time function to :attr:`CLOCKS` map.

        If a mapping already exists for *clock_name*, it will be updated with
        *clock_func*. For invalid arguments, error handling is expected from
        :attr:`CLOCKS` properties.

        Args:
            clock_name (str): Clock name.
            clock_func (callable): Reference to a time measurement function.
        """
        cls.CLOCKS[clock_name] = clock_func

    @classmethod
    def unregister_clock(cls, clock_name):
        """Remove a registered clock from :attr:`CLOCKS` map.

        For invalid arguments, error handling is expected from
        :attr:`CLOCKS` properties.

        Args:
            clock_name (str): Clock name.
        """
        # Query map using __getitem__ property to check for valid key because
        # 'del' does not triggers __getitem__.
        dummy = cls.CLOCKS[clock_name]
        del dummy  # to prevent warning from linting
        del cls.CLOCKS[clock_name]

    @classmethod
    def print_clocks(cls):
        """Pretty print information of registered clocks."""
        print("Default clock: {}".format(cls.DEFAULT_CLOCK_NAME))
        for n in cls.CLOCKS.keys():
            print()
            Timer(clock_name=n).print_info()
