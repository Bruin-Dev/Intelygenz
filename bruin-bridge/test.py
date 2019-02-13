import unittest


class DummyTest(unittest.TestCase):

    def test_dummy(self):
        self.assertEqual('KA', 'KA')


if __name__ == '__main__':
    unittest.main()
