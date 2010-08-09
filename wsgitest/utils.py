import os
import sys
import imp

def stderr(s=''):
    print >> sys.stderr, s

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
