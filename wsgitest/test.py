import sys
import httplib
from itertools import chain, count
from wsgitest import expect, config
from wsgitest.utils import stderr

def normalize_docstring(docstr):
    docstr = docstr.strip('\n')
    return '\n'.join(
        line.lstrip() for line in docstr.split('\n')
    ).replace('\n\n', '\r\n')

class Request(object):
    def __init__(self, data):
        self.data = data

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
    def __init__(self, app, request, validators, _id=count(1)):
        self.id = _id.next()
        self.app = app
        self.request = request
        self.validators = validators

    @classmethod
    def from_func(cls, func):
        # always add server_error to the list of validators
        expect.server_error(None)(func)
        return cls(
            func,
            Request(normalize_docstring(func.__doc__)),
            func._validators
        )

    def get_validators(self):
        lazy_validators = []
        for validator in self.validators:
            if validator._lazy:
                lazy_validators.append(validator)
            else:
                yield validator
        for validator in reversed(lazy_validators):
            yield validator

    def run(self, server):
        exception_occurred = False
        server_process = server.run(self)
        try:
            response = self.request.send()
            response._subprocess = server_process
            self.errors = []
            for validator in self.get_validators():
                errors = tuple(validator(response))
                if errors:
                    self.errors.append((validator, errors))
        except:
            # skip errors for now, see below
            exception_occurred = True
        finally:
            # there may have been errors in the server process.
            # we definitely want to see them, because they can
            # explain for example a 'Connection refused' socket error.
            # print them first.
            server_process.terminate()
            stderr_outp = server_process.stderr.read()
            if stderr_outp:
                stderr('-' * 80)
                stderr('Expection in server:')
                stderr(stderr_outp.strip('\n'))
                stderr('-' * 80)

            # now, re-raise the original traceback, if any.
            if exception_occurred:
                raise

    @property
    def failed(self):
        return bool(self.errors)
