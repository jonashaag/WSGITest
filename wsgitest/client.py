import sys
import httplib
from itertools import count
from wsgitest.config import SERVER_HOST, SERVER_PORT_RANGE

class Client(object):
    def run(self, testsuite):
        self.responses = []
        port_offset = count()

        for module, tests in testsuite.tests.iteritems():
            for test in tests:
                try:
                    response = self.request(
                        SERVER_HOST,
                        SERVER_PORT_RANGE[port_offset.next()],
                        test.request
                    )
                except:
                    response = sys.exc_info()
                self.responses.append(response)

    def request(self, host, port, raw_request):
        raw_request = self.prepare_raw_request(raw_request)
        connection = httplib.HTTPConnection(host, port)
        connection.send(raw_request)
        connection._HTTPConnection__state = httplib._CS_REQ_SENT
        return connection.getresponse()

    def prepare_raw_request(self, raw_request):
        header_end = raw_request.find('\r\n\r\n')
        if raw_request.find('User-Agent', header_end) != -1:
            # no User-Agent found
            first_line_end = raw_request.find('\r\n') + 2
            if first_line_end == 1: # -1 + 2 = 1
                first_line_end = len(raw_request)
            return raw_request[:first_line_end] + 'User-Agent: %s\r\n' + raw_request[first_line_end:]
        return raw_request
