from wsgitest import expect

@expect.Status(200, 'Ok')
@expect.Body('hello\nfrom\na\nsimple\niterable')
@expect.Header('Content-Length', '28')
def test_simple(env, start_response):
    start_response('200 Ok', [('Content-Length', '28')])
    yield 'hello\n'
    yield 'from\n'
    yield 'a\n'
    yield 'simple\n'
    yield 'iterable'

@expect.ServerError(NameError)
# no expectations for body/status here,
# because the response in this is undefined.
def test_with_error(env, start_response):
    start_response('200 Ok', [])
    yield 'foo'
    a # NameError
    yield 'bar'

@expect.Status(321, 'blah')
@expect.Body('hello world!')
@expect.Header('Content-Length', '12')
def test_with_start_response_in_generator(env, start_response):
    x = False
    for item in ('hello ', 'wor', 'ld!'):
        if not x:
            x = True
            start_response('321 blah', [('Content-Length', '12')])
        yield item

@expect.Body('thisisacustomstringfromacustomiterable')
@expect.Header('Content-Length', None)
def test_custom_iterable(env, start_response):
    start_response('200 ok', [])
    class foo(object):
        def __iter__(self):
            for char in 'thisisacustomstringfromacustomiterable':
                yield char
    return foo()

@expect.Body('thisisacustomstringfromacustomiterable'[:11])
@expect.Header('Content-Length', '11')
def test_custom_iterable_with_len(env, start_response):
    start_response('200 ok', [('Content-Length', '11')])
    class foo(object):
        def __iter__(self):
            for char in 'thisisacustomstringfromacustomiterable':
                yield char
        def __len__(self):
            return 11
    return foo()
