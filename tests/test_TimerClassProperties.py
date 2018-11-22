import unittest
from .utiltest import TestStack
import time
from smarttimer import Timer
from smarttimer.timer import (TimerDict,
                              TimerTypeError,
                              TimerValueError,
                              TimerKeyError)


class TimerClassPropertiesTestCase(unittest.TestCase):

    def test_TimerDict(self):
        td1 = TimerDict()
        # Invalid
        for value in [0, 0., 'clock', ['clock', time.clock],
                      ('clock', time.clock)]:
            with self.subTest(value=value):
                with self.assertRaises(TimerTypeError):
                    td1.update(value)

    def test_DefaultClockName(self):
        # Invalid
        for clock_name in [1, 1., ['clock'], ('clock',),
                           {'DEFAULT_CLOCK_NAME': 'clock'}]:
            with self.subTest(clock_name=clock_name):
                with self.assertRaises(TimerTypeError):
                    Timer.DEFAULT_CLOCK_NAME = clock_name
        TestStack.push(Timer.DEFAULT_CLOCK_NAME)
        Timer.DEFAULT_CLOCK_NAME = 'clock'
        self.assertEqual(Timer.DEFAULT_CLOCK_NAME, 'clock')
        Timer.DEFAULT_CLOCK_NAME = TestStack.pop()

    def test_Clocks(self):
        # Invalid
        for value in [1, 1., 'clock', ['clock'], ('clock',)]:
            with self.subTest(value=value):
                with self.assertRaises(TimerTypeError):
                    Timer.CLOCKS = value
        # Invalid key, valid value
        for keyval in [{1: 'clock'}, {1.: 'clock'}]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(TimerKeyError):
                    Timer.CLOCKS.update(keyval)
        # Valid key, invalid value
        for keyval in [{'clock': 1}, {'clock': 1.}, {'clock': 'clock'}]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(TimerValueError):
                    Timer.CLOCKS.update(keyval)
        # Valid
        TestStack.push(Timer.CLOCKS)
        for keyval in [{'clock': time.clock},
                       TimerDict({'clock': time.clock})]:
            Timer.CLOCKS = keyval
            with self.subTest(keyval=keyval):
                self.assertTrue(keyval.items() == Timer.CLOCKS.items())
        Timer.CLOCKS = TestStack.pop()


if __name__ == '__main__':
    unittest.main()
