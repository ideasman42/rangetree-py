
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
    ) + ((("_rb",) if USE_BTREE else ()))

    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.prev = None
        self.next = None


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
            node._rb = self._tree.add_ex(node.min, node)

        def tree_remove(self, node):
            self._tree.remove(node.min)

        def tree_update(self, node):
            node._rb.key = node.min

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


    def _node_from_value(self, value):
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

    def take(self, value):
        node = self._node_from_value(value)
        if node is None:
            if value < self._range[0] or value > self._range[1]:
                raise Exception("Value out of range")
            else:
                raise Exception("Already taken")

        if node.min == value:
            if node.max != value:
                node.min += 1
                if USE_BTREE:
                    self.tree_update(node)
            else:
                assert(node.min == node.max)
                self._list.remove(node)
                if USE_BTREE:
                    self.tree_remove(node)
        elif node.max == value:
            node.max -= 1
        else:
            node_next = Node(min=value + 1, max=node.max)
            self._list.push_after(node, node_next)
            node.max = value - 1
            if USE_BTREE:
                self.tree_add(node_next)

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
            self._list.remove(node)
            if USE_BTREE:
                self.tree_remove(node)
        else:
            node.min += 1
            if USE_BTREE:
                self.tree_update(node)
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
            self._list.remove(node_next)
            if USE_BTREE:
                self.tree_remove(node_next)
        elif touch_prev:  # 2)
            assert(node_prev.max + 1 == value)
            node_prev.max = value
        elif touch_next:  # 3)
            assert(node_next.min - 1 == value)
            node_next.min = value
            if USE_BTREE:
                self.tree_update(node_next)
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

