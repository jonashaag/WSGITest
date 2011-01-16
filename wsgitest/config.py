SERVER_HOST = '127.0.0.1'
SERVER_PORT_RANGE = xrange(8000, 9000)
SERVER_BOOT_DURATION = 0.3
USER_AGENT = 'wsgitest/0.2'

def run_server(app, host, port):
    from fapws import base
    from fapws._evwsgi import start, set_base_module, wsgi_cb, run
    start(host, str(port))
    set_base_module(base)
    wsgi_cb(('/', app))
    run()

from bjoern import run as run_server
