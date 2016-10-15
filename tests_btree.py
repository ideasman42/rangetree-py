import rangetree_btree
import sys
sys.modules["rangetree"] = rangetree_btree

import tests_impl
tests_impl.main()
