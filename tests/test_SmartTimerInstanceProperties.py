import unittest
from smarttimers import (SmartTimer, TimerTypeError, TimerValueError)


class SmartTimerInstancePropertiesTestCase(unittest.TestCase):

    def test_Name(self):
        t = SmartTimer()
        t.name = 'atimer'
        self.assertEqual(t.name, 'atimer')
        for nameval in [1, 1., ['atimer'], ('atimer',), {'atimer': 1}, None]:
            with self.subTest(nameval=nameval):
                t.name = nameval
                self.assertEqual(t.name, nameval)


if __name__ == '__main__':
    unittest.main()
