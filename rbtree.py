__all__ = (
    "RBTree",
)
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


def rb_pop_max_recursive(node):
    if is_red(node.left):
        node = rb_rotate_right(node)
    if node.right is None:
        #  rb_free(node)
        return None, node
    if (not is_red(node.right)) and (not is_red(node.right.left)):
        node = rb_move_red_to_right(node)
    node.right, node_free = rb_pop_max_recursive(node.right)
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


def rb_pop_min(node):
    node, node_free = rb_pop_min_recursive(node)
    if node is not None:
        node.color = BLACK
    return node, node_free


def rb_pop_max(node):
    node, node_free = rb_pop_max_recursive(node)
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


class RBTree:
    __slots__ = (
        "root",
    )

    def __init__(self):
        self.root = None

    def get(self, key, default=None):
        n = rb_lookup(self.root, key)
        if n is not None:
            return n.value
        else:
            return default

    def get_or_upper(self, key, default=None):
        for n in self._node_iter_forward():
            if n.key >= key:
                return n
        return default

    def get_or_lower(self, key, default=None):
        for n in self._node_iter_backward():
            if n.key <= key:
                return n
        return default

    def add(self, node):
        self.root = rb_insert_root(self.root, node)

    def remove(self, key, swap_fn):
        assert(rb_lookup(self.root, key) is not None)
        self.root, node_free = rb_pop_key(self.root, key, swap_fn)
        #  rb_free(node_free)
        return node_free

    def discard(self, key, swap_fn):
        if key in self:
            self.root, node_free = rb_pop_key(self.root, key, swap_fn)
            rb_free(node_free)

    def pop_key(self, key, swap_fn):
        assert(rb_lookup(self.root, key) is not None)
        self.root, node_free = rb_pop_key(self.root, key, swap_fn)
        if node_free is None:
            raise Exception("internal error, removed value which is not in the tree! tree is now invalid!")
        value = node_free.value
        rb_free(node_free)
        return value

    def pop_min(self):
        if self.root is None:
            raise IndexError("pop from empty tree")
        self.root, node_free = rb_pop_min(self.root)
        return value

    def pop_max(self):
        if self.root is None:
            raise IndexError("pop from empty tree")
        self.root, node_free = rb_pop_max(self.root)
        value = node_free.value
        return value

    def clear(self):
        rb_free_recursive(self.root)
        self.root = None

    def is_empty(self):
        self.root is None

    def copy(self):
        copy = RBTree()
        copy.root = rb_copy_recursive(self.root)
        return copy

    def __contains__(self, key):
        return rb_lookup(self.root, key) is not None

    def __getitem__(self, key):
        node = rb_lookup(self.root, key)
        if node is None:
            raise KeyError(repr(key))
        return node.value

    def __setitem__(self, key, value):
        self.add(key, value)

    # ------------------------------------------------------------------------
    # Convenience Helpers

    def _node_iter_forward(self):
        def node_iter(node):
            if node is not None:
                yield from node_iter(node.left)
                yield node
                yield from node_iter(node.right)
        yield from node_iter(self.root)

    def _node_iter_backward(self):
        def node_iter(node):
            if node is not None:
                yield from node_iter(node.right)
                yield node
                yield from node_iter(node.left)
        yield from node_iter(self.root)

    def _node_iter_dir(self, reverse=False):
        if reverse:
            yield from self._node_iter_backward()
        else:
            yield from self._node_iter_forward()

    def items(self, reverse=False):
        for n in self._node_iter_dir(reverse):
            yield (n.key, n.value)

    def keys(self, reverse=False):
        for n in self._node_iter_dir(reverse):
            yield n.key

    def values(self, reverse=False):
        for n in self._node_iter_dir(reverse):
            yield n.value
