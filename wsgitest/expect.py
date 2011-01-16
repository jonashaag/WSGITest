from wsgitest.utils import find_exception

class Expectation(object):
    def __new__(cls, *args, **kwargs):
        def decorator(func):
            if not hasattr(func, '_expectations'):
                func._expectations = []
            expectation = object.__new__(cls)
            expectation.__init__(*args, **kwargs)
            func._expectations.append(expectation)
            return func
        return decorator

    def validate(self, errors, *args):
        raise NotImplementedError

class ResponseExpectation(Expectation):
    def validate(self, errors, response):
        raise NotImplementedError

class ServerExpectation(Expectation):
    def validate(self, errors, stdout, stderr):
        raise NotImplementedError

class Status(ResponseExpectation):
    def __init__(self, status, reason=None):
        self.status = status
        self.reason = reason

    def validate(self, errors, response):
        if self.status is None:
            # Explicitly expect no status
            return
        status, reason = response.status, response.reason
        if self.reason is not None and reason != self.reason \
           and status != self.status:
            errors.append("Status is '%d %s', expected '%d %s'" % \
                          (status, reason, self.status, self.reason))
        elif self.reason is not None and reason != self.reason:
            errors.append('Status reason is %r, expected %r' % (reason, self.reason))
        elif status != self.status:
            errors.append('Status code is %d, expected %d' % (status, self.status))

class Header(ResponseExpectation):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def validate(self, errors, response):
        value = response.getheader(self.name)
        if value is None:
            errors.append('Missing expected header %r' % self.name)
        elif value != self.value:
            errors.append('Header %r: Got value %r, expected %r'
                          % (self.name, value, self.value))

class Body(ResponseExpectation):
    def __init__(self, body):
        self.body = body

    def validate(self, errors, response):
        if self.body != response.body:
            errors.append('Body is %r, expected %r' % (response.body, self.body))


class ServerError(ServerExpectation):
    def __init__(self, name, value=None):
        if not isinstance(name, (type(None), basestring)):
             name = name.__name__ # assuming `name` is a Exception-derived class
        if value is not None:
            assert name
        self.name = name
        self.value = value

    def validate(self, errors, stdout, stderr):
        exc_name, exc_value = find_exception(stderr)
        if exc_name is None:
            # No exception was found.  But what if one was expected?
            if self.name:
                errors.append('Server raised no execption, expected %r' % \
                              self.format_exception(self.name, self.value))
            return

        if self.name is None:
            errors.append('Server raised %r' % \
                          self.format_exception(exc_name, exc_value))
            return

        if '.' in exc_name and '.' not in self.name:
            # the exception raised by the server might be prefixed with
            # namespaces, e.g. "foo.bar.MyException". If no '.' could be
            # found in the expected exception name, we ignore all namespaces.
            # Matching "foo.bar.MyException" against "MyException" succeeds.
            # Matching "foo.bar.MyException" against "bar.MyException" doesn't.
            exc_name = exc_name.rsplit('.', 1)[1]

        if self.name != exc_name or \
           (self.value is not None and self.value != exc_value):
            errors.append('Server raised %r, expected %r' % \
                          (self.format_exception(exc_name, exc_value),
                           self.format_exception(self.name, self.value)))

    def format_exception(self, exc_name, exc_value):
        if exc_value is None:
            return exc_name
        else:
            return '%s: %s' % (exc_name, exc_value)
