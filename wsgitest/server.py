import os
import sys
import time
import inspect
import subprocess
import signal

from wsgitest import config

SERVER_RUNNER = os.path.join(os.path.dirname(__file__), os.pardir, 'run-server.py')

SIGNALS = dict((getattr(signal, k), '%s (%d)' % (k, getattr(signal, k)))
               for k in dir(signal) if k.isupper())


class Subprocess(subprocess.Popen):
    killed = False

    def terminate(self):
        rv = self.poll()
        if rv is None:
            time.sleep(0.01) # give the server a chance to flush stderr
            subprocess.Popen.terminate(self)
        else:
            if rv < 0 and rv != -15:
                rv = -rv
                self.killed = True
                self.killed_msg = SIGNALS.get(rv, rv)

        self.stderr_buf = self.stderr.read().strip('\n')

def run(test):
    app_file = inspect.getsourcefile(test.app)
    app_name = test.app.__name__
    proc = Subprocess(
        [sys.executable, SERVER_RUNNER, app_file, app_name],
        stderr=subprocess.PIPE
    )
    # give the server a chance to boot up
    time.sleep(config.SERVER_BOOT_DURATION)
    return proc
