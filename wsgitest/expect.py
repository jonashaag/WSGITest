from functools import partial, wraps

def validator(validator_func, lazy=False):
    def validator(*args, **kwargs):
        def decorator(test_func):
            @wraps(validator_func)
            def actual_validator(response):
                return validator_func(response, *args, **kwargs)
            actual_validator._lazy = lazy
            if not hasattr(test_func, '_validators'):
                test_func._validators = []
            test_func._validators.append(actual_validator)
            return test_func
        return decorator
    return validator

lazy_validator = partial(validator, lazy=True)

@validator
def status(response, expected_status, expected_reason):
    if response.status != expected_status:
        yield 'Status is %d, expected %d' % (response.status, expected_status)
    if response.reason != expected_reason:
        yield 'Reason is %r, expected %r' % (response.reason, expected_reason)

@validator
def header(response, name, expected_value):
    value = response.getheader(name)
    if value != expected_value:
        yield "Value of header %r is %r, expected %r" \
                % (name, value, expected_value)

@validator
def body(response, expected_body):
    body = response.read()
    if body != expected_body:
        yield 'Body is %r, expected %r' % (body, expected_body)

@lazy_validator
def server_error(response, exception_name, exception_body=None):
    response._subprocess.terminate()
    exc = response._subprocess.stderr.read().strip('\n').split('\n')[-1]
    try:
        name, body = exc.split(':', 1)
    except ValueError:
        name, body = (None, None)
    if name != exception_name:
        if exception_name:
            yield 'Server raised %s, expected %s' % (exc, exception_name)
        else:
            yield 'Server raised %s' % exc
