"""SmartTimer module.

Todo:
    * Improve handling of imports vs special methods:
        * Use try-except in __init__.py (not ideal)
        * Use explicit values in setup.py and docs/conf.py
        * Import required modules at top of setup.py and docs/conf.py
"""


# Allow ingesting this file when accessing special attributes only.
try:
    from .timer import Timer
    from .smarttimer import SmartTimer
    from .exceptions import (TimerException, TimerTypeError, TimerValueError,
                             TimerKeyError, TimerCompatibilityError)

    __all__ = [
        'Timer',
        'SmartTimer',
        'TimerException',
        'TimerTypeError',
        'TimerValueError',
        'TimerKeyError',
        'TimerCompatibilityError'
    ]
except ImportError:
    pass


__title__ = "SmartTimer"
__name__ = "SmartTimer"
__version__ = "0.9.0"
__description__ = "SmartTimer library"
__keywords__ = [
    "time",
    "profiling",
    "walltime"
]
__url__ = "https://github.com/edponce/smarttimers"
__author__ = "Eduardo Ponce, The University of Tennessee, Knoxville, TN"
__author_email__ = "edponce2010@gmail.com"
__license__ = "MIT"
__copyright__ = "2018 Eduardo Ponce"
