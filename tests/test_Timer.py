#!/usr/bin/env python3

import unittest
import smarttimer


__all__ = ['TestTimer']


class TestTimer(unittest.TestCase):

    def test_TimerInit(self):
        t = smarttimer.Timer()
        self.assertTrue(len(t.id) == 0 and t.seconds == 0. and t.minutes == 0.)


if __name__ == '__main__':
    unittest.main()
