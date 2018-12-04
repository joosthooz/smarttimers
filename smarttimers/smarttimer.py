"""SmartTimer

Classes:
    :class:`SmartTimer`
"""


# Check numpy for 'to_array()'
try:
    import numpy
except ImportError:
    HAS_NUMPY = False
else:
    HAS_NUMPY = True
import re
import types
from collections import defaultdict
from .exceptions import (TimerError, TimerKeyError, TimerTypeError,
                         TimerValueError)
from .timer import Timer


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

    def __init__(self, name="smarttimer", **kwargs):
        self.name = name
        self._timer = Timer(label="", **kwargs)  # internal Timer
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
            raise TimerTypeError("name '{}' is not a {}".format(name, str))
        if not name:
            raise TimerValueError("name '{}' is not a non-empty string"
                                  .format(name))
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
    def relative_percent(self):
        return [t.relative_percent if t else t for t in self._timers]

    @property
    def cumulative_seconds(self):
        return [t.cumulative_seconds if t else t for t in self._timers]

    @property
    def cumulative_minutes(self):
        return [t.cumulative_minutes if t else t for t in self._timers]

    @property
    def cumulative_percent(self):
        return [t.cumulative_percent if t else t for t in self._timers]

    @property
    def times(self):
        times_map = defaultdict(list)
        for t in filter(None, self._timers):
            times_map[t.label].append(t.seconds)
        return times_map

    def __str__(self):
        data = "{:>12}, {:>12}, {:>12}, {:>12}, {:>12}, {:>12}, {:>12}\n" \
               .format("label", "seconds", "minutes", "rel_percent",
                       "cumul_sec", "cumul_min",
                       "cumul_percent")
        for t in self._timers:
            if t:
                data += "{:>12}, {:12.6f}, {:12.6f}, {:12.4f}, {:12.6f}, " \
                        "{:12.6f}, {:12.4f}\n" \
                        .format(t.label, t.seconds, t.minutes,
                                t.relative_percent, t.cumulative_seconds,
                                t.cumulative_minutes, t.cumulative_percent)
        return data

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, *args):
        self.toc()

    def __getitem__(self, *keys):
        """Query time(s) of completed code blocks.

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
                raise TimerKeyError("key '{}' is not a {}, {}, or {}"
                                    .format(key, str, int, slice))

        if not seconds:
            return None
        else:
            return seconds if len(seconds) > 1 else seconds[0]

    def _update_cumulative_and_percent(self):
        """Set cumulative and percent attributes to completed timers.

        Percent calculations are based on :attr:`seconds`.
        """
        total_seconds = sum(self.seconds)
        for i, t in enumerate(self._timers):
            # Skip timers already processed, only update percentages
            if t.cumulative_seconds < 0. or t.cumulative_minutes < 0.:
                t.cumulative_seconds = t.seconds
                t.cumulative_minutes = t.minutes
                if i > 0:
                    t_prev = self._timers[i - 1]
                    t.cumulative_seconds += t_prev.cumulative_seconds
                    t.cumulative_minutes += t_prev.cumulative_minutes
            t.relative_percent = t.seconds / total_seconds
            t.cumulative_percent = t.cumulative_seconds / total_seconds

    def tic(self, label=""):
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

        Note:
            In cascade regions, that is, multiple toc() calls, O(ms) noise will
            be introduced. In a future release, there is the possibility of
            correcting this noise, but even the correction is noise itself.

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
            raise TimerError("'toc()' has no matching 'tic()'")

        # Measure time at the soonest moment possible to minimize noise from
        # internal operations.
        self._timer.time()

        # Stack is not empty so there is a matching tic
        if self._timer_stack:

            # Last item or item specified by label
            stack_idx = -1

            # Label-paired timer
            if label is not None:
                if not isinstance(label, str):
                    raise TimerTypeError("label '{}' is not a {}".format(label,
                                                                         str))

                # Find index of last timer in stack with matching label
                for i, t in enumerate(self._timer_stack[::-1]):
                    if label == t.label:
                        stack_idx = len(self._timer_stack) - i - 1
                        break
                else:
                    raise TimerKeyError("label '{}' has no matching label"
                                        .format(label))

            # Calculate time elapsed
            t_first = self._timer_stack.pop(stack_idx)
            t_diff = self._timer - t_first

            # Add extra attributes, use a negative sentinel value
            t_diff.relative_percent = -1.
            t_diff.cumulative_seconds = -1.
            t_diff.cumulative_minutes = -1.
            t_diff.cumulative_percent = -1.

            # Place time in corresponding position
            idx = [i for i, v in enumerate(self._timers)
                   if v is None][stack_idx]
            self._timers[idx] = t_diff

        # Empty stack, use _last_tic -> timer from most recent tic
        else:
            t_diff = self._timer - self._last_tic

            # Add extra attributes, use a negative sentinel value
            t_diff.relative_percent = -1.
            t_diff.cumulative_seconds = -1.
            t_diff.cumulative_minutes = -1.
            t_diff.cumulative_percent = -1.

            # Use label
            if label is not None:
                t_diff.label = label

            self._timers.append(t_diff)

        # Update cumulative and percent times when all timers have completed
        if None not in self._timers:
            self._update_cumulative_and_percent()

        return t_diff.seconds

    def walltime(self):
        """Compute elapsed time in seconds between first :meth:`tic` and
        most recent :meth:`toc`.

        :meth:`walltime` >= sum(:attr:`seconds`)
        """
        return (self._timer.seconds - self._first_tic.seconds,
                self._timer.minutes - self._first_tic.minutes)

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
                raise TimerKeyError("key '{}' is not a {}, {}, or {}"
                                    .format(key, str, int, slice))

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

    def to_file(self, fn="", mode='w'):
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
            raise TimerTypeError("filename '{}' is not a {}".format(fn, str))
        if not fn:
            fn = self.name if '.' in self.name else self.name + ".txt"

        # Remove excess whitespace
        data = re.sub(r"^\s*", "", str(self), flags=re.MULTILINE)
        data = re.sub(r",\s*", ",", data)
        with open(fn, mode) as fd:
            fd.write(data)

    def stats(self, label=None):
        """Compute min, max, and average stats for timings.

        Args:
            label (str, optional): Label or subword to match timer labels to
                select. If set to None then all completed timings are used.

        Returns:
            `types.SimpleNamespace`_: Namespace with stats in seconds/minutes.

        Raises:
            TimerKeyError: If *label* is not a string.
        """
        if label is None:
            seconds = self.seconds
            minutes = self.minutes
        else:
            if not isinstance(label, str):
                raise TimerTypeError("label '{}' is not a {}"
                                     .format(label, str))

            # Filter data based on label
            label_filt = re.compile(r"\b{}\b".format(label))
            seconds = [t.seconds for t in self._timers
                       if label_filt.search(t.label)]
            minutes = [t.minutes for t in self._timers
                       if label_filt.search(t.label)]

        timer_stats = {
            "total": (sum(seconds), sum(minutes)),
            "min": (min(seconds), min(minutes)),
            "max": (max(seconds), max(minutes)),
            "avg": (sum(seconds) / len(seconds), sum(minutes) / len(minutes))}
        return types.SimpleNamespace(**timer_stats)

    def sleep(self, seconds):
        """Sleep for given seconds."""
        self._timer.sleep(seconds)

    def to_array(self):
        """Return timing data as a numpy array or list of lists (no labels).

        Data is arranged as a transposed view of :meth:`__str__` and
        :meth:`to_file` formats.

        .. _`numpy.ndarray`: https://www.numpy.org/devdocs/index.html

        Returns:
            `numpy.ndarray`_, list of lists: Timing data.
        """
        data = [self.seconds, self.minutes, self.relative_percent,
                self.cumulative_seconds, self.cumulative_minutes,
                self.cumulative_percent]

        if HAS_NUMPY:
            data = numpy.array(data)
        return data
