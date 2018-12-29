import unittest
from smarttimers import SmartTimer


class SmartTimerInstancePropertiesTestCase(unittest.TestCase):

    def test_Name(self):
        t = SmartTimer()
        t.name = 'timer'
        self.assertEqual(t.name, 'timer')
        for nameval in [1, 1., ['timer'], ('timer',), {'timer': 1}, None]:
            with self.subTest(nameval=nameval):
                t.name = nameval
                self.assertEqual(t.name, nameval)


if __name__ == '__main__':
    unittest.main()
