
# while inotifywait -e close_write ./*.py || true; do tput reset ; pypy3 tests_linklist.py && pypy3 tests_slow.py; done

USE_BTREE = True

if USE_BTREE:
    BLACK = True
    RED = False

    def rb_free(node):
        del node.color
        del node.left
        del node.right
        # free(node);


    def is_red(node):
        return (node is not None and node.color == RED)


    def my_compare(key1, key2):
        return 0 if (key1 == key2) else (-1 if (key1 < key2) else 1)


    def rb_flip_color(node):
        node.color ^= True
        node.left.color ^= True
        node.right.color ^= True

    def rb_rotate_left(left):
        """ Make a right-leaning 3-node lean to the left.
        """
        if left is None:
            return None
        right = left.right
        left.right = right.left
        right.left = left
        right.color = left.color
        left.color = RED
        return right

    def rb_rotate_right(right):
        """ Make a left-leaning 3-node lean to the right.
        """
        if right is None:
            return None
        left = right.left
        right.left = left.right
        left.right = right
        left.color = right.color
        right.color = RED
        return left


    def rb_insert_recursive(node, node_to_insert):
        if node is None:
            return node_to_insert

        res = my_compare(node_to_insert.key, node.key)
        if res == 0:
            pass
        elif res < 0:
            node.left = rb_insert_recursive(node.left, node_to_insert)
        else:
            node.right = rb_insert_recursive(node.right, node_to_insert)

        if is_red(node.right) and not is_red(node.left):
            node = rb_rotate_left(node)
        if is_red(node.left) and is_red(node.left.left):
            node = rb_rotate_right(node)

        if is_red(node.left) and is_red(node.right):
            rb_flip_color(node)

        return node


    def rb_insert_root(root_rbtree, node_to_insert):
        root_rbtree = rb_insert_recursive(root_rbtree, node_to_insert)
        root_rbtree.color = BLACK
        return root_rbtree


    def rb_lookup(node, key):
        # get node from key
        while node is not None:
            cmp = my_compare(key, node.key)
            if cmp == 0:
                return node
            if cmp < 0:
                node = node.left
            else:
                node = node.right
        return None


    def rb_min(node):
        # -> Node
        if node is None:
            return None
        while node.left is not None:
            node = node.left
        return node


    def rb_balance_recursive(node):
        # -> Node
        if is_red(node.right):
            node = rb_rotate_left(node)
        if is_red(node.left) and is_red(node.left.left):
            node = rb_rotate_right(node)
        if is_red(node.left) and is_red(node.right):
            rb_flip_color(node)
        return node


    def rb_move_red_to_left(node):
        """ Assuming that h is red and both h.left and h.left.left
            are black, make h.left or one of its children red.
        """
        rb_flip_color(node)
        if node and node.right and is_red(node.right.left):
            node.right = rb_rotate_right(node.right)
            node = rb_rotate_left(node)
            rb_flip_color(node)
        return node


    def rb_move_red_to_right(node):
        """ Assuming that h is red and both h.right and h.right.left
            are black, make h.right or one of its children red.
        """
        rb_flip_color(node)
        if node and node.left and is_red(node.left.left):
            node = rb_rotate_right(node)
            rb_flip_color(node)
        return node


    def rb_pop_min_recursive(node):
        if node is None:
            return None
        if node.left is None:
            #  rb_free(node)
            return None, node
        if (not is_red(node.left)) and (not is_red(node.left.left)):
            node = rb_move_red_to_left(node)
        node.left, node_free = rb_pop_min_recursive(node.left)
        return rb_balance_recursive(node), node_free


    def rb_pop_key_recursive(node, key, swap_fn):
        if node is None:
            return None, None

        node_free = None
        if my_compare(key, node.key) == -1:
            if node.left is not None:
                if (not is_red(node.left)) and (not is_red(node.left.left)):
                    node = rb_move_red_to_left(node)
            node.left, node_free = rb_pop_key_recursive(node.left, key, swap_fn)
        else:
            if is_red(node.left):
                node = rb_rotate_right(node)
            cmp = my_compare(key, node.key)
            if cmp == 0 and (node.right is None):
                #  rb_free(node)
                return None, node
            assert(node.right is not None)
            if (not is_red(node.right)) and (not is_red(node.right.left)):
                node = rb_move_red_to_right(node)
                cmp = my_compare(key, node.key)

            if cmp == 0:
                # minor improvement over original method
                # no need to double lookup min
                node.right, node_free = rb_pop_min_recursive(node.right)

                # Swap 'node' with 'rb_pop_min_recursive(node.right)',
                # treating the right's minimum as removed.
                swap_fn(node, node_free)
            else:
                node.right, node_free = rb_pop_key_recursive(node.right, key, swap_fn)
        return rb_balance_recursive(node), node_free


    def rb_pop_key(node, key, swap_fn):
        node, node_free = rb_pop_key_recursive(node, key, swap_fn)
        if node is not None:
            node.color = BLACK
        return node, node_free


    def rb_copy_recursive(node):
        if node is None:
            return None
        copy = node.copy()
        copy.color = node.color
        copy.left = rb_copy_recursive(copy.left)
        copy.right = rb_copy_recursive(copy.right)
        return copy


    def rb_free_recursive(node):
        if node is not None:
            if node.left:
                rb_free_recursive(node.left)
            if node.right:
                rb_free_recursive(node.right)
            node.left = None
            node.right = None
            rb_free(node)











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
    ) + ((("_root",) if USE_BTREE else ()))

    if USE_BTREE:
        # External tree API
        def tree_add(self, node):
            self.rb_add(node)

        def tree_remove(self, node):
            def swap_fn(a, b):
                a.min, b.min = b.min, a.min
                a.max, b.max = b.max, a.max

                self._list.swap_pair(a, b)
                self._list._validate()

            return self.rb_remove(node.min, swap_fn)

        def tree_get_or_upper(self, key, default=None):
            # slow, in-efficient version
            """
            for n in self._node_iter_forward():
                if n.key >= key:
                    return n
            return default
            """

            def get_or_upper_recursive(n, n_best):
                """
                Check if (n.key >= key and key < n_best.key)
                to get the node directly after 'key'
                """
                if n is None:
                    return None
                # return best node and key_upper
                cmp_lower = my_compare(n.key, key)
                if cmp_lower == 0:
                    return n  # perfect match
                elif cmp_lower == 1:
                    assert(n.key >= key)
                    # n is lower than our best so far
                    # check if its an improvement on 'n_best'
                    if n_best is None or my_compare(n.key, n_best.key) == -1:
                        n_test = get_or_upper_recursive(n.left, n)
                        if n_test is not None:
                            return n_test
                        else:
                            return n  # keep as is
                    else:
                        return None
                    assert(0)  # unreachable
                else:  # -1
                    return get_or_upper_recursive(n.right, n_best)
                assert(0)  # unreachable

            n_best = get_or_upper_recursive(self._root, None)
            if n_best is not None:
                return n_best
            else:
                return default

        def tree_get_or_lower(self, key, default=None):
            # slow, in-efficient version
            """
            for n in self._node_iter_backward():
                if n.key <= key:
                    return n
            return default
            """
            def get_or_lower_recursive(n, n_best):
                """
                Check if (n.key >= key and key < n_best.key)
                to get the node directly after 'key'
                """
                if n is None:
                    return None
                # return best node and key_lower
                cmp_lower = my_compare(n.key, key)
                if cmp_lower == 0:
                    return n  # perfect match
                elif cmp_lower == -1:
                    assert(n.key <= key)
                    # n is greater than our best so far
                    # check if its an improvement on 'n_best'
                    if n_best is None or my_compare(n.key, n_best.key) == 1:
                        n_test = get_or_lower_recursive(n.right, n)
                        if n_test is not None:
                            return n_test
                        else:
                            return n  # keep as is
                    else:
                        return None
                    assert(0)  # unreachable
                else:  # 1
                    return get_or_lower_recursive(n.left, n_best)
                assert(0)  # unreachable

            n_best = get_or_lower_recursive(self._root, None)
            if n_best is not None:
                return n_best
            else:
                return default

        # --------------------------------------------------------------------
        # RB-TREE

        def rb_add(self, node):
            node.color = RED
            node.left = None
            node.right = None
            self._root = rb_insert_root(self._root, node)

        def rb_remove(self, key, swap_fn):
            assert(rb_lookup(self._root, key) is not None)
            self._root, node_free = rb_pop_key(self._root, key, swap_fn)
            rb_free(node_free)
            return node_free

        def clear(self):
            rb_free_recursive(self._root)
            self._root = None

        def is_empty(self):
            self._root is None

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
            node = self.tree_get_or_lower(value)
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
                node_next = self.tree_get_or_upper(value)
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
            self._root = None
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

