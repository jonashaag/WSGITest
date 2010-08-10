import sys
import httplib
from itertools import chain, count
from wsgitest import expect, config
from wsgitest.utils import stderr

def normalize_docstring(docstr):
    if not docstr:
        return docstr
    docstr = docstr.strip('\n')
    return '\n'.join(
        line.lstrip() for line in docstr.split('\n')
    ).replace('\n\n', '\r\n')

class Request(object):
    DEFAULT_DATA = 'GET / HTTP/1.0'''
    def __init__(self, data=None):
        self.data = data or self.DEFAULT_DATA

    def connect(self):
        return httplib.HTTPConnection(
            config.SERVER_HOST,
            config.SERVER_PORT
        )

    def send(self):
        connection = self.connect()
        connection.send(self.data)
        # workahack for httplibs stupid internal state
        connection._HTTPConnection__state = httplib._CS_REQ_SENT
        return connection.getresponse()

class Test(object):
    def __init__(self, app, request, validators, stderr_validator, _id=count(1)):
        self.id = _id.next()
        self.app = app
        self.request = request
        self.validators = validators
        self.stderr_validator = stderr_validator

    @classmethod
    def from_func(cls, func):
        if not hasattr(func, '_stderr_validator'):
            # make sure someone takes care of the server stderr
            expect.server_error(None)(func)
        return cls(
            func,
            Request(normalize_docstring(func.__doc__)),
            func._validators,
            func._stderr_validator
        )

    def run(self, server):
        self.errors = []
        exception_occurred = False
        server_process = server.run(self)
        try:
            response = self.request.send()
            response._subprocess = server_process
            for validator in self.validators:
                errors = tuple(validator(response))
                if errors:
                    self.errors.append((validator, errors))
            if server_process.terminate():
                errors = tuple(self.stderr_validator(response, server_process.stderr_buf))
                if errors:
                    self.errors.append((self.stderr_validator, errors))
        except httplib.BadStatusLine:
            self.errors.append(('Response', ['empty (probably server segfault)']))
        except:
            # skip errors for now, see below
            exception_occurred = True
        finally:
            # there may have been errors in the server process.
            # we definitely want to see them, because they can
            # explain for example a 'Connection refused' socket error.
            # print them first.
            if server_process.terminate():
                if server_process.stderr_buf:
                    stderr('-' * 80)
                    stderr('Uncatched expection in server:')
                    stderr(server_process.stderr_buf.strip('\n'))
                    stderr('-' * 80)

            if server_process.killed:
                self.errors.append(('Killed', [server_process.killed_msg]))

            # now, re-raise the original traceback, if any.
            if exception_occurred:
                raise

    @property
    def failed(self):
        return bool(self.errors)
