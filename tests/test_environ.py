from wsgitest import expect
from wsgitest.config import SERVER_HOST, SERVER_PORT
from wsgitest.testutils import assert_equal, assert_isinstance

@expect.status(200, 'ok')
def test_GET(env, start_response):
    assert_equal(env['REQUEST_METHOD'], 'GET')
    start_response('200 ok', [])
    return ()

@expect.status(200, 'ok')
def test_POST(env, start_response):
    '''
    POST / HTTP/1.0
    Content-Length: 12

    hello\\nworld!
    '''
    assert_equal(env['REQUEST_METHOD'], 'POST')
    assert_equal(env['CONTENT_LENGTH'], '12')
    assert_equal(env['wsgi.input'].read(), 'hello\nworld!')
    start_response('200 ok', [])
    return []

@expect.status(400)
def test_BLAH(env, start_response):
    '''
    BLAH / HTTP/1.0
    '''
    assert_equal(env['REQUEST_METHOD'], 'BLAH')
    start_response('200 ok', [])
    return ''

# TODO: SCRIPT_NAME
#       PATH_INFO

@expect.status(200, 'ok')
def test_query_string(env, start_response):
    '''
    GET /hello?foo=bar&x=y HTTP/1.0
    '''
    assert_equal(env['QUERY_STRING'], 'foo=bar&x=y')
    start_response('200 ok', [])
    return iter(lambda: None, None)

@expect.status(200, 'ok')
def test_content__star(env, start_response):
    '''
    GET / HTTP/1.1
    Content-Type: text/x-python
    Content-Length: 3

    Hi!
    '''
    assert_equal(env['CONTENT_TYPE'], 'text/x-python')
    assert_equal(env['CONTENT_LENGTH'], '3')
    start_response('200 ok', [])
    return ['']

@expect.status(200, 'ok')
def test_empty_query_string(env, start_response):
    assert_equal(env.get('QUERY_STRING', ''), '')
    start_response('200 ok', [])
    return ['blah']

@expect.status(200, 'ok')
def test_server_star(env, start_response):
    assert_equal(env['SERVER_NAME'], SERVER_HOST)
    assert_equal(env['SERVER_PORT'], str(SERVER_PORT))
    start_response('200 ok', [])
    return ()

@expect.status(200, 'ok')
def test_server_protocol(env, start_response):
    assert_equal(env['SERVER_PROTOCOL'], 'HTTP/1.0')
    start_response('200 ok', [])
    return []

@expect.status(200, 'ok')
def test_http_vars(env, start_response):
    '''
    GET /foo HTTP/1.1
    x-hello-iam-a-header: 42,42
    IgNoREtheCAsE_pLeas-E: hello world!
    and-a-multiline-value: foo 42
    \tbar and\\r\\n\t
    \tso
     on
    '''
    # normalize the joined header because
    # RFC2616 does not specify whether
    # \r\n(\t| ) has to be replaced by ' '
    env['HTTP_AND_A_MULTILINE_VALUE'] = \
        env['HTTP_AND_A_MULTILINE_VALUE'].replace('\r\n', '').replace('\t', ' ')
    assert_equal(
        env,
        { 'HTTP_X_HELLO_IAM_A_HEADER' : '42,42',
          'HTTP_IGNORETHECASE_PLEAS_E' : 'hello world!',
          'HTTP_AND_A_MULTILINE_VALUE' : 'foo 42 bar and so on'}
    )
    start_response('200 ok', [])
    return []

@expect.status(200, 'ok')
def test_wsgi_vars(env, start_response):
    assert_isinstance(env['wsgi.version'], tuple)
    assert_equal(len(env['wsgi.version']), 2)
    assert_equal(env['wsgi.url_scheme'][:4], 'http')
    assert_isinstance(env['wsgi.multithread'], bool)
    assert_isinstance(env['wsgi.multiprocess'], bool)
    assert_isinstance(env['wsgi.run_once'], bool)
    start_response('200 ok', [])
    return []

@expect.status(200)
@expect.body('yay')
def test_input(env, start_response):
    '''
    GET /foo HTTP/1.1
    Content-Length: 29

    Hello\\nWorld,\\r\\n\twhat's\\r\\n\r\\n\\nup?
    '''
    input_ = env['wsgi.input']

    # test wsgi.input:
    assert_equal(input_.read(1), 'H')
    assert_equal(input_.readline(), 'ello\n')
    for line in input_:
        assert_equal(line, 'World,\r\n')
        break
    assert_equal(input_.read(4), '\twha')
    assert_equal(input_.readlines(), ["t's\r\n", "\r\n", "\n", "up?"])
    assert_equal(input_.read(123), '')

    start_response('200 ok', [])
    return 'yay'

@expect.status(200)
@expect.body('yay')
@expect.server_error('ExpectedError')
def test_errors(env, start_response):
    '''
    GET /foo HTTP/1.0
    Content-Length: 29

    Hello\\nWorld,\\r\\n\twhat's\\r\\n\\r\\n\\nup?
    '''
    errors = env['wsgi.errors']

    # test wsgi.errors:
    errors.write("Hello World, this is an error\n")
    errors.writelines(["Hello\n", "ExpectedError: blah"])
    errors.flush()

    start_response('200 ok', [])
    return 'yay'
