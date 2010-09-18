import os
import sys
import imp
import inspect

try:
    from collections import OrderedDict
except ImportError:
    class OrderedDict(object):
        """ Stupid ordered dictionary """
        def __init__(self):
            self._keys = []
            self._items = {}

        def __getitem__(self, name):
            self._items[name]

        def __setitem__(self, name, value):
            if name in self:
                self._keys.remove(name)
            self._keys.append(name)
            self._items[name] = value

        def __contains__(self, name):
            return name in self._items

        def iteritems(self):
            for key in self._keys:
                yield key, self._items[key]

        def itervalues(self):
            for key, value in self.iteritems():
                yield value

def docstring_to_request(docstring):
    if not docstring:
        return docstring

    docstring = docstring.strip().split('\n')
    indentation = len(docstring[0]) - len(docstring[0].lstrip())
    if not docstring[0][indentation:]:
        docstring = docstring[1:]
    if not docstring[-1][indentation]:
        docstring = docstring[:-1]

    return '\n'.join(
        line[indentation:] for line in docstring
    ).replace('\n', '\r\n').replace('\\n', '\n').replace('\\r', '\r')

def import_file(filename):
    if not os.path.exists(filename):
        raise ImportError("Cannot import %s: File does not exist" % filename)
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    module_name = os.path.splitext(basename)[0]

    sys.path.insert(0, dirname)
    try:
        return imp.load_module(module_name, *imp.find_module(module_name))
    finally:
        sys.path = sys.path[1:]

def get_sourcefile(obj):
    return inspect.getsourcefile(obj)

def chain_iterable(iterables):
    for iterable in iterables:
        for item in iterable:
            yield item
