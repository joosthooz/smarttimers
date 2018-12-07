"""SmartTimer

Classes:
    :class:`SmartTimer`
"""


import cProfile
try:
    import numpy
except ImportError:
    HAS_NUMPY = False
else:
    HAS_NUMPY = True
import os
import re
import signal
import types
from collections import defaultdict
from .exceptions import (TimerError, TimerKeyError)
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

    def __init__(self, name="", **kwargs):
        self.name = name if name else self.DEFAULT_NAME
        self._timer = Timer(label="", **kwargs)  # internal Timer
        self._first_tic = None  # pointer used to calculate walltime
        self._last_tic = self._timer  # pointer used to support cascade scheme
        self._timers = []  # completed time blocks
        self._timer_stack = []  # stack of active time blocks
        self._prof = None  # profiling object

    @property
    def DEFAULT_NAME(self):
        return "smarttimer"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def labels(self):
        return [t.label for t in filter(None, self._timers)]

    @property
    def active_labels(self):
        return [t.label for t in self._timer_stack]

    @property
    def seconds(self):
        return [t.seconds for t in filter(None, self._timers)]

    @property
    def minutes(self):
        return [t.minutes for t in filter(None, self._timers)]

    @property
    def relative_percent(self):
        return [t.relative_percent for t in filter(None, self._timers)]

    @property
    def cumulative_seconds(self):
        return [t.cumulative_seconds for t in filter(None, self._timers)]

    @property
    def cumulative_minutes(self):
        return [t.cumulative_minutes for t in filter(None, self._timers)]

    @property
    def cumulative_percent(self):
        return [t.cumulative_percent for t in filter(None, self._timers)]

    @property
    def times(self):
        times_map = defaultdict(list)
        for t in filter(None, self._timers):
            times_map[t.label].append(t.seconds)
        return times_map

    def __str__(self):
        data = "{:>12}, {:>12}, {:>12}, {:>12}, {:>12}, {:>12}, {:>12}\n" \
               .format("label", "seconds", "minutes", "rel_percent",
                       "cum_sec", "cum_min",
                       "cum_percent")
        for t in filter(None, self._timers):
            data += "{:>12}, {:12.6f}, {:12.6f}, {:12.4f}, {:12.6f}, " \
                    "{:12.6f}, {:12.4f}\n" \
                    .format(t.label, t.seconds, t.minutes, t.relative_percent,
                            t.cumulative_seconds, t.cumulative_minutes,
                            t.cumulative_percent)
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
                seconds.append(self._timers[key].seconds)
            elif isinstance(key, slice):
                seconds.append(self.seconds[key])

        if not seconds:
            return None
        else:
            return seconds if len(seconds) > 1 else seconds[0]

    def _update_cumulative_and_percent(self):
        """Set cumulative and percent attributes to completed timers.

        Percent calculations are based on :attr:`seconds`.
        """
        total_seconds = sum(self.seconds)
        for i, t in enumerate(filter(None, self._timers)):
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
            TimerError, TimerKeyError: If there is not a matching :meth:`tic`.
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
        if all(self._timers):
            self._update_cumulative_and_percent()

        return t_diff.seconds

    def walltime(self):
        """Compute elapsed time in seconds between first :meth:`tic` and
        most recent :meth:`toc`.

        :meth:`walltime` >= sum(:attr:`seconds`)
        """
        if any(self._timers):
            return (self._timer.seconds - self._first_tic.seconds,
                    self._timer.minutes - self._first_tic.minutes)
        else:
            return (0., 0.)

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
        """
        # Ensure 'key' is a single level iterable to allow loop
        # processing. When an iterable or multiple keys are passed,
        # the arguments are automatically organized as a tuple of
        # tuple of values ((arg1,arg2),).
        if isinstance(keys[0], tuple):
            keys = keys[0]

        for key in keys:
            if isinstance(key, str):
                for t in filter(None, self._timers[:]):
                    if key == t.label:
                        self._timers.remove(t)
            elif isinstance(key, int):
                for i, t in enumerate(filter(None, self._timers[:])):
                    if key == i:
                        self._timers.remove(t)
            elif isinstance(key, slice):
                for t in list(filter(None, self._timers))[key]:
                    self._timers.remove(t)

    def clear(self):
        """Empty internal storage."""
        self._timers = []
        self._timer_stack = []
        self._timer.clear()
        self._first_tic = None
        self._last_tic = self._timer
        if self._prof:
            self._prof.clear()
        self._prof = None

    def reset(self):
        """Restore :attr:`name`, reset clock to default value, and empty
        internal storage."""
        self.name = self.DEFAULT_NAME
        self._timer.reset()
        self.clear()

    def dump_times(self, filename="", mode='w'):
        """Write timing results to a file.

        If *filename* is provided, then it will be used as the filename.
        Otherwise :attr:`name` is used if non-empty, else the default filename
        is used. The extension *txt* is appended only if filename does not
        already has an extension. Using *mode* the file can be overwritten or
        appended with timing data.

        .. _`open`: https://docs.python.org/3/library/functions.html#open

        Args:
            filename (str, optional): Name of file.
            mode (str, optional): Mode flag passed to `open`_. Default is *w*.
        """
        if len(filename) == 0:
            filename = self.name if self.name else self.DEFAULT_NAME
        if not os.path.splitext(filename)[1]:
            filename += ".txt"

        with open(filename, mode) as fd:
            # Remove excess whitespace used by __str__
            fd.write(re.sub(r"\s*,\s*", ",",
                     re.sub(r"^\s*|\s*$", "", str(self), flags=re.MULTILINE)))

    def stats(self, label=None):
        """Compute total, min, max, and average stats for timings.

        Note:
            * An alphanumeric label is used as a word-bounded regular
              expression.
            * A non-alphanumeric label is compared literally.
            * If *label* is 'None' then all completed timings are used.

        Args:
            label (str, iterable, optional): String used to match timer labels
                to select.

        Returns:
            `types.SimpleNamespace`_: Namespace with stats in seconds/minutes.
        """
        timers = list(filter(None, self._timers))

        # Label can be "", so explicitly check against None
        if label is None:
            seconds = self.seconds
            minutes = self.minutes
            selected = timers
        else:
            # Make strings iterate as strings, not characters
            if isinstance(label, str):
                label = [label]

            seconds = []
            minutes = []
            selected = []
            for ll in label:
                # NOTE: Extra work? Regex not always used
                label_regex = re.compile(r"\b{}\b".format(ll))
                for t in timers:
                    matched = False
                    if ll.isalnum():
                        if label_regex.search(t.label):
                            matched = True
                    elif ll == t.label:
                        matched = True
                    if matched and t not in selected:
                        seconds.append(t.seconds)
                        minutes.append(t.minutes)
                        selected.append(t)

        if selected:
            total_seconds = sum(seconds)
            total_minutes = sum(minutes)
            time_stats = {
                "total": (total_seconds, total_minutes),
                "min": (min(seconds), min(minutes)),
                "max": (max(seconds), max(minutes)),
                "avg": (total_seconds / len(seconds),
                        total_minutes / len(minutes))}
        else:
            time_stats = {"total": None, "min": None, "max": None, "avg": None}

        return types.SimpleNamespace(**time_stats)

    def sleep(self, seconds):
        """Sleep for given seconds."""
        self._timer.sleep(seconds)

    def to_array(self):
        """Return timing data as a list or numpy array (no labels).

        Data is arranged as a transposed view of :meth:`__str__` and
        :meth:`to_file` formats.

        .. _`numpy.ndarray`: https://www.numpy.org/devdocs/index.html

        Returns:
            `numpy.ndarray`_, list: Timing data.
        """
        data = [self.seconds, self.minutes, self.relative_percent,
                self.cumulative_seconds, self.cumulative_minutes,
                self.cumulative_percent]
        if HAS_NUMPY:
            return numpy.array(data)
        return data

    def pic(self, subcalls=True, builtins=True):
        """Start profiling.

        .. _`profile`: https://docs.python.org/3.3/library/profile.html

        See `profile`_
        """
        self._prof = cProfile.Profile(timer=self._timer.clock,
                                      subcalls=subcalls, builtins=builtins)
        self._prof.enable()

    def poc(self):
        """Stop profiling."""
        self._prof.disable()
        self._prof.create_stats()
        self._prof.clear()

    def print_profile(self, sort='time'):
        """Print profiling statistics."""
        self._prof.print_stats(sort)

    def get_profile(self):
        return self._prof.getstats()

    def dump_profile(self, filename="", mode='w'):
        """Write profiling results to a file.

        If *filename* is provided, then it will be used as the filename.
        Otherwise :attr:`name` is used if non-empty, else the default filename
        is used. The extension *.prof* is appended only if filename does not
        already has an extension. Using *mode* the file can be overwritten or
        appended with timing data.

        .. _`open`: https://docs.python.org/3/library/functions.html#open

        Args:
            filename (str, optional): Name of file.
            mode (str, optional): Mode flag passed to `open`_. Default is *w*.
        """
        if not filename:
            filename = self.name if self.name else self.DEFAULT_NAME
        base, ext = os.path.splitext(filename)
        if not ext:
            filename += ".prof"
        else:
            # TODO: strip extension so that it does not clashes with .txt
            pass
        # TODO: allow to append to file
        self._prof.dump_stats(filename)
