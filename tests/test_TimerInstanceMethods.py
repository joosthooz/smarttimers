import time
import types
import unittest
from smarttimers import (Timer, TimerTypeError, TimerValueError)
from .utiltest import TestStack


# Custom timing function
def constant_time():
    return 1.


class TimerInstanceMethodsTestCase(unittest.TestCase):

    def test_Str(self):
        t1 = Timer()
        print(t1)
        t2 = Timer('timer2')
        print(t2)

    def test_InitDefaultArgs(self):
        t = Timer()
        self.assertEqual(t.label, '')
        self.assertEqual(t.seconds, 0.)
        self.assertEqual(t.minutes, 0.)
        self.assertEqual(t.clock_name, Timer.DEFAULT_CLOCK_NAME)

    def test_InitUserArgs(self):
        # Invalid
        for value in ['0.', [0.], (0.,), {0: 0}]:
            with self.subTest(value=value):
                with self.assertRaises(TimerTypeError):
                    t = Timer(seconds=value)
        with self.assertRaises(TimerValueError):
            t = Timer(seconds=-1.)
        # Valid
        t = Timer('timer1', seconds=10.5, clock_name='clock')
        self.assertEqual(t.label, 'timer1')
        self.assertEqual(t.seconds, 10.5)
        self.assertAlmostEqual(t.minutes, 10.5 / 60.)
        self.assertEqual(t.clock_name, 'clock')

    def test_InitOtherTimer(self):
        t = Timer('timer1')
        t.time()
        t2 = Timer('timer2', timer=t)
        self.assertNotEqual(t.label, t2.label)
        self.assertEqual(t.seconds, t2.seconds)
        self.assertEqual(t.minutes, t2.minutes)
        self.assertEqual(t.clock_name, t2.clock_name)

    def test_RecordTime(self):
        t = Timer()
        t.time()
        self.assertEqual(t.label, '')
        self.assertGreater(t.seconds, 0.)
        self.assertGreater(t.minutes, 0.)
        self.assertEqual(t.clock_name, Timer.DEFAULT_CLOCK_NAME)

    def test_Clear(self):
        # Assumes 'process_time' is a valid clock and not the default one.
        t = Timer('timer1', clock_name='process_time')
        t.time()
        t.clear()
        self.assertEqual(t.label, 'timer1')
        self.assertEqual(t.seconds, 0.)
        self.assertEqual(t.minutes, 0.)
        self.assertNotEqual(t.clock_name, Timer.DEFAULT_CLOCK_NAME)

    def test_Reset(self):
        t = Timer('timer1', clock_name='process_time')
        t.time()
        t.reset()
        self.assertEqual(t.label, '')
        self.assertEqual(t.seconds, 0.)
        self.assertEqual(t.minutes, 0.)
        self.assertEqual(t.clock_name, Timer.DEFAULT_CLOCK_NAME)

    def test_PrintInfo(self):
        t = Timer()
        t.print_info()

    def test_GetInfo(self):
        # Timer with clock supported by time.get_clock_info()
        t = Timer()
        info = t.get_info()
        self.assertIsInstance(info, types.SimpleNamespace)
        for value in info.__dict__.values():
            with self.subTest(value=value):
                self.assertIsNotNone(value)
        # Timer with custom function, does not supports time.get_clock_info()
        TestStack.push(Timer.CLOCKS)
        Timer.register_clock('constant_time', constant_time)
        t.clock_name = 'constant_time'
        info = t.get_info()
        self.assertIsInstance(info, types.SimpleNamespace)
        self.assertIsNotNone(info.implementation)
        self.assertIsNone(info.adjustable)
        self.assertIsNone(info.monotonic)
        self.assertIsNone(info.resolution)
        Timer.CLOCKS = TestStack.pop()

    def test_RegisterClock(self):
        TestStack.push(Timer.CLOCKS)
        Timer.register_clock('constant_time', constant_time)
        t = Timer()
        t.clock_name = 'constant_time'
        t.time()
        self.assertEqual(t.clock_name, 'constant_time')
        self.assertAlmostEqual(t.seconds, 1.)
        self.assertAlmostEqual(t.minutes, 1. / 60.)
        Timer.CLOCKS = TestStack.pop()

    def test_Compatibility(self):
        TestStack.push(Timer.CLOCKS)
        Timer.register_clock('constant_time', constant_time)
        t = Timer('timer1', clock_name='clock')
        # Invalid
        for value in [0, 0., 'clock', time,
                      Timer(clock_name='constant_time'),
                      Timer(clock_name='time')]:
            with self.subTest(value=value):
                self.assertFalse(t.is_compatible(value))
        # Valid
        self.assertTrue(t.is_compatible(Timer(clock_name='clock')))
        Timer.CLOCKS = TestStack.pop()


if __name__ == '__main__':
    unittest.main()
