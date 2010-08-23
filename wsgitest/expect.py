from functools import partial, wraps

def validator(validator_func):
    def validator(*args, **kwargs):
        @wraps(validator_func)
        def actual_validator(*args2):
            return validator_func(*(args2+args), **kwargs)

        def decorator(test_func):
            if not hasattr(test_func, '_validators'):
                test_func._validators = []
            if validator_func.__name__ == 'server_error':
                test_func._stderr_validator = actual_validator
            else:
                test_func._validators.append(actual_validator)
            return test_func
        decorator.validate = actual_validator
        return decorator
    return validator

@validator
def status(response, expected_status, expected_reason=None):
    if response.status != expected_status:
        yield 'Status is %s, expected %s' % (response.status, expected_status)
    if expected_reason is not None and response.reason != expected_reason:
        yield 'Reason is %r, expected %r' % (response.reason, expected_reason)

@validator
def header(response, name, expected_value):
    value = response.getheader(name)
    if value != expected_value:
        yield "Value of header %r is %r, expected %r" \
                % (name, value, expected_value)

@validator
def body(response, expected_body):
    import httplib
    try:
        body = response.read()
    except httplib.IncompleteRead as err:
        body = err.partial
    if body != expected_body:
        yield 'Body is %r, expected %r' % (body, expected_body)

@validator
def server_error(response, stderr, exception_name, exception_body=None):
    exc = stderr.split('\n')[-1]
    if exc:
        try:
            name, body = exc.split(':', 1)
        except ValueError:
            name = exc
            body = ''
    else:
        name, body = None, None
    if exception_name:
        # error expected, this implicits a @status(500)
        status(500).validate(response)
        # normalize exception_name
        if not isinstance(exception_name, str):
            exception_name = exception_name.__name__ # assume type exceptions.Foo
    if name == exception_name:
        return

    if name.split('.')[-1] == exception_name:
        # server may have raised something like 'foo.Error',
        # but expected is 'Error' -- so try to match when
        # module prefixes are stripped away
        return

    if exception_name:
        yield 'Server raised %s, expected %s' % (exc, exception_name)
    else:
        yield 'Server raised %s' % exc
