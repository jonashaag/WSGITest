import os
import sys
import imp
import inspect
import string
import socket
import errno

class dummy:
    pass

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

        def __len__(self):
            return len(self._keys)

        def iteritems(self):
            for key in self._keys:
                yield key, self._items[key]

        def itervalues(self):
            for key, value in self.iteritems():
                yield value

def normalize_docstring(docstring):
    def itersplit(s, c):
        buf = []
        for char in s:
            if char == c:
                yield ''.join(buf)
                buf = []
            else:
                buf.append(char)
        yield ''.join(buf)

    docstring_iter = iter(docstring)
    if docstring[0] == '\n':
        docstring_iter.next()

    lines = itersplit(docstring_iter, '\n')
    first_line = lines.next()
    indentation = len(first_line) - len(first_line.lstrip())
    if '\t' in first_line[:indentation]:
        raise ValueError('Please indent with 4 spaces, not tabs')
    yield first_line[indentation:]

    prev = None
    for line in lines:
        if prev is not None:
            yield prev
        prev = line[indentation:]
    if prev != '\n':
        yield prev

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

def find_exception(stderr):
    for line in stderr.split('\n'):
        if not line or line[0] not in string.letters:
            # line is empty or does not start with (a-zA-Z).
            # Can't be part of a traceback.
            continue
        line = line.strip()
        if ':' in line:
            # line might be of form "ExceptionName: exception message".
            exc_name, exc_value = line.split(':', 1)
            if not exc_value:
                # "ExceptionName:" is no possible traceback formatting.
                # This can't be an exception.
                continue
            return exc_name, exc_value
        else:
            # No ":" in this line, might be of form "ExceptionName", though.
            # We have to invent something to separate exception lines from
            # non-exception lines printed to stderr (which is a bad habit,
            # but not rarely done by servers).
            # The only thing I can think of is searching the name for
            # common exception name patterns:
            lowered = line.split()[0].lower()
            for pattern in ['error', 'exception', 'exist', 'empty', 'empty',
                            'missing', 'permission', 'denied', 'empty']:
                if pattern in lowered:
                    return line, None
    return None, None

def can_connect(*args):
    try:
        socket.create_connection(args).close()
        return True
    except socket.error, exc:
        if exc.errno == errno.ECONNREFUSED:
            return False
        raise
