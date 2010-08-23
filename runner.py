import os
import sys
import textwrap
import inspect
from wsgitest import server
from wsgitest.test import Test
from wsgitest.utils import stderr, import_file


def usage(errmsg):
    stderr('wsgitest: %s' % errmsg)
    exit(128)

def find_test_files(folder):
    for root, folders, files in os.walk(folder):
        for file in files:
            yield os.path.join(root, file)

def find_tests(folders):
    for folder in folders:
        seen_files = set()
        for file in find_test_files(folder):
            if file.endswith('.pyc') and file[:-1] in seen_files:
                continue
            module = import_file(file)
            for name in dir(module):
                if name.startswith('test_'):
                    yield Test.from_func(getattr(module, name))
            seen_files.add(file)


def get_folders():
    argv = iter(sys.argv)
    argv.next()
    yield os.path.join(os.path.dirname(__file__), 'tests')
    for folder in argv:
        if os.path.isabs(folder):
            yield folder
        else:
            yield os.path.join(os.getcwd(), folder)

def to_str(obj):
    return obj if isinstance(obj, str) else obj.__name__

passed = []
failed = []

for test in find_tests(get_folders()):
    #print 'Running test %s...' % test.app.__name__
    test.run(server)
    if test.failed:
        failed.append(test)
        stderr('-' * 80)
        stderr('%s failed, here comes the full-sized report:' % test.name)
        stderr('.' * 80)
        for test_no, (validator, errors) in enumerate(test.errors, 1):
            stderr('%d) %s' % (test_no, to_str(validator).title()))
            for error in errors:
                stderr('   - %s' % '     \n'.join(textwrap.wrap(error, 75)))
        stderr('.' * 80)
        stderr()
    else:
        passed.append(test)

def _pprint_test(test, just):
    name = test.name
    filename = os.path.basename(inspect.getsourcefile(test.app))
    space = just - len(name) - len(filename)
    if space < 3:
        filename = filename[:just-len(name)-3]
    return name + (space * ' ') + filename

print
print '=' * 80
print 'SUMMARY'.center(80)
print '=' * 80
print 'Tests passed:'
for test in passed:
    print '   - %s' % _pprint_test(test, 75)
print '.' * 80

print 'Tests failed'
for test in failed:
    print '   - %s' % _pprint_test(test, 75)
print '.' * 80

if not failed:
    exit(0)
else:
    exit(1)
