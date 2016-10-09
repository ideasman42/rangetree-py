import rangetree_slow
import sys
sys.modules["rangetree"] = rangetree_slow

import tests_impl
tests_impl.main()

