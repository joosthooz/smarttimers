"""SmartTimer

Classes:
    :py:class:`SmartTimer`
"""


from smarttimers.exceptions import (TimerTypeError, TimerKeyError)
from smarttimers.timer import Timer


__all__ = ['SmartTimer']


class SmartTimer:
    """Manager of :py:class:`Timer` measurements for code blocks.

    Supports the following schemes of timed blocks:
        * Consecutive: tic(), toc(), ..., tic(), toc()
        * Nested: tic(), tic(), ..., toc(), toc()
        * Cascade: tic(), toc(), toc(), ...
        * Nested interleaved: tic(), tic(), toc(), tic(), ..., toc(), toc()
        * Key-paired: tic('outer'), tic('inner'), ..., toc('outer'), toc()
    """
    def __init__(self, name='smarttimer', **kwargs):
        self._name = name
        self._timers = []  # list of Timers for completed time blocks
        self._timer_stack = []  # stack of Timers for active time blocks

        # Remove 'label', not needed for internal timer
        if 'label' in kwargs:
            del kwargs['label']

        # _timer: Internal Timer to record time
        # _last_tic: Pointer used to support cascade scheme
        self._last_tic = self._timer = Timer(**kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TimerTypeError('name', str)
        self._name = name

    @property
    def labels(self):
        """Lists of time labels for completed blocks.

        Returns:
            list: Labels of completed blocks.
        """
        return [t.label if t else t for t in self._timers]

    @property
    def active_labels(self):
        """Lists of time labels for active blocks.

        Returns:
            list: Labels of blocks without a matching toc().
        """
        return [t.label for t in self._timer_stack]

    @property
    def seconds(self):
        """List of seconds elapsed for completed blocks.

        Returns:
            list: Time in seconds.
        """
        return [t.seconds if t else t for t in self._timers]

    @property
    def minutes(self):
        """List of minutes elapsed for completed blocks.

        Returns:
            list: Time in minutes.
        """
        return [t.minutes if t else t for t in self._timers]

    @property
    def times(self):
        """Dictionary of times elapsed for completed blocks.

        Returns:
            list: Keys are labels and values list of time in seconds.
        """
        times_map = {}
        for t in self._timers:
            if t is not None:
                if t.label not in times_map:
                    times_map[t.label] = [t.seconds]
                else:
                    times_map[t.label].append(t.seconds)
        return times_map

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, *args):
        self.toc()

    def __str__(self):
        return '\n'.join([t.__str__() for t in self._timers]) + '\n'

    def __getitem__(self, *keys):
        """Use dictionary syntax to access time in seconds

        The values returned correspond to the time in seconds.
        Multiple values are returned as a list, generally in the same order
        as the given keys (except for cases where duplicate labels exist).

        Note:
            * If key is string, then consider it as a label
            * If key is integer or slice, then consider it as an index
            * Key types can be mixed

        Example:
            timer[4, 2]
            timer['I/O', 'Processing']
            timer[2, 'Processing']
            timer[1:2, 4:6]
        """
        # Ensure 'key' is a single level iterable to allow loop
        # processing. When an iterable or multiple keys are passed,
        # the arguments are automatically organized as a tuple of
        # tuple of values ((arg1,arg2),).
        if isinstance(keys[0], tuple):
            keys = keys[0]

        seconds = []
        for key in keys:
            try:
                if isinstance(key, slice):
                    seconds.append(self.seconds[key])
                elif isinstance(key, int):
                    seconds.append(self._timers[key].seconds)
                elif isinstance(key, str):
                    seconds.extend(self.times[key])
                else:
                    raise TimerTypeError(str(key), 'str, int, or slice')
            except (IndexError, ValueError):
                raise TimerKeyError(str(key), 'valid index')

        if not seconds:
            return None
        else:
            return seconds if len(seconds) > 1 else seconds[0]

    def remove(self, *keys):
        """Remove a :py:class:`Timer`.

        Note:
            * Remove from timers, not stack
            * If key is string, then consider it as a label
            * If key is integer or slice, then consider it as an index
            * Key types can be mixed
        """
        # Ensure 'key' is a single level iterable to allow loop
        # processing. When an iterable or multiple keys are passed,
        # the arguments are automatically organized as a tuple of
        # tuple of values ((arg1,arg2),).
        if isinstance(keys[0], tuple):
            keys = keys[0]

        for key in keys:
            try:
                if isinstance(key, slice):
                    # Slice produces a copy of _timers, original is modified
                    for t in self._timers[key]:
                        self._timers.remove(t)
                elif isinstance(key, int):
                    self._timers.remove(self._timers[key])
                elif isinstance(key, str):
                    # Slice produces a copy of _timers, original is modified
                    for t in self._timers[:]:
                        if t is not None:
                            if key == t.label:
                                self._timers.remove(t)
                else:
                    raise TimerTypeError(str(key), 'str, int, or slice')
            except (IndexError, ValueError):
                raise TimerKeyError(str(key), 'valid index')

    def clear(self):
        """Set time values to zero."""
        self._timers = []
        self._timer_stack = []
        self._timer.clear()
        self._last_tic = self._timer

    def walltime(self):
        """Compute walltime in seconds.

        Only supported when all timers have completed, else error occurs.
        """
        return sum(self.seconds)

    def tic(self, key=''):
        """Start measuring time.

        Measure time at the latest moment possible to not minimize noise from
        internal operations.
        """
        # Create Timer
        # _last_tic -> timer of most recent tic
        self._last_tic = t = Timer(label=key)

        # First insert Timer into stack, then record time to minimize noise.
        # This can be done because 't' is a reference.
        self._timer_stack.append(t)

        # Use 'None' as an indicator of active timers
        self._timers.append(None)

        # Record time
        t.time()

    def toc(self, key=None):
        """Stop measuring time.

        Measure time at the soonest moment possible to not minimize noise from
        internal operations.

        Note:
            * In cascade regions, that is, multiple toc() calls, some noise
              will be introduced. There is the possibility of correcting this
              noise, but even the correction is noise itself.
        """
        # Record time
        self._timer.time()

        # Raise error if key is used incorrectly, not str or non-existing pair
        if key is not None:
            if not isinstance(key, str):
                raise TimerTypeError(str(key), str)
            elif not self._timer_stack:
                raise TimerKeyError(str(key), 'matched pair')

        # No-op, if no tic pair (e.g., toc() after instance creation)
        # _last_tic -> _timer
        if self._last_tic is self._timer:
            return None

        # Stack is not empty so there is a matching tic
        if self._timer_stack:

            # Last item or item specified by key
            stack_idx = -1

            # Key-paired timer
            if key is not None:
                # Find index of last timer in stack with matching key
                for i, t in enumerate(self._timer_stack[::-1]):
                    if key == t.label:
                        stack_idx = len(self._timer_stack) - i - 1
                        break
                else:
                    raise TimerKeyError(str(key), 'matched pair')

            # Measure time elapsed
            t_first = self._timer_stack.pop(stack_idx)
            t_diff = self._timer - t_first

            # Place time in corresponding position
            idx = [i for i, v in enumerate(self._timers)
                   if v is None][stack_idx]
            self._timers[idx] = t_diff

        # Empty stack, use _last_tic -> timer from most recent tic
        else:
            t_diff = self._timer - self._last_tic
            self._timers.append(t_diff)

        return t_diff.seconds

    def print_info(self):
        self._timer.print_info()

    def write_to_file(self, fn='', flag='w'):
        """Save timer contents to a file.

        The *flag* argument controls if the file is overwritten or append.
        """
        if not fn:
            fn = self.name if '.' in self.name else self.name + '.time'
        with open(fn, flag) as fd:
            fd.write(self.__str__())
