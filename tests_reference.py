import rangetree_reference as rangetree
import sys
sys.modules["rangetree"] = rangetree

import tests_impl
tests_impl.main()
