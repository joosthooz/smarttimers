"""SmartTimer

Classes:
    :class:`SmartTimer`
"""


from collections import defaultdict
from smarttimers.exceptions import (TimerError, TimerKeyError, TimerTypeError,
                                    TimerValueError)
from smarttimers.timer import Timer


__all__ = ['SmartTimer']


class SmartTimer:
    """`Timer`_ container to perform time measurements in code blocks.

    Args:
        name (str, optional): Name of container. Default is *smarttimer*.

        kwargs (dict, optional): Map of options to configure the internal
            `Timer`_. Default is `Timer`_ defaults.

    A :class:`SmartTimer` allows recording elapsed time in an arbitrary
    number of code blocks. Specified points in the code are marked as either
    the beginning of a block to measure, :meth:`tic`, or as the end of a
    measured block, :meth:`toc`. Times are managed internally and ordered
    based on :meth:`tic` calls. Times can be queried, operated on, and
    written to file.

    The following schemes are supported for timing code blocks
        * Consecutive: ``tic('A')``, ``toc()``, ..., ``tic('B')``, ``toc()``
        * Cascade: ``tic('A')``, ``toc()``, ``toc()``, ...
        * Nested: ``tic('A')``, ``tic('B')``, ..., ``toc()``, ``toc()``
        * Label-paired: ``tic('A')``, ``tic('B')``, ..., ``toc('A')``,
          ``toc('B')``
        * Mixed: arbitrary combinations of schemes

    .. literalinclude:: ../examples/example_SmartTimer.py
        :language: python
        :linenos:
        :name: SmartTimer_API
        :caption: SmartTimer API examples.

    Attributes:
        name (str): Name of container. May be used for filename in
            :meth:`write_to_file`.

            Raises:
                :class:`smarttimers.exceptions.TimerTypeError`: If not a
                    string.
                :class:`smarttimers.exceptions.TimerValueError`: If empty
                    string.

        labels (list, str, read-only): Label identifiers of completed timed
            code blocks.

        active_labels (list, str, read-only): Label identifiers of active code
            blocks.

        seconds (list, float, read-only): Elapsed time in seconds for
            completed code blocks.

        minutes (list, float, read-only): Elapsed time in minutes for
            completed code blocks.

        times (dict, str -> float, read-only): Map of times elapsed for
            completed blocks. Keys are the labels used when invoking
            :meth:`tic`.
    """

    def __init__(self, name='smarttimer', **kwargs):
        self.name = name
        self._timer = Timer(label='', **kwargs)  # internal Timer
        self._first_tic = None  # pointer used to calculate walltime
        self._last_tic = self._timer  # pointer used to support cascade scheme
        self._timers = []  # completed time blocks
        self._timer_stack = []  # stack of active time blocks

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TimerTypeError("name", str)
        if not name:
            raise TimerValueError("name", "non-empty string")
        self._name = name

    @property
    def labels(self):
        return [t.label if t else t for t in self._timers]

    @property
    def active_labels(self):
        return [t.label for t in self._timer_stack]

    @property
    def seconds(self):
        return [t.seconds if t else t for t in self._timers]

    @property
    def minutes(self):
        return [t.minutes if t else t for t in self._timers]

    @property
    def times(self):
        times_map = defaultdict(list)
        for t in filter(None, self._timers):
            times_map[t.label].append(t.seconds)
        return times_map

    def __str__(self):
        return '\n'.join([str(t) for t in self._timers]) + '\n'

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, *args):
        self.toc()

    def __getitem__(self, *keys):
        """Query time(s) of completed code blocks.

        Example:
            * timings[2, 4]
            * timings['I/O', 'Processing']
            * timings[2, 'Processing']
            * timings[1:2, 4:6, 'I/O']

        Args:
            keys (str, slice, integer): Key(s) to select times. If string, then
                consider it as a label used in :meth:`tic`. If integer or
                slice, then consider it as an index (based on :meth:`tic`
                ordering). Key types can be mixed.

        Returns:
            None: If key did not match a completed `Timer`_ label.
            list, float: Time in seconds of completed code blocks.

        Raises:
            TimerKeyError: If keys are not string, integer, or slice.
        """
        # Ensure 'key' is a single level iterable to allow loop
        # processing. When an iterable or multiple keys are passed,
        # the arguments are automatically organized as a tuple of
        # tuple of values ((arg1,arg2),).
        if isinstance(keys[0], tuple):
            keys = keys[0]

        seconds = []
        for key in keys:
            if isinstance(key, str):
                seconds.extend(self.times[key])
            elif isinstance(key, int):
                if key >= 0 and key < len(self._timers):
                    seconds.append(self._timers[key].seconds)
            elif isinstance(key, slice):
                seconds.append(self.seconds[key])
            else:
                raise TimerKeyError(str(key), "{}, {}, or {}".format(str,
                                    int, slice))

        if not seconds:
            return None
        else:
            return seconds if len(seconds) > 1 else seconds[0]

    def tic(self, label=''):
        """Start measuring time.

        Measure time at the latest moment possible to minimize noise from
        internal operations.

        Args:
            label (str): Label identifier for current code block.

        Raises:
            *: Exceptions generated by internal :class:`Timer` initialized
                with *label*.
        """
        # _last_tic -> timer of most recent tic
        self._last_tic = Timer(label=label)

        # _first_tic -> timer of first tic
        if self._first_tic is None:
            self._first_tic = self._last_tic

        # Insert Timer into stack, then record time to minimize noise
        self._timer_stack.append(self._last_tic)

        # Use 'None' as an indicator of active code blocks
        self._timers.append(None)

        # Measure time
        self._last_tic.time()

    def toc(self, label=None):
        """Stop measuring time at end of code block.

        Measure time at the soonest moment possible to minimize noise from
        internal operations.

        Note:
            In cascade regions, that is, multiple toc() calls, some noise will
            be introduced, < 2ms. There is the possibility of correcting this
            noise, but even the correction is noise itself.

        Args:
            label (str): Label identifier for current code block.

        Returns:
            float: Measured time in seconds.

        Raises:
            TimerError: If there is not a matching :meth:`tic`.
            TimerTypeError: If *label* is not a string.
            TimerKeyError: If there is not a matching :meth:`tic`.
        """
        # Error if no tic pair (e.g., toc() after instance creation)
        # _last_tic -> _timer
        if self._last_tic is self._timer:
            raise TimerError("no matched pair")

        # Measure time
        self._timer.time()

        # Stack is not empty so there is a matching tic
        if self._timer_stack:

            # Last item or item specified by label
            stack_idx = -1

            # Label-paired timer
            if label is not None:
                if not isinstance(label, str):
                    raise TimerTypeError(str(label), str)

                # Find index of last timer in stack with matching label
                for i, t in enumerate(self._timer_stack[::-1]):
                    if label == t.label:
                        stack_idx = len(self._timer_stack) - i - 1
                        break
                else:
                    raise TimerKeyError(str(label), "matched pair")

            # Calculate time elapsed
            t_first = self._timer_stack.pop(stack_idx)
            t_diff = self._timer - t_first

            # Place time in corresponding position
            idx = [i for i, v in enumerate(self._timers)
                   if v is None][stack_idx]
            self._timers[idx] = t_diff

        # Empty stack, use _last_tic -> timer from most recent tic
        else:
            if label is not None:
                raise TimerKeyError(str(label), "matched pair")

            t_diff = self._timer - self._last_tic
            self._timers.append(t_diff)

        return t_diff.seconds

    def walltime(self):
        """Compute elapsed time in seconds between first :meth:`tic` and
        most recent :meth:`toc`.
        """
        return self._timer.seconds - self._first_tic.seconds

    def print_info(self):
        """Pretty print information of registered clock."""
        self._timer.print_info()

    def remove(self, *keys):
        """Remove time(s) of completed code blocks.

        Args:
            keys (str, slice, integer): Key(s) to select times. If string, then
                consider it as a label used in :meth:`tic`. If integer or
                slice, then consider it as an index (based on :meth:`tic`
                ordering). Key types can be mixed.

        Raises:
            TimerKeyError: If keys are not string, integer, or slice.
        """
        # Ensure 'key' is a single level iterable to allow loop
        # processing. When an iterable or multiple keys are passed,
        # the arguments are automatically organized as a tuple of
        # tuple of values ((arg1,arg2),).
        if isinstance(keys[0], tuple):
            keys = keys[0]

        for key in keys:
            if isinstance(key, str):
                # Slice produces a copy of _timers, original is modified
                for t in filter(None, self._timers[:]):
                    if key == t.label:
                        self._timers.remove(t)
            elif isinstance(key, int):
                if key >= 0 and key < len(self._timers):
                    self._timers.remove(self._timers[key])
            elif isinstance(key, slice):
                # Slice produces a copy of _timers, original is modified
                for t in self._timers[key]:
                    self._timers.remove(t)
            else:
                raise TimerKeyError(str(key), "{}, {}, or {}".format(str,
                                    int, slice))

    def clear(self):
        """Empty internal storage."""
        self._timers = []
        self._timer_stack = []
        self._timer.clear()
        self._first_tic = None
        self._last_tic = self._timer

    def reset(self):
        """Restore :attr:`name`, reset clock to default value, and empty
        internal storage."""
        self.name = 'smarttimer'
        self._timer.reset()
        self.clear()

    def write_to_file(self, fn='', mode='w'):
        """Save time contents to file.

        Default filename is to use :attr:`name`. If *fn* is provided, then it
        will be used. The extension *.txt* is appended only if filename does
        not already has an extension. Using *mode* the file can be overwritten
        or appended with timing data.

        .. _`open`: https://docs.python.org/3/library/functions.html#open

        Args:
            fn (str, optional): Filename. Default is :attr:`name`.txt.
            mode (str, optional): Mode flag passed to `open`_. Default is *w*.

        Raises:
            TimerTypeError: If arguments are not strings.
            *: If arguments are not valid values, exceptions from `open`_ are
                raised.
        """
        if not isinstance(fn, str):
            raise TimerTypeError(str(fn), str)
        if not fn:
            fn = self.name if '.' in self.name else self.name + ".txt"
        with open(fn, mode) as fd:
            fd.write(", ".join(3 * ["{}"]).format("label",
                                                  "seconds",
                                                  "minutes") + "\n")
            fd.write(str(self))
