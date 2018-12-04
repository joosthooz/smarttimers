"""SmartTimers package.

Todo:
    Improve handling of module imports vs special attributes if using
    non-standard libraries. Currently applicable when runnign tox environments
    that do not include the install_requirements.txt:
        * Use try-except in __init__.py (bad hack)
        * Use explicit values in setup.py and doc/conf.py
        * Include install_requirements.txt in tox environment (e.g., doc)
"""


from .exceptions import (TimerCompatibilityError, TimerError, TimerKeyError,
                         TimerTypeError, TimerValueError)
from .smarttimer import SmartTimer
from .timer import (Timer, TimerDict)


__all__ = [
    'SmartTimer',
    'Timer',
    'TimerCompatibilityError',
    'TimerDict',
    'TimerError',
    'TimerKeyError',
    'TimerTypeError',
    'TimerValueError'
]


__title__ = "SmartTimers"
__name__ = "SmartTimers"
__version__ = "1.3.0"
__description__ = "Timing library with a simple and flexible API for " \
                  "measuring a variety of consecutive and nested code blocks."
__keywords__ = [
    "timer",
    "profiling",
    "runtime",
    "measurement",
    "performance"
]
__url__ = "https://github.com/edponce/smarttimers"
__author__ = "Eduardo Ponce, The University of Tennessee, Knoxville, TN"
__author_email__ = "edponce2010@gmail.com"
__license__ = "MIT"
__copyright__ = "2018 Eduardo Ponce"
