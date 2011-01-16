from os import pardir
from os.path import abspath, join, dirname, realpath

DEFAULT_TESTS_DIR = abspath(join((dirname(realpath(__file__))), pardir, 'tests'))

del pardir, abspath, join, dirname, realpath
