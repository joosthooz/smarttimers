import random
from smarttimers import (Timer, TimerCompatibilityError)
import time
import unittest


class TimerInstanceOperatorsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create Timer instances with different time measurements.

        Timers are created at class level so it gets executed once (sleeps
        between time measurements using a random delay).
        """
        cls.t1 = Timer()
        cls.t1.time()
        time.sleep(random.randint(1, 5))
        cls.t2 = Timer()
        cls.t2.time()

    def test_ArithmeticSum(self):
        t1, t2 = type(self).t1, type(self).t2
        # Invalid
        for value in [1, 1., 'clock', time, [Timer()]]:
            with self.subTest(value=value):
                with self.assertRaises(TimerCompatibilityError):
                    t3 = t1 + value
        # Valid
        t3 = t1 + t2
        t4 = t2 + t1
        self.assertIsInstance(t3, Timer)
        self.assertNotEqual(t3, t2)
        self.assertAlmostEqual(t3.seconds, t1.seconds + t2.seconds)
        self.assertAlmostEqual(t3.minutes, (t1.seconds + t2.seconds) / 60.)
        self.assertEqual(t3, t4)

    def test_ArithmeticDiff(self):
        t1, t2 = type(self).t1, type(self).t2
        # Invalid
        for value in [1, 1., 'clock', time, [Timer()]]:
            with self.subTest(value=value):
                with self.assertRaises(TimerCompatibilityError):
                    t3 = t1 - value
        # Valid
        t3 = t1 - t2
        t4 = t2 - t1
        self.assertIsInstance(t3, Timer)
        self.assertNotEqual(t3, t2)
        self.assertAlmostEqual(t3.seconds, abs(t1.seconds - t2.seconds))
        self.assertAlmostEqual(t3.minutes, abs(t1.seconds - t2.seconds) / 60.)
        self.assertEqual(t3, t4)

    def test_TimerSum(self):
        t1, t2 = type(self).t1, type(self).t2
        # Valid
        t3 = Timer.sum(t1, t2)
        t4 = Timer.sum(t2, t1)
        self.assertIsInstance(t3, Timer)
        self.assertNotEqual(t3, t2)
        self.assertAlmostEqual(t3.seconds, t1.seconds + t2.seconds)
        self.assertAlmostEqual(t3.minutes, (t1.seconds + t2.seconds) / 60.)
        self.assertEqual(t3, t4)

    def test_TimerDiff(self):
        t1, t2 = type(self).t1, type(self).t2
        # Valid
        t3 = Timer.diff(t1, t2)
        t4 = Timer.diff(t2, t1)
        self.assertIsInstance(t3, Timer)
        self.assertNotEqual(t3, t2)
        self.assertAlmostEqual(t3.seconds, abs(t1.seconds - t2.seconds))
        self.assertAlmostEqual(t3.minutes, abs(t1.seconds - t2.seconds) / 60.)
        self.assertEqual(t3, t4)

    def test_Comparison(self):
        t1, t2 = type(self).t1, type(self).t2
        # Invalid
        for value in [1, 1., 'clock', time, [Timer()]]:
            with self.subTest(value=value):
                with self.assertRaises(TimerCompatibilityError):
                    t2 > value
            with self.subTest(value=value):
                with self.assertRaises(TimerCompatibilityError):
                    t2 >= value
            with self.subTest(value=value):
                with self.assertRaises(TimerCompatibilityError):
                    value < t2
            with self.subTest(value=value):
                with self.assertRaises(TimerCompatibilityError):
                    value <= t2
            with self.subTest(value=value):
                self.assertTrue(value != t2)
            with self.subTest(value=value):
                self.assertFalse(value == t2)
        # Valid
        self.assertGreater(t2, t1)
        self.assertGreaterEqual(t2, t1)
        self.assertLess(t1, t2)
        self.assertLessEqual(t1, t2)
        self.assertNotEqual(t1, t2)
        self.assertEqual(Timer(), Timer())


if __name__ == '__main__':
    unittest.main()
