import unittest
from .utiltest import TestStack
import time
from smarttimer import Timer
from smarttimer.timer import (TimerDict,
                              TimerTypeError,
                              TimerValueError,
                              TimerKeyError,
                              TimerCompatibilityError)


class TimerClassMethodsTestCase(unittest.TestCase):

    def test_PrintClocksInfo(self):
        Timer.print_clocks()

    def test_RegisterClock(self):
        # Invalid key, valid value
        for keyval in [[1, 'clock'], [1., 'clock']]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(TimerKeyError):
                    Timer.register_clock(*keyval)
        # Valid key, invalid value
        for keyval in [['clock', 1], ['clock', 1.], ['clock', 'clock']]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(TimerValueError):
                    Timer.register_clock(*keyval)
        # Valid
        TestStack.push(Timer.CLOCKS)
        Timer.register_clock('dup_clock', time.clock)
        self.assertTrue({'dup_clock': time.clock}.items() <= \
                        Timer.CLOCKS.items())
        Timer.CLOCKS = TestStack.pop()

    def test_UnregisterClock(self):
        # Invalid
        for clock_name in [1, 1., 'dummy_clock', ['clock'], ('clock',), \
            {'clock': time.clock}]:
            with self.subTest(clock_name=clock_name):
                with self.assertRaises(TimerKeyError):
                    Timer.unregister_clock(clock_name)
        # Valid
        TestStack.push(Timer.CLOCKS)
        Timer.unregister_clock('clock')
        self.assertFalse({'clock': time.clock}.items() <= Timer.CLOCKS.items())
        Timer.CLOCKS = TestStack.pop()


if __name__ == '__main__':
    unittest.main()
