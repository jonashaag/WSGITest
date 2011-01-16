import sys
import httplib
from itertools import count
from wsgitest.config import SERVER_HOST, SERVER_PORT_RANGE

class Client(object):
    def run(self, testsuite, servers=None):
        self.responses = []
        port_offset = count()

        for test in testsuite.tests.chainvalues():
            if servers:
                # start the next server
                servers.next()
            try:
                response = False, self.request(
                    SERVER_HOST,
                    SERVER_PORT_RANGE[port_offset.next()],
                    test.request
                )
            except:
                response = True, sys.exc_info()
            self.responses.append(response)

    def request(self, host, port, request):
        buf = []
        buf.append(' '.join([request.method, request.path, request.protocol]))
        for field in request.header:
            buf.append('%s: %s' % field)
        buf.extend(['', ''])

        connection = httplib.HTTPConnection(host, port)
        connection.send('\r\n'.join(buf))
        if request.body is not None:
            connection.send(request.body)
        connection._HTTPConnection__state = httplib._CS_REQ_SENT
        response = connection.getresponse()
        response.body = response.read()
        return response
