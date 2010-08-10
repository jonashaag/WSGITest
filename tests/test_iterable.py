from wsgitest import expect

@expect.status(200, 'Ok')
@expect.body('hello\nfrom\na\nsimple\niterable')
@expect.header('Content-Length', '28')
def test_simple(env, start_response):
    start_response('200 Ok', [('Content-Length', '28')])
    yield 'hello\n'
    yield 'from\n'
    yield 'a\n'
    yield 'simple\n'
    yield 'iterable'

def test_with_error(env, start_response):
    start_response('200 Ok', [])
    yield 'foo'
    a # NameError
    yield 'bar'

@expect.status(321, 'blah')
@expect.body('hello world!')
@expect.header('Content-Length', '12')
def test_with_start_response_in_generator(env, start_response):
    x = False
    for item in ('hello ', 'wor', 'ld!'):
        if not x:
            x = True
            start_response('321 blah', [('Content-Length', '12')])
        yield item

@expect.body('thisisacustomstringfromacustomiterable')
@expect.header('Content-Length', None)
def test_custom_iterable(env, start_response):
    start_response('200 ok', [])
    class foo(object):
        def __iter__(self):
            for char in 'thisisacustomstringfromacustomiterable':
                yield char
    return foo()

@expect.body('thisisacustomstringfromacustomiterable'[:11])
@expect.header('Content-Length', '11')
def test_custom_iterable_with_len(env, start_response):
    start_response('200 ok', [('Content-Length', '11')])
    class foo(object):
        def __iter__(self):
            for char in 'thisisacustomstringfromacustomiterable':
                yield char
        def __len__(self):
            return 11
    return foo()
