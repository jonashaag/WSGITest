import bjoern

SERVER_PORT = 9998
SERVER_BOOT_DURATION = 0.05

def run_server(app, host, port):
    bjoern.route('.*')(app)
    bjoern.run(host, port)
