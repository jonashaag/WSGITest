import sys
import subprocess

if __name__ == '__main__':
    # Make sure the wsgitest module can be imported by fixing sys.path
    class I_like_to_abuse_classes_to_keep_the_module_namespace_clean:
        from os.path import join, abspath, dirname
        from os import pardir
        sys.path.append(abspath(join(dirname(abspath(__file__)), pardir)))

from wsgitest.utils import get_sourcefile


class Rack(object):
    def __init__(self):
        self.results = []
        self._running_servers = []

    def start_servers(self, tests):
        for index, test in enumerate(tests):
            proc = subprocess.Popen(
                [sys.executable, __file__, str(index),
                 get_sourcefile(test.app), test.app.__name__],
                #stderr=subprocess.PIPE#, stdout=subprocess.PIPE
            )
            self._running_servers.append(proc)

    def stop_servers(self):
        for proc in self._running_servers:
            proc.terminate()
            continue
            self.results.append(
                #ServerResult.from_output
                [
                    #proc.stdout.read(),
                    proc.stderr.read()
                ]
            )
        self._running_servers = []

if __name__ == '__main__':
    from wsgitest.config import SERVER_HOST, SERVER_PORT_RANGE, run_server
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
