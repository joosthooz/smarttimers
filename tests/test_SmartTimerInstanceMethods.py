import os
import unittest
from smarttimers import (SmartTimer, TimerError)


class SmartTimerInstanceMethodsTestCase(unittest.TestCase):

    def test_Str(self):
        t = SmartTimer()
        print(t)
        t.tic()
        t.toc()
        print(t)

    def test_InitDefaultArgs(self):
        t = SmartTimer()
        self.assertEqual(t.name, 'smarttimer')
        self.assertListEqual(t.labels, [])
        self.assertListEqual(t.active_labels, [])
        self.assertListEqual(t.seconds, [])
        self.assertListEqual(t.minutes, [])
        self.assertDictEqual(t.times, {})

    def test_InitUserArgs(self):
        t = SmartTimer(name='atimer', seconds=10.5, clock_name='clock')
        self.assertEqual(t.name, 'atimer')
        self.assertListEqual(t.labels, [])
        self.assertListEqual(t.active_labels, [])
        self.assertListEqual(t.seconds, [])
        self.assertListEqual(t.minutes, [])
        self.assertDictEqual(t.times, {})

    def test_PrintInfo(self):
        t = SmartTimer()
        t.print_info()
        t = SmartTimer(name='atimer', seconds=10.5, clock_name='clock')
        t.print_info()

    def test_ActiveCompletedTimes(self):
        t = SmartTimer()
        t.tic('A')
        self.assertEqual(len(t.active_labels), 1)
        self.assertEqual(len(t.labels), 0)
        t.toc()
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.labels), 1)
        t.tic('B')
        self.assertEqual(len(t.active_labels), 1)
        self.assertEqual(len(t.labels), 1)
        t.toc()
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.labels), 2)

    def test_ConsecutiveScheme(self):
        t = SmartTimer()
        t.tic('A')
        t.sleep(0.5)
        t.toc()
        t.tic('B')
        t.sleep(0.5)
        t.toc()
        self.assertEqual(len(t.labels), 2)
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.seconds), 2)
        self.assertEqual(len(t.minutes), 2)
        self.assertEqual(len(t.times), 2)
        self.assertIn('A', t.times)
        self.assertIn('B', t.times)
        self.assertAlmostEqual(t.walltime()[0], sum(t.seconds), 3)

    def test_CascadeScheme(self):
        t = SmartTimer()
        t.tic('A')
        t.sleep(0.5)
        t.toc()
        t.sleep(0.5)
        t.toc('B')
        self.assertEqual(len(t.labels), 2)
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.seconds), 2)
        self.assertEqual(len(t.minutes), 2)
        self.assertEqual(len(t.times), 2)
        self.assertIn('A', t.times)
        self.assertIn('B', t.times)
        self.assertEqual(t.walltime()[0], t.seconds[1])

    def test_NestedScheme(self):
        t = SmartTimer()
        t.tic('A')
        t.sleep(0.5)
        t.tic('B')
        t.sleep(0.5)
        t.toc()
        t.sleep(0.5)
        t.toc()
        self.assertEqual(len(t.labels), 2)
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.seconds), 2)
        self.assertEqual(len(t.minutes), 2)
        self.assertEqual(len(t.times), 2)
        self.assertIn('A', t.times)
        self.assertIn('B', t.times)
        self.assertEqual(t.walltime()[0], t.seconds[0])

    def test_LabelPairedScheme(self):
        t = SmartTimer()
        t.tic('A')
        t.sleep(0.5)
        t.tic('B')
        t.sleep(0.5)
        t.toc('A')
        t.sleep(0.5)
        t.toc('B')
        self.assertEqual(len(t.labels), 2)
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.seconds), 2)
        self.assertEqual(len(t.minutes), 2)
        self.assertEqual(len(t.times), 2)
        self.assertIn('A', t.times)
        self.assertIn('B', t.times)

    def test_WithStatement(self):
        t = SmartTimer()
        with t:
            t.sleep(1)
        self.assertEqual(len(t.labels), 1)
        self.assertEqual(len(t.active_labels), 0)
        self.assertEqual(len(t.seconds), 1)
        self.assertEqual(len(t.minutes), 1)
        self.assertEqual(len(t.times), 1)
        self.assertIn('', t.times)
        self.assertAlmostEqual(t.walltime()[0], t.seconds[0], 3)

    def test_NoMatchedPair(self):
        t = SmartTimer()
        with self.assertRaises(TimerError):
            t.toc()
        t.tic('A')
        with self.assertRaises(KeyError):
            t.toc('B')

    def test_InvalidTocKey(self):
        t = SmartTimer()
        t.tic('A')
        for keyval in [1, 1., ['A'], ('A',), {'A': 1}]:
            with self.subTest(keyval=keyval):
                with self.assertRaises(KeyError):
                    t.toc(keyval)

    def test_QueryKey(self):
        t = SmartTimer()
        t.tic('A')
        t.tic('B')
        t.toc()
        t.toc()
        # Valid, key not found
        for keyval in [1., ['A'], {'A': 1}, 'F', ('Z',)]:
            with self.subTest(keyval=keyval):
                self.assertIsNone(t[keyval])
        # Valid
        self.assertEqual(t['A'], t.seconds[0])
        self.assertListEqual(t['A', 'B'], t.seconds)
        self.assertListEqual(t[:], t.seconds)
        self.assertListEqual(t[0, 1], t.seconds)
        self.assertListEqual(t[0, 'B'], t.seconds)

    def test_RemoveKey(self):
        t = SmartTimer()
        t.tic('A')
        t.tic('B')
        t.tic('C')
        t.tic('D')
        t.tic('E')
        t.tic('F')
        t.toc()
        t.toc()
        t.toc()
        t.toc()
        t.toc()
        t.toc()
        # Invalid keys, not found
        for keyval in [1., ['A'], {'A': 1}]:
            t.remove(keyval)
        self.assertEqual(len(t.labels), 6)
        # Valid keys, not found
        for keyval in [100, 'G', ('Z',)]:
            t.remove(keyval)
        self.assertEqual(len(t.labels), 6)
        # Valid
        t.remove('A')
        t.remove('B', 'C')
        t.remove(0)
        t.remove(slice(0, 2, None))
        self.assertListEqual(t.labels, [])
        self.assertListEqual(t.active_labels, [])
        self.assertListEqual(t.seconds, [])
        self.assertListEqual(t.minutes, [])
        self.assertDictEqual(t.times, {})

    def test_Clear(self):
        t = SmartTimer('atimer')
        t.tic('A')
        t.toc()
        t.clear()
        self.assertEqual(t.name, 'atimer')
        self.assertListEqual(t.labels, [])
        self.assertListEqual(t.active_labels, [])
        self.assertListEqual(t.seconds, [])
        self.assertListEqual(t.minutes, [])
        self.assertDictEqual(t.times, {})

    def test_Reset(self):
        t = SmartTimer('atimer')
        t.tic('A')
        t.toc()
        t.reset()
        self.assertEqual(t.name, 'smarttimer')
        self.assertListEqual(t.labels, [])
        self.assertListEqual(t.active_labels, [])
        self.assertListEqual(t.seconds, [])
        self.assertListEqual(t.minutes, [])
        self.assertDictEqual(t.times, {})

    def test_WriteToFile(self):
        t = SmartTimer()
        t.tic('A')
        t.toc()
        # Invalid
        for fn in [1, 1., ['smarttimer'], ('smarttimer',), {'smarttimer': 1}]:
                with self.assertRaises(AttributeError):
                    t.dump_times(filename=fn)
        # Valid
        t.dump_times(filename='', mode='w')
        t.dump_times(filename='smarttimer.txt', mode='a')
        os.remove('smarttimer.txt')

    def test_TimerStatsAll(self):
        t = SmartTimer()
        for i in range(5):
            t.tic('loop ' + str(i))
            t.sleep(0.2)
            t.toc()
        stats = t.stats()
        print(stats)
        self.assertAlmostEqual(0.2, stats.min[0], 3)
        self.assertAlmostEqual(0.2, stats.max[0], 3)
        self.assertAlmostEqual(0.2, stats.avg[0], 3)

    def test_TimerStatsSelect(self):
        t = SmartTimer()
        t.tic('A')
        t.toc()
        t.toc()
        for i in range(5):
            t.tic('loop ' + str(i))
            t.sleep(0.2)
            t.toc()
        stats = t.stats('loop')
        print(stats)
        self.assertAlmostEqual(0.2, stats.min[0], 3)
        self.assertAlmostEqual(0.2, stats.max[0], 3)
        self.assertAlmostEqual(0.2, stats.avg[0], 3)


if __name__ == '__main__':
    unittest.main()
