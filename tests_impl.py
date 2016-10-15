
if __name__ == "__main__":
    raise Exception("Can't run this directly!")

import unittest
from rangetree import RangeTree

# while inotifywait -e close_write ./*.py || true; do tput reset ; python tests_slow.py; done


class TestBasics(unittest.TestCase):

    def test_copy_empty(self):
        r_src = RangeTree(min=0, max=10)
        r_dst = r_src.copy()
        self.assertEqual(list(r_src.range_iter()), list(r_dst.range_iter()))

    def test_copy_10(self):
        r_src = RangeTree(min=0, max=10)
        for i in range(0, 10, 2):
            r_src.take(i)
        r_dst = r_src.copy()
        data = list(r_src.range_iter())
        self.assertEqual(data, list(r_dst.range_iter()))
        r_dst.clear()
        self.assertEqual([], list(r_dst.range_iter()))


class TestRange_Helper:
    def assertRangeData(self, range_iter):
        range_ls_src = list(range_iter)
        r = RangeTree.FromRanges(range_ls_src)
        range_ls_dst = list(r.range_iter())
        range_ls_src.sort()
        self.assertEqual(range_ls_src, range_ls_dst)


class TestRandom_Helper:

    def assertRandomItems(self, *, total, take_factor, seed):
        import random

        ls = list(range(total))
        rng = random.Random(seed)
        rng.shuffle(ls)
        ls_all = ls[:]
        del ls[int(total * take_factor):]

        r = RangeTree(min=0, max=total - 1)

        for pass_nr in range(4):
            self.assertEqual(r.is_empty(), True)

            if pass_nr == 0:
                pass
            elif pass_nr == 1:
                ls.reverse()
            elif pass_nr == 2:
                ls.sort()
            elif pass_nr == 3:
                ls.reverse()

            for i in ls:
                r.take(i)

            items_a = set(ls)
            items_b = set(range(1, total + 1)) - items_a

            for i in sorted(items_a):
                self.assertEqual(r.has(i), True)

            for i in sorted(items_b):
                self.assertEqual(r.has(i), False)

            # test retake
            for i in ls_all:
                test = r.retake(i)
                self.assertEqual(test, i not in ls)

            for i in ls_all:
                r.release(i)


class RangeTest(unittest.TestCase, TestRange_Helper):
    def test_nil(self):
        self.assertRangeData([
        ])

    def test_single(self):
        self.assertRangeData([
            (0, 0),
        ])

    def test_simple(self):
        self.assertRangeData([
            (0, 10),
            (12, 14),
        ])

    def test_wide(self):
        self.assertRangeData([
            (-100, 100),
            (200, 300),
        ])

    def test_single_many(self):
        self.assertRangeData([
            (-10, -10),
            (0, 0),
            (10, 10),
        ])


class IncrementalTest(unittest.TestCase):

    def test_simple(self):
        r = RangeTree(min=0, max=9)
        ls = list(range(0, 10))
        for i in ls:
            r.take(i)

        self.assertEqual(list(r.range_iter()), [(ls[0], ls[-1])])

        self.assertEqual(r.has(ls[0] - 0), True)
        self.assertEqual(r.has(ls[0] - 1), False)

        self.assertEqual(r.has(ls[-1] + 0), True)
        self.assertEqual(r.has(ls[-1] + 1), False)

    def test_many(self):
        r = RangeTree(min=0, max=9)

        # 2 passes to be sure
        for _ in range(2):
            self.assertEqual(r.is_empty(), True)
            ls = list(range(0, 10, 2))
            for i in ls:
                r.take(i)
            self.assertEqual(r.is_empty(), False)

            self.assertEqual(r.has(ls[0] - 0), True)
            self.assertEqual(r.has(ls[0] - 1), False)

            self.assertEqual(r.has(ls[-1] + 0), True)
            self.assertEqual(r.has(ls[-1] + 1), False)

            self.assertEqual(
                list(r.range_iter()),
                [(0, 0), (2, 2), (4, 4), (6, 6), (8, 8)],
            )

            r.release(ls.pop(0))
            r.release(ls.pop(-1))
            r.take(3)
            r.take(5)
            self.assertEqual(list(r.range_iter()), [(2, 6)])
            r.release(2)
            r.release(6)
            self.assertEqual(list(r.range_iter()), [(3, 5)])
            r.release(4)
            self.assertEqual(list(r.range_iter()), [(3, 3), (5, 5)])

            for i in (3, 5):
                r.release(i)

            self.assertEqual(list(r.range_iter()), [])

    def test_complex(self):
        """
        Test complex pairs
        """
        r = RangeTree(min=-10, max=11)
        # 2 passes on the same data structure.
        for _ in range(2):
            self.assertEqual(r.is_empty(), True)
            for i in (-10, 10, 11):
                r.take(i)
            self.assertEqual(r.is_empty(), False)

            self.assertEqual(list(r.range_iter()), [(-10, -10), (10, 11)])
            for i in (-8, -7, 8):
                r.take(i)
            self.assertEqual(list(r.range_iter()), [(-10, -10), (-8, -7), (8, 8), (10, 11)])
            for i in (-9, 9):
                r.take(i)
            self.assertEqual(list(r.range_iter()), [(-10, -7), (8, 11)])
            for i in (-9, 9):
                r.release(i)
            self.assertEqual(list(r.range_iter()), [(-10, -10), (-8, -7), (8, 8), (10, 11)])
            for i in (8, 10, 11):
                r.release(i)
            self.assertEqual(list(r.range_iter()), [(-10, -10), (-8, -7)])
            for i in (-10, -8, -7):
                r.release(i)
            # empty for next pass
            self.assertEqual(list(r.range_iter()), [])


class TestRandom(unittest.TestCase, TestRandom_Helper):
    """
    Use many random points in a range, ensure rangetree correctly detects their presence.
    """

    def test_random_1(self):
        self.assertRandomItems(total=100, take_factor=0.1, seed=1)

    def test_random_2(self):
        self.assertRandomItems(total=100, take_factor=0.25, seed=10)

    def test_random_3(self):
        self.assertRandomItems(total=100, take_factor=0.5, seed=100)

    def test_random_4(self):
        self.assertRandomItems(total=100, take_factor=0.75, seed=1000)

    def test_random_5(self):
        self.assertRandomItems(total=100, take_factor=1.0, seed=10000)

    def test_random_big(self):
        self.assertRandomItems(total=511, take_factor=0.5, seed=5)


def main():
    unittest.main(module=__name__)

