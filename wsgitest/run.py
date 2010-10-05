import os
from wsgitest.base    import Test, Testsuite, TestsuiteResult
from wsgitest.client  import Client
from wsgitest.server  import Rack
from wsgitest.utils   import import_file, chain_iterable

def find_tests(files_and_folders):
    files = []
    for obj in files_and_folders:
        if os.path.isfile(obj):
            files.append(obj)
            continue

        for file in os.listdir(obj):
            if file.endswith('.py'):
                files.append(os.path.join(obj, file))

    modules = []
    for file in files:
        modules.append(import_file(file))

    suite = Testsuite()
    for module in modules:
        module_tests = [Test.from_func(getattr(module, obj)) \
                        for obj in dir(module) if obj.startswith('test_')]
        if module_tests:
            suite.add_tests(module, module_tests)
    return suite

import time
def run_tests(files):
    testsuite = find_tests(files)
    rack = Rack()
    client = Client()
    number_of_tests = sum(map(len, testsuite.tests.itervalues()))

    rack.start_servers(chain_iterable(testsuite.tests.itervalues()))
    time.sleep(number_of_tests * 0.2)
    client.run(testsuite)
    rack.stop_servers()

    client_results = testsuite.validate_responses(client.responses)

    return TestsuiteResult(testsuite.tests, client_results, rack.results)
