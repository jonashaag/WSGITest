import os
from module import import_file

_conf_module = import_file(os.path.join(os.getcwd(), 'config.py'))

SERVER_HOST = getattr(_conf_module, 'SERVER_HOST', '127.0.0.1')
SERVER_PORT = getattr(_conf_module, 'SERVER_PORT', 9999)
SERVER_BOOT_DURATION = _conf_module.SERVER_BOOT_DURATION

def run_server(app):
    _conf_module.run_server(app, SERVER_HOST, SERVER_PORT)
