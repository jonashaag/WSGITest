import os
import sys
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

passed = []
failed = []

for test in find_tests(get_folders()):
    test.run(server)
    if test.failed:
        failed.append(test)
        stderr('=' * 80)
        stderr('Test %d failed, here comes the full-sized report:' % test.id)
        stderr('-' * 80)
        for test_no, (validator, errors) in enumerate(test.errors, 1):
            stderr('%d) %s' % (test_no, validator.__name__.title()))
            for error in errors:
                stderr('   - %s' % error)
        stderr('-' * 80)
        stderr()
    else:
        passed.append(test)

print 'SUMMARY: %d tests passed, %d failed' % (len(passed), len(failed))
