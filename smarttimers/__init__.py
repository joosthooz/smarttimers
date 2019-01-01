"""SmartTimers package.

Todo:
    Improve handling of module imports vs special attributes if using
    non-standard libraries. Currently applicable when running tox environments
    that do not include the install_requirements.txt:
        * Use try-except in __init__.py (bad hack)
        * Use explicit values in setup.py and doc/conf.py
        * Include install_requirements.txt in tox environment (e.g., doc)
"""


from .decorators import _timer, time
from .timer import Timer
from .smarttimer import SmartTimer


__all__ = [
    'SmartTimer',
    '_timer',
    'Timer',
    'time',
]


__title__ = "SmartTimers"
__name__ = "SmartTimers"
__version__ = "1.3.5"
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
