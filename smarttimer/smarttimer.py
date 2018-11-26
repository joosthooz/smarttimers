"""SmartTimer

Classes:
    :py:class:`SmartTimer`

Todo:
    * Add time correction for tic(), toc(), toc() , ...
"""


from .timer import Timer
from .exceptions import TimerTypeError


__all__ = ['SmartTimer']


class SmartTimer:
    """Data structure for timing code blocks.

    Supports consecutive and nested timed regions:
        * Consecutive timer: tic(), toc(), ..., tic(), toc()
        * Nested timer:      tic(), tic(), ..., toc(), toc()
        * Cascade timer:     tic(), toc(), toc(), ...

    Contains time of last event and list of all events (supports indexing).
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
        time_map = {}
        for k, v in zip(self.labels, self.seconds):
            if k is None:
                continue
            if k not in time_map:
                time_map[k] = [v]
            else:
                time_map[k].append(v)
        return time_map

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
            * Remove from timers, not stack

        Note:
            * If key is string, then consider it as a label
            * If key is integer, then consider it as an index
            * If key is dict, then dict.key is used as the actual key
            * Key can be an iterable of integers and/or strings

        Example:
            timer[4, 2]
            timer['I/O', 'Processing']
            timer[2, 'Processing']
            timer[1:2, 4:6]
            timer[['I/O', 'Processing'], [1,2]]
        """
        seconds = []
        try:
            for key in keys:
                # Ensure 'key' is a single level iterable to allow loop
                # processing. When an iterable or multiple keys are passed,
                # the arguments are automatically organized as a tuple of
                # tuple of values ((arg1,arg2),).
                # Handle single strings because they are iterable.
                if not hasattr(key, '__iter__') or isinstance(key, str):
                    key = [key]

                for k in key:
                    if isinstance(k, slice):
                        seconds.append(self.seconds[k])
                    elif isinstance(k, int):
                        seconds.append(self._timers[k].seconds)
                    elif isinstance(k, str):
                        for t in self._timers:
                            if t is None:
                                continue
                            if k == t.label:
                                seconds.append(t.seconds)
                    else:
                        raise KeyError('Invalid key \'{}\' for {} '
                                       'object'.format(key, repr(self)))
        except (IndexError, ValueError) as ex:
            print(ex)

        if not seconds:
            return None
        else:
            return seconds if len(seconds) > 1 else seconds[0]

    def remove(self, *keys):
        """Remove a Timer.
        Note:
            * Remove from timers, not stack

        Note:
            * If key is string, then consider it as a label
            * If key is integer, then consider it as an index
            * If key is dict, then dict.key is used as the actual key
            * Key can be an iterable of integers and/or strings
        """
        try:
            for key in keys:
                # Ensure 'key' is a single level iterable to allow loop
                # processing. When an iterable or multiple keys are passed,
                # the arguments are automatically organized as a tuple of
                # tuple of values ((arg1,arg2),).
                # Handle single strings because they are iterable.
                if not hasattr(key, '__iter__') or isinstance(key, str):
                    key = [key]

                for k in key:
                    if isinstance(k, slice):
                        for t in self._timers[key]:
                            self._timers.remove(t)
                    elif isinstance(k, int):
                        self._timers.remove(self._timers[k])
                    elif isinstance(k, str):
                        # Need a copy of _timers because it is modified
                        for t in self._timers[:]:
                            if t is None:
                                continue
                            if k == t.label:
                                self._timers.remove(t)
                    else:
                        raise KeyError('Invalid key \'{}\' for {} '
                                       'object'.format(key, repr(self)))
        except (IndexError, ValueError) as ex:
            print(ex)

    def clear(self):
        """Set time values to zero."""
        self._timers = []
        self._timer_stack = []
        self._timer.clear()
        self._last_tic = self._timer

    def walltime(self):
        """Compute walltime in seconds.

        Throws exception if there are active timers.
        """
        return sum(self.seconds)

    def tic(self, key=''):
        """Start measuring time.

        Create Timer and use as reference for _last_tic.
        First insert Timer into stack, then measure time to minimize noise.
        """
        self._last_tic = t = Timer(label=key)
        self._timer_stack.append(t)
        t.time()

    def toc(self, key=None):
        """Stop measuring time.

        Measure time at the soonest moment possible to not include internal
        processing tasks.
        """
        # No-op, if no tic() has been invoked previously
        # _last_tic -> _timer
        if self._last_tic is self._timer:
            return None

        # Record time
        self._timer.time()

        # There is a matching tic(), if stack is not empty
        if self._timer_stack:
            t_first = self._timer_stack.pop()
            t_diff = self._timer - t_first

            # Find index to place current timer
            #   * Find last 'None' position
            #   * Find last position considering completed and active timers
            if None in self._timers:
                idx = len(self._timers) - self._timers[::-1].index(None) - 1
            else:
                # tic-toc pair or inner-most from nested timers
                idx = len(self._timers) + len(self._timer_stack)

            #  * For nested regions, insert 'None' in positions until index of
            #    inner timer
            #  * tic-toc() pair
            if idx >= len(self._timers):
                for k in range(len(self._timers), idx):
                    self._timers.append(None)
                self._timers.append(t_diff)

            # Inner-most timer of nested regions
            else:
                self._timers[idx] = t_diff

        # Empty stack
        # _last_tic -> timer from last tic()
        else:
            t_diff = self._timer - self._last_tic
            self._timers.append(t_diff)

        self._timer.clear()  # clear internal Timer
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
