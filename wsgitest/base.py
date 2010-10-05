from wsgitest.utils import OrderedDict
from wsgitest.request import Request
from wsgitest.expect import ResponseExpectation

DEFAULT_REQUEST = Request('GET', '/wsgitest?version=0.2')

class Test(object):
    def __init__(self, app, expectations, request=None):
        self.app = app
        self.request = request or DEFAULT_REQUEST
        self.expectations = expectations

    @classmethod
    def from_func(cls, testfunc):
        request = testfunc.__doc__
        if request is not None:
            request = Request.from_docstring(request)
        expectations = getattr(testfunc, '_expectations', ())
        return cls(testfunc, expectations, request)

    def validate_response(self, response):
        result = TestResult()
        for expectation in self.expectations:
            if not isinstance(expectation, ResponseExpectation):
                continue
            expectation.validate(result, response)
        return result

class TestResult(list):
    pass


class Testsuite(object):
    def __init__(self):
        self.tests = OrderedDict()

    def add_tests(self, module, tests):
        self.tests[module] = tests

    def validate_responses(self, responses):
        results = []
        for module, tests in self.tests.iteritems():
            for test, response in zip(tests, responses):
                if isinstance(response, tuple) and len(response) == 3:
                    # exception
                    results.append(response)
                else:
                    # http response
                    results.append(test.validate_response(response))
        return results

class TestsuiteResult(object):
    def __init__(self, tests, client_results, server_results):
        self.tests = tests
        self.client_results = client_results
        self.server_results = server_results

    def summary(self):
        for module, tests in self.tests.iteritems():
            for test, (client_errors, server_errors) in \
                zip(tests, zip(self.client_results, self.server_results)):
                if client_errors or server_errors:
                    print test.app.__name__
                    print client_errors
                    print server_errors
                    print
