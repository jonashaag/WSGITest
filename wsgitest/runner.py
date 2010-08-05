import sys
from itertools import count
from module import TestModule
import server

def print_(s=''):
    print >> sys.stderr, s

file = sys.argv[1]
module = TestModule.from_file(file)
for test in module.tests:
    test.run(server)
    if test.failed:
        print_('=' * 80)
        print_('Test %d failed, here comes the full-sized report:' % test.id)
        print_('-' * 80)
        counter = count(1)
        for validator, errors in test.errors:
            print_('%d) %s' % (counter.next(), validator.__name__.title()))
            for error in errors:
                print_('   - %s' % error)
        print_('-' * 80)
        print_()
