from wsgitest.utils import OrderedDict, docstring_to_request

DEFAULT_REQUEST = '''GET /wsgitest?version=0.2'''

class Testsuite(object):
    def __init__(self):
        self.tests = OrderedDict()

    def add_tests(self, module, tests):
        self.tests[module] = tests

    def validate_responses(self, responses):
        responses = iter(responses)
        results = []
        for module, tests in self.tests.iteritems():
            for test in tests:
                results.append(
                    test.validate_response(responses.next())
                )
        return results

class Test(object):
    def __init__(self, app, expectations, request=None):
        self.app = app
        self.request = request or DEFAULT_REQUEST
        self.expectations = expectations

    @classmethod
    def from_func(cls, testfunc):
        request = docstring_to_request(testfunc.__doc__)
        expectations = getattr(testfunc, '_expectations', ())
        return cls(testfunc, expectations, request)

    def validate_response(self, response):
        return response

class TestsuiteResult(object):
    def __init__(self, client_results, server_results):
        self.client_results = client_results
        self.server_results = server_results

    def summary(self):
        return self.client_results, self.server_results
