import os
import optparse

DEFAULT_TESTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests')

parser = optparse.OptionParser()
parser.add_option('-d', dest='default_tests',
                  action='store_true', default=None)


if __name__ == '__main__':
    from wsgitest.run import run_tests

    options, files = parser.parse_args()

    if not files:
        if options.default_tests is None:
            options.default_tests = True

    if options.default_tests:
        files.append(DEFAULT_TESTS_DIR)

    result = run_tests(files)
    print result.summary()
