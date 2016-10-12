
# while inotifywait -e close_write ./*.py || true; do tput reset ; pypy3 tests_linklist.py && pypy3 tests_slow.py; done

USE_BTREE = True

if USE_BTREE:
    import rbtree

def iter_pairs(iterable):
    it = iter(iterable)
    prev_ = next(it)
    while True:
        try:
            next_ = next(it)
        except StopIteration:
            return
        yield (prev_, next_)
        prev_ = next_


class Node:
    """
    Both a linked list and red-black tree node.
    """
    __slots__ = (
        "prev",
        "next",

        # range data (inclusive)
        "min",
        "max",
    ) + (((
        "left",
        "right",
        "color",
    ) if USE_BTREE else ()))

    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.prev = None
        self.next = None

        if USE_BTREE:
            self.left = None
            self.right = None

    @property
    def key(self):
        return self.min



class LinkedList:
    """
    Nodes can be None, or any object having a next & prev members.

    Note that identity is used for comparison.
    """
    __slots__ = (
        "first",
        "last",
    )

    def __init__(self):
        self.first = None
        self.last = None

    def push_front(self, node):
        assert(node not in self.iter())
        if self.first is None:
            self.last = node
        else:
            node.next = self.first
            node.next.prev = node
            node.prev = None
        self.first = node

    def push_back(self, node):
        assert(node not in self.iter())
        if self.first is None:
            self.first = node
        else:
            node.prev = self.last
            node.prev.next = node
            node.next = None
        self.last = node

    def push_after(self, node_prev, node_new):
        # node_new before node_next

        # empty list
        if self.first is None:
            self.first = node_new
            self.last = node_new
            return

        # insert at head of list
        if node_prev is None:
            node_new.prev = None
            node_new.next = self.first
            node_new.next.prev = node_new
            self.first = node_new
            return

        # at end of list
        if self.last is node_prev:
            self.last = node_new

        node_new.next = node_prev.next
        node_new.prev = node_prev
        node_prev.next = node_new
        if node_new.next:
            node_new.next.prev = node_new

    def push_before(self, node_next, node_new):
        # node_new before node_next

        # empty list
        if self.first is None:
            self.first = node_new
            self.last = node_new
            return

        # insert at end of list
        if node_next is None:
            node_new.prev = self.last
            node_new.next = None
            self.last.next = node_new
            self.last = node_new
            return

        # at beginning of list
        if self.first is node_next:
            self.first = node_new

        node_new.next = node_next
        node_new.prev = node_next.prev
        node_next.prev = node_new
        if node_new.prev:
            node_new.prev.next = node_new

    def remove(self, node):
        if node.next is not None:
            node.next.prev = node.prev
        if node.prev is not None:
            node.prev.next = node.next

        if self.last is node:
            self.last = node.prev
        if self.first is node:
            self.first = node.next

    def is_empty(self):
        return self.first is None

    def iter(self):
        node = self.first
        while node is not None:
            yield node
            node = node.next

    def swap_pair(self, a, b):
        if a is b:
            return

        if b.next is a:
            # cheap trick!
            a, b = b, a

        if a.next is b:

            self._validate()

            # right next to each other
            a.next = b.next
            b.prev = a.prev

            if a.next is not None:
                a.next.prev = a

            if b.prev is not None:
                b.prev.next = b

            b.next = a
            a.prev = b

        else:
            a.prev, b.prev = b.prev, a.prev
            a.next, b.next = b.next, a.next

            if a.prev is not None:
                a.prev.next = a
            if b.prev is not None:
                b.prev.next = b

            if a.next is not None:
                a.next.prev = a
            if b.next is not None:
                b.next.prev = b

        # update list endpoints
        if self.first is a:
            self.first = b
        elif self.first is b:
            self.first = a

        if self.last is a:
            self.last = b
        elif self.last is b:
            self.last = a

    def _validate(self):
        A = 1
        _ = self.last
        if _ is not None:
            while _.prev is not None:
                _ = _.prev
                A += 1

        B = 1
        _ = self.first
        if _ is not None:
            while _.next is not None:
                _ = _.next
                B += 1

        assert(B == A)


class RangeTree:
    """
    List based range tree.
    """
    __slots__ = (
        "_list",
        "_range",
    ) + ((("_tree",) if USE_BTREE else ()))

    if USE_BTREE:
        def tree_add(self, node):
            node.color = rbtree.RED
            self._tree.add(node)

        def tree_remove(self, node):
            def swap_fn(a, b):
                a.min, b.min = b.min, a.min
                a.max, b.max = b.max, a.max

                self._list.swap_pair(a, b)
                self._list._validate()

            return self._tree.remove(node.min, swap_fn)

    def _list_validate(self):
        ls = list(self._list.iter())
        # no duplicates
        assert(len(ls) == len({id(node) for node in ls}))
        for a, b in iter_pairs(ls):
            assert(a.next is b)
            assert(a is b.prev)
        assert(ls[0].prev is None)
        assert(ls[-1].next is None)
        for a, b in iter_pairs(ls):
            if not a.max < b.min:
                print(a.max, b.min)
            assert(a.max < b.min)
            assert(a.min <= a.max)
            assert(b.min <= b.max)
        if ls:
            assert(ls[0] is self._list.first)
            assert(ls[-1] is self._list.last)

        A = 1
        _ = self._list.last
        while _.prev is not None:
            _ = _.prev
            A += 1

        B = 1
        _ = self._list.first
        while _.next is not None:
            _ = _.next
            B += 1

        assert(B == A)

    def _node_from_value(self, value):
        self._list._validate()
        if USE_BTREE:
            node = self._tree.get_or_lower(value)
            if node is not None:
                if value >= node.min and value <= node.max:
                    return node
            return None
        else:
            for node in self._list.iter():
                if value >= node.min and value <= node.max:
                    return node
            return None

    def _node_pair_around_value(self, value):
        if value < self._list.first.min:
            return (None, self._list.first)
        elif value > self._list.last.max:
            return (self._list.last, None)
        else:
            if USE_BTREE:
                node_next = self._tree.get_or_upper(value)
                if node_next is not None:
                    node_prev = node_next.prev
                    if node_prev.max < value < node_next.min:
                        return (node_prev, node_next)
            else:
                for node_prev, node_next in iter_pairs(self._list.iter()):
                    if node_prev.max < value < node_next.min:
                        return (node_prev, node_next)

        return (None, None)

    @classmethod
    def FromRanges(cls, range_iter):
        range_ls = list(range_iter)
        range_ls_unpack = [value for pair in range_ls for value in pair]
        if not range_ls_unpack:
            # empty case
            range_ls_unpack = [0]
        r = RangeTree(min=min(range_ls_unpack), max=max(range_ls_unpack))
        for pair in range_ls:
            for value in range(pair[0], pair[1] + 1):
                r.take(value)
        return r

    def __init__(self, *, min, max):
        self._list = LinkedList()
        self._range = (min, max)
        node = Node(min=min, max=max)
        self._list.push_front(node)
        if USE_BTREE:
            self._tree = rbtree.RBTree()
            self.tree_add(node)

    def __repr__(self):
        return ("<%s object at %s [%s]>" %
                (self.__class__.__name__,
                 hex(id(self)),
                 [(node.min, node.max) for node in self._list.iter()]))

    def node_remove(self, node):
        if USE_BTREE:
            node = self.tree_remove(node)
        self._list.remove(node)

    def take(self, value):
        self._list._validate()
        node = self._node_from_value(value)
        if node is None:
            if value < self._range[0] or value > self._range[1]:
                raise Exception("Value out of range")
            else:
                raise Exception("Already taken")
        self._list._validate()

        if node.min == value:
            if node.max != value:
                node.min += 1
            else:
                assert(node.min == node.max)
                self.node_remove(node)
            self._list._validate()
        elif node.max == value:
            node.max -= 1
            self._list._validate()
        else:
            self._list._validate()
            node_next = Node(min=value + 1, max=node.max)
            self._list.push_after(node, node_next)
            node.max = value - 1
            self._list._validate()
            if USE_BTREE:
                self.tree_add(node_next)
            self._list._validate()

        # self._list_validate()

    def retake(self, value):
        # TODO, optimize
        if self.has(value):
            return False
        else:
            self.take(value)
            return True

    def take_any(self):
        node = self._list.first
        value = node.min
        if value == node.max:
            self.node_remove(node)
        else:
            node.min += 1
        return value

    def release(self, value):

        if self._list.first is not None:
            node_prev, node_next = self._node_pair_around_value(value)
            if node_prev is None and node_next is None:
                raise Exception("Value not taken")

            # 4 Cases:
            # 1) fill the gap between prev & next (two spans into one span).
            # 2) touching prev, (grow prev.max up one).
            # 3) touching next, (grow next.min down one).
            # 4) touching neither, add a new segment.
            touch_prev = (node_prev is not None and node_prev.max + 1 == value)
            touch_next = (node_next is not None and node_next.min - 1 == value)
        else:
            # we could handle this case (4) inline,
            # since its not a common case - use regular logic.
            node_prev = node_next = None
            touch_prev = False
            touch_next = False

        if touch_prev and touch_next:  # 1)
            node_prev.max = node_next.max
            self.node_remove(node_next)
        elif touch_prev:  # 2)
            assert(node_prev.max + 1 == value)
            node_prev.max = value
        elif touch_next:  # 3)
            assert(node_next.min - 1 == value)
            node_next.min = value
        else:  # 4)
            node_new = Node(min=value, max=value)
            if node_prev is not None:
                self._list.push_after(node_prev, node_new)
            elif node_next is not None:
                self._list.push_before(node_next, node_new)
            else:
                assert(self._list.first is None)
                self._list.push_back(node_new)
            if USE_BTREE:
                self.tree_add(node_new)

        #  self._list_validate()

    def is_empty(self):
        first = self._list.first
        if first is None:
            return False  # full
        last = self._list.last
        return ((first is last) and
                (self._range == (first.min, first.max)))

    def has(self, value):
        if value < self._range[0]:
            return False
        elif value > self._range[1]:
            return False

        node = self._node_from_value(value)
        return node is None

    def range_iter(self):

        if self.is_empty():
            return

        if self._list.first is None:
            yield (self._range[0], self._range[1])
            return


        if self._list.first.min != self._range[0]:
            yield (self._range[0], self._list.first.min - 1)

        for node_prev, node_next in iter_pairs(self._list.iter()):
            yield (node_prev.max + 1, node_next.min - 1)

        # This never happens!
        if self._list.last.max != self._range[1]:
            yield (self._list.last.max + 1, self._range[1])

