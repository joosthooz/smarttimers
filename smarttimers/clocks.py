"""Utilities to manage system and custom clocks/counters."""


__all__ = [
    'CLOCKS',
    'ClockInfo',
    'print_clock',
    'print_clocks',
    'get_clock_info',
    'register_clock',
    'unregister_clock',
    'are_clocks_compatible',
    'is_clock_function_valid'
    ]


import os
import sys
import textwrap
import time as std_time
from numbers import Number
from collections import namedtuple, OrderedDict


# Predefined clocks 
#  process_time: process-wide
#  thread_time: thread-wide
#  perf_counter: system-wide
#  monotonic: system-wide
#  time: system-wide
#  clock: depends on implementation, deprecated
if sys.version_info >= (3, 7):
    CLOCKS = OrderedDict((
        ("process_time", std_time.process_time),
        ("thread_time", std_time.thread_time),
        ("perf_counter", std_time.perf_counter),
        ("monotonic", std_time.monotonic),
        ("time", std_time.time),
        ("clock", std_time.clock)
        ))
else:
    CLOCKS = OrderedDict((
        ("process_time", std_time.process_time),
        ("perf_counter", std_time.perf_counter),
        ("monotonic", std_time.monotonic),
        ("time", std_time.time),
        ("clock", std_time.clock)
        ))

# Structure used to represent clock attributes.
_ClockInfo_fields = ('function', *vars(std_time.get_clock_info('time')))
if sys.version_info >= (3, 7):
    ClockInfo = namedtuple('ClockInfo', _ClockInfo_fields,
                           defaults=len(_ClockInfo_fields) * (None,))
else:
    ClockInfo = namedtuple('ClockInfo', _ClockInfo_fields)
    ClockInfo.__new__.__defaults__ = len(_ClockInfo_fields) * (None,)

# Map of clock name to clock attributes, dict of dicts.
_CLOCKS_INFO = {}

def get_clock_info(clock_name):
    # Check local structure in case even a standard clock name has been
    # overwritten.
    if clock_name in _CLOCKS_INFO:
        return ClockInfo(function=CLOCKS[clock_name],
                         **_CLOCKS_INFO[clock_name])
    return ClockInfo(function=CLOCKS[clock_name],
                     **vars(std_time.get_clock_info(clock_name)))

def are_clocks_compatible(clock_name1, clock_name2):
    # [1:] to skip 'function' attribute.
    return get_clock_info(clock_name1)[1:] == get_clock_info(clock_name2)[1:]

def is_clock_function_valid(clock_function):
    # Check that clock function returns a number.
    # If function requires arguments to work correctly, then ignore
    # validation and assume function is valid.
    clock_value = 0.
    try:
        clock_value = clock_function()
    except Exception as ex:
        pass
    return isinstance(clock_value, Number)
 
def register_clock(clock_name, clock_function, **kwargs):
    if not is_clock_function_valid(clock_function):
        raise ValueError("clock function to register, '{}', does not returns a"
                         " numeric value".format(clock_function.__qualname__))
    CLOCKS[clock_name] = clock_function
    kwargs['implementation'] = kwargs.get('implementation', clock_function)
    _CLOCKS_INFO[clock_name] = kwargs

def unregister_clock(clock_name):
    CLOCKS.pop(clock_name)
    if clock_name in _CLOCKS_INFO:
        _CLOCKS_INFO.pop(clock_name)

def print_clock(clock_name):
    print(textwrap.dedent(
          """\
          '{clock_name}'
              function      : {info.function}
              adjustable    : {info.adjustable}
              implementation: {info.implementation}
              monotonic     : {info.monotonic}
              resolution    : {info.resolution}\
          """
          ).format(clock_name=clock_name, info=get_clock_info(clock_name)),
          end=2 * os.linesep)

def print_clocks():
    for clock_name in CLOCKS:
        print_clock(clock_name)
