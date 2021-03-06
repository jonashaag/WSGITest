from wsgitest import expect
from wsgitest.config import SERVER_HOST, SERVER_PORT_RANGE
from wsgitest.testutils import *

def test_GET(env, start_response):
    assert_equal(env['REQUEST_METHOD'], 'GET')
    start_response('200 ok', [])
    return ()

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

@expect.Status(400)
def test_BLAH(env, start_response):
    '''
    BLAH / HTTP/1.0
    '''
    assert_equal(env['REQUEST_METHOD'], 'BLAH')
    start_response('200 ok', [])
    return ''

# TODO: SCRIPT_NAME
#       PATH_INFO

def test_query_string(env, start_response):
    '''
    GET /hello?foo=bar&x=y HTTP/1.0
    '''
    assert_equal(env['QUERY_STRING'], 'foo=bar&x=y')
    start_response('200 ok', [])
    return iter(lambda: None, None)

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

def test_empty_query_string(env, start_response):
    '''
    GET / HTTP/1.0
    '''
    assert_equal(env.get('QUERY_STRING', ''), '')
    start_response('200 ok', [])
    return ['blah']

def test_server_star(env, start_response):
    assert_equal(env['SERVER_NAME'], SERVER_HOST)
    assert_contains(SERVER_PORT_RANGE, int(env['SERVER_PORT']))
    start_response('200 ok', [])
    return ()

def test_server_protocol(env, start_response):
    assert_equal(env['SERVER_PROTOCOL'], 'HTTP/1.1')
    start_response('200 ok', [])
    return []

def test_http_vars(env, start_response):
    '''
    GET /foo HTTP/1.1
    x-hello-iam-a-header: 42,42
    header-twice: 1
    IgNoREtheCAsE_pLeas-E: hello world!
    header-twice: 2
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
    assert_subdict(
        env,
        { 'HTTP_X_HELLO_IAM_A_HEADER'  : '42,42',
         'HEADER_TWICE'                : '1,2',
          'HTTP_IGNORETHECASE_PLEAS_E' : 'hello world!',
          'HTTP_AND_A_MULTILINE_VALUE' : 'foo 42 bar and so on'}
    )
    start_response('200 ok', [])
    return []

@expect.Status(200, 'ok')
def test_wsgi_vars(env, start_response):
    assert_isinstance(env['wsgi.version'], tuple)
    assert_equal(len(env['wsgi.version']), 2)
    assert_equal(env['wsgi.url_scheme'][:4], 'http')
    assert_isinstance(env['wsgi.multithread'], bool)
    assert_isinstance(env['wsgi.multiprocess'], bool)
    assert_isinstance(env['wsgi.run_once'], bool)
    start_response('200 ok', [])
    return []

@expect.Status(200)
@expect.Body('yay')
def test_input(env, start_response):
    '''
    POST /foo HTTP/1.1
    Content-Length: 29

    Hello<NL>World,\r<NL>\twhat's\r<NL>\r<NL><NL>up?
    '''
    input_ = env['wsgi.input']
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

@expect.Status(200)
@expect.Body('yay')
@expect.ServerError('ExpectedError')
def test_errors(env, start_response):
    errors = env['wsgi.errors']
    errors.write("Hello World, this is an error\n")
    errors.writelines(["Hello\n", "ExpectedError: blah"])
    errors.flush()
    start_response('200 ok', [])
    return 'yay'
