from wsgitest import expect

@expect.Status(200, 'Ok')
@expect.Body('hello')
def test_empty_headers(env, start_response):
    start_response('200 Ok', [])
    return ['hello']

@expect.Status(200, 'Ok')
@expect.Header('Content-Length', '5')
@expect.Body('hello')
def test_with_content_length(env, start_response):
    start_response('200 Ok', [('Content-Length', '5')])
    return ['hello']

@expect.ServerError(TypeError)
def test_too_few_arguments(env, start_response):
    start_response('200 Ok')
    return []

@expect.ServerError(TypeError)
def test_too_many_arguments(env, start_response):
    start_response('200 Ok', [], 42, 42)
    return []

@expect.ServerError(TypeError)
def test_wrong_types1(env, start_response):
    start_response(object(), [])
    return ['hello']

@expect.ServerError(TypeError)
def test_wrong_types2(env, start_response):
    start_response('200 Ok', object())
    return ['hello']

@expect.ServerError(TypeError)
def test_illegal_return_type_and_arguments(env, start_response):
    start_response('200 Ok')
    return object()

class MyError(Exception):
    pass
@expect.Status(500, 'error')
@expect.ServerError(MyError)
def test_myerror(env, start_response):
    start_response('200 ok', [])
    try:
        raise MyError
    except:
        import sys
        exc_info = sys.exc_info()
    start_response('500 error', [], exc_info)
    return ['hello']

@expect.ServerError(TypeError)
def test_multiple_start_response(env, start_response):
    start_response('200 ok', [])
    start_response('200 ok', [])
    return ['hello']
