#!/usr/bin/env python3

"""SmartTimer

Classes:

    SmartTimer
"""


import numpy
from .timer import Timer


__all__ = ['SmartTimer']


class SmartTimer:
    """Timer that tracks multiple timed regions.

    Supports consecutive and nested timed regions.
    Consecutive timer: tic(), toc(), ..., tic(), toc()
    Nested timer:      tic(), tic(), ..., toc(), toc()

    Contains time of last event and list of all events (supports indexing).

    Todo:
        * Use id attribute
    """
    def __init__(self, id='', **kwargs_t):
        self.id = id
        self._timers = []
        self._timer_stack = []  # stack of Time objects for active code blocks
        self._kwargs_t = kwargs_t

    @property
    def timers(self):
        return self._timers

    def get_times(self, key=slice(None)):
        """Return times as Numpy array.
        """
        if not self.timers:
            return numpy.empty(shape=0)

        data = self.timers[key]
        times = numpy.empty(shape=(len(data), 2))
        for i, t in enumerate(data):
            times[i] = t.seconds, t.minutes
        return times

    def __enter__(self):
        """
        Measure time at the latest moment possible to not include internal
        processing tasks.
        """
        self.tic()
        return self

    def __exit__(self, *args):
        """
        Measure time at the soonest moment possible to not include internal
        processing tasks.
        """
        self.toc()

    def __str__(self):
        return '\n'.join([t.__str__() for t in self.timers])

    def __getitem__(self, *keys):
        """Use dictionary syntax to access time in seconds

        The values returned correspond to the time in seconds.
        Multiple values are returned as a list, generally in the same order
        as the given keys (except for cases where duplicate labels exist).

        Todo:
            * Fix this method, support slices

        Notes:
            * If key is string, then consider it as a label
            * If key is integer, then consider it as an index
            * Key can be an iterable of integers and/or strings

        Example:
            timer[4, 2]
            timer['I/O', 'Processing']
            timer['I/O', 2]
        """
        data = []
        for key in keys:
            try:
                if isinstance(key, slice):
                    return self.timers

                else:
                    # Ensure 'key' is a single level iterable to allow loop processing.
                    # When an iterable or multiple keys are passed, the arguments are
                    # automatically organized as a tuple of tuple of values
                    # ((arg1,arg2),)
                    if not hasattr(key, '__iter__'):
                        key = [key]

                    # str, int: returns a list of Timers [t1,t2,...]
                    if all(isinstance(k, str) for k in key):
                        data = [self.timers[i] for i, k in enumerate(key) if k == self.timers[i].id]
                    elif all(isinstance(k, int) for k in key):
                        data = [self.timers[k] for k in key]
                    else:
                        raise KeyError('Invalid key \'{}\' for {} '
                                       'object'.format(key, repr(self)))
            except (IndexError, ValueError) as ex:
                print(ex)

        # Return the items when there is only a single item
        # This is important for supporting vector arithmetic.
        if len(data) == 1: data = data[0]

        return data

    def __add__(self, other):
        return self.walltime() + other.walltime()

    def remove(self, key):
        """Remove a Timer.
        Note:
            * Remove from timers, not stack
        """
        if isinstance(key, int):
            self.timers.remove(self.timers[key])
        elif isinstance(key, str):
            for t in self[key]:
                self.timers.remove(t)

    def clear():
        pass

    def walltime(self):
        """
        Compute walltime by adding all timings measured.
        Walltime is computed on-demand because it is not expected to be
        invoked multiple times, so to reduce internal processing tasks, a
        running sum is not used.
        """
        return sum([t.seconds for t in self.timers])

    def tic(self, key=''):
        t1 = Timer(id=key, **self._kwargs_t)
        t1.time()
        self._timer_stack.append(t1)

    def toc(self, key=''):
        """
        Measure time at the soonest moment possible to not include internal
        processing tasks.

        Todo:
            * Use label parameter to provide control of what it is paired with
        """
        t2 = Timer(id=key, **self._kwargs_t)
        t2.time()
        tdiff = t2 - self._timer_stack.pop()
        self.timers.append(tdiff)

        return tdiff.seconds

    def print_info(self):
        if self.timers:
            self.timers[0].print_info()
