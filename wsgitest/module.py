import os
import sys
import imp

def import_file(filename):
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    module_name = os.path.splitext(basename)[0]

    sys.path.insert(0, dirname)
    try:
        return imp.load_module(module_name, *imp.find_module(module_name))
    finally:
        sys.path = sys.path[1:]

class TestModule(object):
    def __init__(self, module):
        self._module = module
        self.tests = tuple(self._find_tests())

    def _find_tests(self):
        from test import Test
        for name in dir(self._module):
            if name.startswith('test_'):
                yield Test.from_func(getattr(self._module, name))

    @classmethod
    def from_file(cls, filename):
        return cls(import_file(filename))
