try:
    import unittest
except ImportError:
    import unittest2 as unittest

import os

from rtbot34 import normalize_path


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_path = os.path.dirname(os.path.dirname(__file__))
        cls.home_path = os.path.expanduser('~')

    def test_normalize_none_path(self):
        self.assertIsNone(normalize_path(None))

    def test_normalize_abs_path(self):
        path = normalize_path('/tmp/test.txt')
        self.assertEqual(normalize_path(path), '/tmp/test.txt')

    def test_normalize_abs_path_ignore_default(self):
        path = normalize_path('/tmp/test.txt', default='/tmp/default.txt')
        self.assertEqual(normalize_path(path), '/tmp/test.txt')

    def test_normalize_abs_path_default(self):
        path = normalize_path(None, default='/tmp/default.txt')
        self.assertEqual(normalize_path(path), '/tmp/default.txt')

    def test_normalize_relative_path(self):
        path = normalize_path('test.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.root_path, 'test.txt'))

    def test_normalize_relative_path_the_same_dir(self):
        path = normalize_path('./test.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.root_path, 'test.txt'))

    def test_normalize_relative_path_parent_dir(self):
        path = normalize_path('../test.txt')
        self.assertEqual(
            normalize_path(path),
            os.path.join(os.path.dirname(self.root_path), 'test.txt')
        )

    def test_normalize_relative_path_ignore_default(self):
        path = normalize_path('test.txt', default='default.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.root_path, 'test.txt'))

    def test_normalize_relative_path_default(self):
        path = normalize_path(None, default='default.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.root_path, 'default.txt'))

    def test_normalize_home_path(self):
        path = normalize_path('~/test.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.home_path, 'test.txt'))

    def test_normalize_home_path_ignore_default(self):
        path = normalize_path('~/test.txt', default='~/default.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.home_path, 'test.txt'))

    def test_normalize_home_path_default(self):
        path = normalize_path(None, default='~/default.txt')
        self.assertEqual(normalize_path(path),
                         os.path.join(self.home_path, 'default.txt'))


if __name__ == '__main__':
    unittest.main()
