from wsgitest.utils import OrderedDict, chain_iterable
from wsgitest.request import Request
from wsgitest.expect import ResponseExpectation, Status, ServerError

DEFAULT_REQUEST = Request('GET', '/wsgitest?version=0.2')

class Test(object):
    def __init__(self, app, expectations, request=None):
        self.app = app
        self.request = request or DEFAULT_REQUEST
        self.expectations = expectations
        self.client_errors = []
        self.server_errors = []

    @classmethod
    def from_func(cls, testfunc):
        request = testfunc.__doc__
        if request is not None:
            request = Request.from_docstring(request)

        expectations = getattr(testfunc, '_expectations', ())

        error_expected = any(isinstance(exc, ServerError) for exc in expectations)
        status_expected = any(isinstance(exc, Status) for exc in expectations)
        if not error_expected:
            ServerError(None)(testfunc)
        elif not status_expected:
            Status(500)(testfunc)
        else:
            Status(200, 'ok')(testfunc)

        return cls(testfunc, expectations, request)

    def validate_response(self, response):
        isexception, value = response
        if isexception:
            self.client_errors.append(value)
        else:
            for expectation in self.expectations:
                if not isinstance(expectation, ResponseExpectation):
                    continue
                expectation.validate(self.client_errors, value)

    def validate_output(self, stdout, stderr):
        for expectation in self.expectations:
            if isinstance(expectation, ResponseExpectation):
                continue
            expectation.validate(self.server_errors, stdout, stderr)


class TestModuleDict(OrderedDict):
    def chainvalues(self):
        return chain_iterable(self.itervalues())

class Testsuite(object):
    def __init__(self):
        self.tests = TestModuleDict()

    def add_tests(self, module, tests):
        self.tests[module] = tests

    def get_result(self, client_responses, server_outputs, duration):
        for test, response in zip(self.tests.chainvalues(), client_responses):
            test.validate_response(response)
        for test, output in zip(self.tests.chainvalues(), server_outputs):
            test.validate_output(*output)
        return TestsuiteResult(self.tests, duration)

class TestsuiteResult(object):
    def __init__(self, tests, duration):
        self.tests = list(tests.chainvalues())
        self.failed_tests = filter(lambda x: x.client_errors or x.server_errors,
                                   self.tests)
        self.duration = duration

    def summary(self):
        if not self.failed_tests:
            return 'SUCCESS (ran %d tests in %2fs)' % (len(self.tests), self.duration)

        buf = []
        for test in self.failed_tests:
            buf.append('%r failed:' % test.app.__name__)
            for err in test.client_errors:
                buf.append('  * ' + str(err))
            for err in test.server_errors:
                buf.append('  * ' + str(err))
            buf.append('---')
        buf.append('%d tests failed (ran %d tests in %2fs)' %
                   (len(self.failed_tests), len(self.tests), self.duration))
        return '\n'.join(buf)
