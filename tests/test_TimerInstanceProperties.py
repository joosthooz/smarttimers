import unittest
import copy
from smarttimer import Timer
from smarttimer.timer import (TimerDict,
                              TimerTypeError,
                              TimerValueError,
                              TimerKeyError,
                              TimerCompatibilityError)


class TimerInstancePropertiesTestCase(unittest.TestCase):

    def test_ID(self):
        t = Timer()
        # Invalid
        for id in [1, 1., ['timer1'], ('timer1',), {'id': 'timer1'}]:
            with self.subTest(id=id):
                with self.assertRaises(TimerTypeError):
                    t.id = id
        # Valid
        t.id = 'timer1'
        self.assertEqual(t.id, 'timer1')

    def test_ClockName(self):
        t = Timer()
        # Invalid
        for clock_name in [1, 1., ['clock'], ('clock',), \
            {'clock_name': 'clock'}]:
            with self.subTest(clock_name=clock_name):
                with self.assertRaises(TimerTypeError):
                    t.clock_name = clock_name

        for clock_name in ['myclock', 'acounter']:
            with self.subTest(clock_name=clock_name):
                with self.assertRaises(TimerKeyError):
                    t.clock_name = clock_name
        # Valid
        t.clock_name = 'clock'
        self.assertEqual(t.clock_name, 'clock')
        self.assertIs(t._clock, Timer.CLOCKS['clock'])

    def test_Seconds(self):
        t = Timer()
        # Invalid
        for seconds in [1, 1., '1', ['1'], ('1',), {'seconds': 1}]:
            with self.subTest(seconds=seconds):
                with self.assertRaises(AttributeError):
                    t.seconds = seconds

    def test_Minutes(self):
        t = Timer()
        # Invalid
        for minutes in [1, 1., '1', ['1'], ('1',), {'minutes': 1}]:
            with self.subTest(minutes=minutes):
                with self.assertRaises(AttributeError):
                    t.minutes = minutes


if __name__ == '__main__':
    unittest.main()
