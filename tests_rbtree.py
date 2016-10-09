
import rbtree

import unittest

# TODO, test copy, pop_min, pop_max
class TestDict_Helper:

    def assertDict(self, d, *, seed):
        r = rbtree.RBTree()
        d_items = list(d.items())
        d_items.sort()

        for pass_nr in range(2):
            if pass_nr == 0:
                pass
            elif pass_nr == 1:
                d_items.reverse()
            elif pass_nr == 2:
                rng = random.Random(seed)
                rng.shuffle(d_items)

            for k, v in d_items:
                self.assertEqual(k in r, False)
                r[k] = v
                self.assertEqual(k in r, True)

            for k, v in d_items:
                self.assertEqual(r[k], v)

            self.assertEqual(len(d), len(list(r.keys())))

            # remove half the items
            d_items_split = len(d_items) // 2
            d_items_a = d_items[d_items_split:]
            d_items_b = d_items[:d_items_split]

            for k, v in d_items_a:
                self.assertEqual(r.pop_key(k), v)

            for k, v in d_items_a:
                self.assertEqual(k in r, False)
            for k, v in d_items_b:
                self.assertEqual(r[k], d[k])

            for k, v in reversed(d_items_a):
                r[k] = v

            for k, v in reversed(d_items_b):
                self.assertEqual(r.pop_key(k), v)

            for k, v in d_items_a:
                self.assertEqual(r[k], v)

            for k, v in d_items_a:
                r.remove(k)

            self.assertEqual(0, len(list(r.keys())))

    def assertSet(self, s, *, seed):
        self.assertDict({k: repr(k) for k in s}, seed=seed)


class TestSimple(unittest.TestCase, TestDict_Helper):

    def test_single(self):
        self.assertSet({1}, seed=10)

    def test_triple(self):
        self.assertSet({1, 2, 3}, seed=100)

    def test_100(self):
        self.assertSet(set(range(1000)), seed=1000)


if __name__ == "__main__":
    unittest.main()
