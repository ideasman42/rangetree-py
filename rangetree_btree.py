
# while inotifywait -e close_write ./*.py || true; do tput reset ; pypy3 tests_btree.py && pypy3 tests_slow.py; done

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

    def key_cmp(key1, key2):
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

    def rb_fixup_insert(node):
        if is_red(node.right) and not is_red(node.left):
            node = rb_rotate_left(node)
        if is_red(node.left) and is_red(node.left.left):
            node = rb_rotate_right(node)

        if is_red(node.left) and is_red(node.right):
            rb_flip_color(node)
        return node

    def rb_insert_recursive(node, node_to_insert):
        if node is None:
            return node_to_insert

        cmp = key_cmp(node_to_insert.key, node.key)
        if cmp == 0:
            pass
        elif cmp == -1:
            node.left = rb_insert_recursive(node.left, node_to_insert)
        else:
            node.right = rb_insert_recursive(node.right, node_to_insert)

        return rb_fixup_remove(node)

    def rb_insert_root(root_rbtree, node_to_insert):
        root = rb_insert_recursive(root_rbtree, node_to_insert)
        root.color = BLACK
        return root

    def rb_fixup_remove(node):
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
            return None, None
        if node.left is None:
            #  rb_free(node)
            return None, node
        if (not is_red(node.left)) and (not is_red(node.left.left)):
            node = rb_move_red_to_left(node)
        node.left, node_free = rb_pop_min_recursive(node.left)
        return rb_fixup_remove(node), node_free

    def rb_remove_recursive(node, node_to_remove):
        if node is None:
            return None
        if key_cmp(node_to_remove.key, node.key) == -1:
            if node.left is not None:
                if (not is_red(node.left)) and (not is_red(node.left.left)):
                    node = rb_move_red_to_left(node)
            node.left = rb_remove_recursive(node.left, node_to_remove)
        else:
            if is_red(node.left):
                node = rb_rotate_right(node)
            if (node is node_to_remove) and (node.right is None):
                rb_free(node)
                return None
            assert(node.right is not None)
            if (not is_red(node.right)) and (not is_red(node.right.left)):
                node = rb_move_red_to_right(node)

            if node is node_to_remove:
                # minor improvement over original method
                # no need to double lookup min
                node.right, node_free = rb_pop_min_recursive(node.right)

                node_free.left = node.left
                node_free.right = node.right
                node_free.color = node.color
                rb_free(node)

                node = node_free
            else:
                node.right = rb_remove_recursive(node.right, node_to_remove)
        return rb_fixup_remove(node)

    def rb_remove_root(root, node_to_remove):
        root = rb_remove_recursive(root, node_to_remove)
        if root is not None:
            root.color = BLACK
        return root

    def rb_copy_recursive(node_src, fn):
        if node_src is None:
            return None
        node_dst = Node(node_src.min, node_src.max)
        node_dst.color = node_src.color
        node_dst.left = rb_copy_recursive(node_src.left, fn)
        fn(node_dst)
        node_dst.right = rb_copy_recursive(node_src.right, fn)
        return node_dst

    def rb_free_recursive(node):
        if node is not None:
            if node.left:
                rb_free_recursive(node.left)
            if node.right:
                rb_free_recursive(node.right)
            node.left = None
            node.right = None
            rb_free(node)

    def rb_is_balanced_recursive(node, black):
        # Check that every path from the root to a leaf
        # has the given number of black links.
        if node is None and black == 0:
            return True
        if node is None and black != 0:
            return False
        if not is_red(node):
            black -= 1
        return (rb_is_balanced_recursive(node.left, black) and
                rb_is_balanced_recursive(node.right, black))

    def rb_is_balanced(root):
        # Do all paths from root to leaf have same number of black edges?
        black = 0  # number of black links on path from root to min
        node = root
        while node is not None:
            if not is_red(node):
                black += 1
            node = node.left
        return rb_is_balanced_recursive(root, black)


# rb api end


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

    def replace(self, n_src, n_dst):
        # put 'n_src' in the position of 'n_dst', then remove 'n_dst'

        # close n_src's links
        if n_src.next is not None:
            n_src.next.prev = n_src.prev
        if n_src.prev is not None:
            n_src.prev.next = n_src.next

        # update adjacent links
        if n_dst.next is not None:
            n_dst.next.prev = n_src
        if n_dst.prev is not None:
            n_dst.prev.next = n_src

        # set direct links
        n_src.next = n_dst.next
        n_src.prev = n_dst.prev

        # update list
        if self.first is n_dst:
            self.first = n_src
        if self.last is n_dst:
            self.last = n_src


class RangeTree:
    """
    List based range tree.
    """
    __slots__ = (
        "_list",
        "_min",
        "_max",
    ) + ((("_root",) if USE_BTREE else ()))

    if USE_BTREE:
        # External tree API
        def tree_get_or_upper(self, key):
            # slow, in-efficient version
            """
            for n in self._node_iter_forward():
                if n.key >= key:
                    return n
            return default
            """
            def get_or_upper_recursive(n):
                """
                Check if (n.key >= key)
                to get the node directly after 'key'
                """
                # return best node and key_upper
                cmp_upper = key_cmp(n.key, key)
                if cmp_upper == 0:
                    return n  # exact match
                elif cmp_upper == 1:
                    assert(n.key >= key)
                    # n is lower than our best so far
                    if n.left is not None:
                        n_test = get_or_upper_recursive(n.left)
                        if n_test is not None:
                            return n_test
                    return n
                else:  # -1
                    if n.right is not None:
                        return get_or_upper_recursive(n.right)
                    return None
                assert(0)  # unreachable

            if self._root is not None:
                return get_or_upper_recursive(self._root)
            return None

        def tree_get_or_lower(self, key):
            # slow, in-efficient version
            """
            for n in self._node_iter_backward():
                if n.key <= key:
                    return n
            return default
            """
            def get_or_lower_recursive(n):
                """
                Check if (n.key >= key)
                to get the node directly after 'key'
                """
                # return best node and key_lower
                cmp_lower = key_cmp(n.key, key)
                if cmp_lower == 0:
                    return n  # exact match
                elif cmp_lower == -1:
                    assert(n.key <= key)
                    # n is greater than our best so far
                    if n.right is not None:
                        n_test = get_or_lower_recursive(n.right)
                        if n_test is not None:
                            return n_test
                    return n
                else:  # 1
                    if n.left is not None:
                        return get_or_lower_recursive(n.left)
                    return None
                assert(0)  # unreachable

            if self._root is not None:
                return get_or_lower_recursive(self._root)
            return None

        # --------------------------------------------------------------------
        # RB-TREE

        def rb_insert(self, node):
            node.color = RED
            node.left = None
            node.right = None
            self._root = rb_insert_root(self._root, node)
            assert(rb_is_balanced(self._root))

        def rb_remove(self, node):
            self._root = rb_remove_root(self._root, node)
            assert(rb_is_balanced(self._root))

        def rb_clear(self):
            rb_free_recursive(self._root)
            self._root = None

        # RB-TREE END

    def find_node_from_value(self, value):
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

    def find_node_pair_around_value(self, value):
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

    def __init__(self, *, min, max, full=False):
        self._list = LinkedList()
        self._min = min
        self._max = max
        if USE_BTREE:
            self._root = None

        if not full:
            node = Node(min=min, max=max)
            self.node_add_front(node)

    def copy(self):
        # use 'full' so tree is empty.
        tree_dst = RangeTree(min=self._min, max=self._max, full=True)
        if USE_BTREE:
            tree_dst._root = rb_copy_recursive(
                self._root,
                tree_dst._list.push_back,
            )
        else:
            push_back = tree_dst._list.push_back
            for node_src in self._list.iter():
                push_back(Node(min=node_src.min, max=node_src.max))
        return tree_dst

    def clear(self, full=False):
        self.__init__(min=self._min, max=self._max, full=full)

    def __repr__(self):
        return ("<%s object at %s [%s]>" %
                (self.__class__.__name__,
                 hex(id(self)),
                 [(node.min, node.max) for node in self._list.iter()]))

    def node_add_back(self, node_new):
        self._list.push_back(node_new)
        if USE_BTREE:
            self.rb_insert(node_new)

    def node_add_front(self, node_new):
        self._list.push_front(node_new)
        if USE_BTREE:
            self.rb_insert(node_new)

    def node_add_before(self, node_next, node_new):
        self._list.push_before(node_next, node_new)
        if USE_BTREE:
            self.rb_insert(node_new)

    def node_add_after(self, node_prev, node_new):
        self._list.push_after(node_prev, node_new)
        if USE_BTREE:
            self.rb_insert(node_new)

    def node_remove(self, node):
        if USE_BTREE:
            # handles list also
            self.rb_remove(node)
        self._list.remove(node)

    def _take_impl(self, value, node):
        if node.min == value:
            if node.max != value:
                node.min += 1
            else:
                assert(node.min == node.max)
                self.node_remove(node)
                del node
        elif node.max == value:
            node.max -= 1
        else:
            node_next = Node(min=value + 1, max=node.max)
            node.max = value - 1
            self.node_add_after(node, node_next)

    def take(self, value):
        node = self.find_node_from_value(value)
        if node is None:
            # should _never_ happen,
            # in cases where it might, use `retake` instead.
            if value < self._min or value > self._max:
                raise Exception("Value out of range")
            else:
                raise Exception("Already taken")
        self._take_impl(value, node)

    def retake(self, value):
        node = self.find_node_from_value(value)
        if node is not None:
            self._take_impl(value, node)
            return True
        else:
            return False

    def take_any(self):
        node = self._list.first
        value = node.min
        if value == self._max:
            raise IndexError("All values taken!")
        if value == node.max:
            self.node_remove(node)
        else:
            node.min += 1
        return value

    def release(self, value):

        if self._list.first is not None:
            node_prev, node_next = self.find_node_pair_around_value(value)
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
            del node_next
        elif touch_prev:  # 2)
            assert(node_prev.max + 1 == value)
            node_prev.max = value
        elif touch_next:  # 3)
            assert(node_next.min - 1 == value)
            node_next.min = value
        else:  # 4)
            node_new = Node(min=value, max=value)
            if node_prev is not None:
                self.node_add_after(node_prev, node_new)
            elif node_next is not None:
                self.node_add_before(node_next, node_new)
            else:
                assert(self._list.first is None)
                self.node_add_back(node_new)

    def is_empty(self):
        first = self._list.first
        if first is None:
            return False  # full
        last = self._list.last
        return ((first is last) and
                ((self._min == first.min and
                  self._max == first.max)))

    def has(self, value):
        if value < self._min or value > self._max:
            return False
        node = self.find_node_from_value(value)
        return node is None

    def range_iter(self):

        if self.is_empty():
            return

        if self._list.first is None:
            yield (self._min, self._max)
            return

        if self._list.first.min != self._min:
            yield (self._min, self._list.first.min - 1)

        for node_prev, node_next in iter_pairs(self._list.iter()):
            yield (node_prev.max + 1, node_next.min - 1)

        if self._list.last.max != self._max:
            yield (self._list.last.max + 1, self._max)

