import sys
import time
import subprocess

if __name__ == '__main__':
    # Make sure the wsgitest module can be imported by fixing sys.path
    from os.path import join, abspath, dirname
    from os import pardir
    sys.path.append(abspath(join(dirname(abspath(__file__)), pardir)))
    del join, abspath, dirname, pardir

from wsgitest.utils import get_sourcefile, can_connect
from wsgitest.config import run_server, SERVER_HOST, SERVER_PORT_RANGE, \
                            SERVER_BOOT_DURATION

class Rack(object):
    def __init__(self):
        self.outputs = []
        self._running_servers = []

    def start_servers_lazily(self, tests):
        for index, test in enumerate(tests):
            test.proc = subprocess.Popen(
                [sys.executable, __file__, str(index),
                 get_sourcefile(test.app), test.app.__name__],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            self._running_servers.append(test)
            time.sleep(SERVER_BOOT_DURATION)
            yield

    def start_all_servers(self, tests):
        for server in self.start_servers_lazily(tests):
            pass
        dummy_server = subprocess.Popen([sys.executable, __file__, str(index+1),
                                         __file__, 'dummy'])
        while not can_connect(SERVER_HOST, SERVER_PORT_RANGE[index+1]):
            time.sleep(0.1)
        dummy_server.terminate()

    def stop_servers(self):
        for test in self._running_servers:
            test.proc.terminate()
            self.outputs.append([test.proc.stdout.read(), test.proc.stderr.read()])
        self._running_servers = []

    def __del__(self):
        self.stop_servers()


if __name__ == '__main__':
    from wsgitest.exceptions import ImproperlyConfigured
    from wsgitest.utils import import_file

    i_am_number = int(sys.argv[1])
    app_file = sys.argv[2]
    app_name = sys.argv[3]
    app = getattr(import_file(app_file), app_name)

    try:
        port = SERVER_PORT_RANGE[i_am_number]
    except IndexError:
        raise ImproperlyConfigured("Too small port range for all tests")

    run_server(app, SERVER_HOST, port)
else:
    from wsgitest.utils import dummy
