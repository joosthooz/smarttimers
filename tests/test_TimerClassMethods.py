import time
import unittest
from smarttimers import Timer
from .utiltest import TestStack


class TimerClassMethodsTestCase(unittest.TestCase):

    def test_PrintClocksInfo(self):
        Timer.print_clocks()

    def test_RegisterClock(self):
        TestStack.push(Timer.CLOCKS)
        # Invalid key, valid value
        for keyval in [[1, 'clock'], [1., 'clock']]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(KeyError):
                    Timer.register_clock(*keyval)
        # Valid key, invalid value
        for keyval in [['clock', 1], ['clock', 1.], ['clock', 'clock']]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(ValueError):
                    Timer.register_clock(*keyval)
        # Valid
        Timer.register_clock('clock2', time.clock)
        self.assertTrue({'clock2': time.clock}.items() <= Timer.CLOCKS.items())
        Timer.CLOCKS = TestStack.pop()

    def test_UnregisterClock(self):
        TestStack.push(Timer.CLOCKS)
        # Invalid
        for clock_name in [1, 1., 'dummy_clock', ('clock',)]:
            with self.subTest(clock_name=clock_name):
                with self.assertRaises(KeyError):
                    Timer.unregister_clock(clock_name)
        # Valid
        Timer.unregister_clock('clock')
        self.assertFalse({'clock': time.clock}.items() <= Timer.CLOCKS.items())
        Timer.CLOCKS = TestStack.pop()


if __name__ == '__main__':
    unittest.main()
