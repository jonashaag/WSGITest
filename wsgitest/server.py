import os
import sys
import time
import inspect
import subprocess

from wsgitest import config

SERVER_RUNNER = os.path.join(os.path.dirname(__file__), os.pardir, 'run-server.py')

def run(test):
    app_file = inspect.getsourcefile(test.app)
    app_name = test.app.__name__
    proc = subprocess.Popen(
        [sys.executable, SERVER_RUNNER, app_file, app_name],
        stderr=subprocess.PIPE
    )
    # give the server a chance to boot up
    time.sleep(config.SERVER_BOOT_DURATION)
    return proc
