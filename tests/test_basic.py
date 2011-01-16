from wsgitest import expect

@expect.Body('hello')
def test_empty_header(env, start_response):
    start_response('200 ok', [])
    return ['hello']

@expect.Header('Content-Length', '5')
@expect.Body('hello')
def test_with_content_length(env, start_response):
    start_response('200 ok', [('Content-Length', '5')])
    return ['hello']

@expect.ServerError(TypeError)
def test_too_few_arguments(env, start_response):
    start_response('200 ok')
    return []

@expect.ServerError(TypeError)
def test_too_many_arguments(env, start_response):
    start_response('200 ok', [], 42, 42)
    return []

@expect.ServerError(TypeError)
def test_wrong_types1(env, start_response):
    start_response(object(), [])
    return ['hello']

@expect.ServerError(TypeError)
def test_wrong_types2(env, start_response):
    start_response('200 ok', object())
    return ['hello']

@expect.ServerError(TypeError)
def test_illegal_return_type_and_arguments(env, start_response):
    start_response('200 ok')
    return object()

@expect.ServerError(TypeError)
def test_multiple_start_response(env, start_response):
    start_response('200 ok', [])
    start_response('200 ok', [])
    return ['hello']
