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

    def validate(self, response, errors):
        raise NotImplementedError()

class Status(Expectation):
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def validate(self, response, errors):
        status, message = response.status.split()
        status = int(status)
        if self.message is not None and message != self.message \
           and status != self.status:
            errors.add("Status is %r, expected '%d %s'"
                       % (response.status, self.status, self.message))
        elif self.message is not None and message != self.message:
            errors.add('Status message is %r, expected %r'
                       % (message, self.message))
        elif status != self.status:
            errors.add('Status code is %d, expected %d' % (status, self.status))

class Header(Expectation):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def validate(self, response, errors):
        if self.name not in response.headers:
            errors.add('Missing expected header%r' % self.name)
        elif response.headers[self.name] != self.value:
            errors.add('Header %r: Got value %r, expected %r'
                       % (self.name, response.headers[self.name], self.value))

class Body(Expectation):
    def __init__(self, body):
        self.body = body

    def validate(self, response, errors):
        if self.body != response.body:
            errors.add('Body is %r, expected %r' % (response.body, self.body))

class ServerError(Expectation):
    def __init__(self, name):
        if not isinstance(name, basestring):
             name = name.__name__ # assuming `name` is a Exception-derived class
        self.name = name

    def validate(self, response, errors):
        return
