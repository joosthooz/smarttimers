from smarttimers import (SmartTimer, TimerTypeError, TimerValueError)
import unittest


class SmartTimerInstancePropertiesTestCase(unittest.TestCase):

    def test_Name(self):
        # Valid
        t = SmartTimer()
        t.name = 'atimer'
        self.assertEqual(t.name, 'atimer')
        # Invalid type
        for nameval in [1, 1., ['atimer'], ('atimer',), {'atimer': 1}, None]:
            with self.subTest(nameval=nameval):
                with self.assertRaises(TimerTypeError):
                    t.name = nameval
        # Invalid value
        with self.assertRaises(TimerValueError):
            t.name = ''
        with self.assertRaises(TimerValueError):
            t = SmartTimer(name='')


if __name__ == '__main__':
    unittest.main()
