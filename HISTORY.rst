.. _`time`: https://docs.python.org/3/library/time.html
.. _`time.get_clock_info`:
    https://docs.python.org/3/library/time.html#time.get_clock_info


HISTORY
=======

v0.9.0
------

:Date: 2018-11-26

Features:
    * SmartTimer: time lists maintain ordering relative to tic() calls.
    * SmartTimer: support for consecutive, nested, cascade, interleaved, and
      key-paired code blocks.
    * Improved error handling and exceptions raised.

Bug fixes:
    * SmartTimer: changed times() to use new labels() output format.


v0.8.5
------

:Date: 2018-11-25

Features
    * SmartTimer: implemented container for tic-toc support.
    * Improved module dependencies for setup, tests, and docs.
    * Code style is compliant with flake8.


v0.6.0
------

:Date: 2018-11-22

Features
    * Timer: time values are read-only.
    * Timer: new clear, reset, (un)register_clock methods.
    * Timer: new custom exception classes and improved exception handling.
    * Timer: rename sum, print_info, and print_clocks methods.
    * Timer: complete documentation.
    * Timer: complete test cases.
    * Integrated tox, Travis CI, code coverage, and Read the Docs.
    * Cleaned code adhering to flake8.


v0.4.0
------

:Date: 2018-11-19

Features
    * Timer: new print/get_clock_info methods.
    * Timer: improved compatibility checks.
    * Timer: new TimerCompatibilityError exception.
    * Timer: documentation revision.


v0.3.0
------

:Date: 2018-11-18

Features
    * Timer: include an example script.
    * Timer: new MetaTimerProperty and TimerDict for handling class variable
      properties.
    * Timer: improved exception coverage.
    * Timer: improved methods for checking compatibility and print clock info.
    * Timer: time values are cleared automatically when clock name is changed.


v0.2.2
------

:Date: 2018-11-18

Features
    * Timer: new methods to print clock details using `time.get_clock_info`_.
    * Timer: updated docstrings and provide usage examples.


v0.2.0
------

:Date: 2018-11-17

Features
    * Timer: new methods to support sum, difference, and comparison operators.
    * Timer: new methods to check compatibility between Timers.


v0.1.0
------

:Date: 2018-11-15

Features
    * Created Timer class with timing functions from standard module `time`_.
    * Ubuntu 16.04 (Linux 4.15.0-38) support.
