from wsgitest import expect

def test_GET(env, start_response):
    assert env['REQUEST_METHOD'] == 'GET'
    start_response('200 ok', [])
    return ()

def test_POST(env, start_response):
    '''
    POST / HTTP/1.0
    '''
    assert env['REQUEST_METHOD'] == 'POST'
    start_response('200 ok', [])
    return []

def test_BLAH(env, start_response):
    '''
    BLAH / HTTP/1.0
    '''
    assert env['REQUEST_METHOD'] == 'BLAH'
    start_response('200 ok', [])
    return ''

# TODO: SCRIPT_NAME
#       PATH_INFO

def test_query_string(env, start_response):
    '''
    GET /hello?foo=bar&x=y
    '''
    assert env['QUERY_STRING'] == 'foo=bar&x=y'
    start_response('200 ok', [])
    return iter(lambda: None, None)

def test_empty_query_string(env, start_response):
    assert env.get('QUERY_STRING', '') == ''
    start_response('200 ok', [])
    return ['blah']

def test_server_star(env, start_response):
    from wsgitest import config
    assert env['SERVER_HOST'] == config.SERVER_HOST
    assert env['SERVER_PORT'] == str(config.SERVER_PORT)
    start_response('200 ok', [])
    return ()

def test_server_protocol(env, start_response):
    assert env['SERVER_PROTOCOL'] == 'HTTP/1.0'
    start_response('200 ok', [])
    return []

def test_http_vars(env, start_response):
    '''
    SOMEMETHOD /foo
    x-hello-iam-a-header: 42,42
    IgNoREtheCAsE_pLeas-E: hello world!
    and-a-multiline-value: foo 42
     bar and so
     on
    '''
    for k, v in {
        'HTTP_X_HELLO_IAM_A_HEADER' : '42,42',
        'HTTP_IGNORETHECASE_PLEAS_E' : 'hello world!',
        'AND_A_MULTILINE_VALUE' : 'foo 42 bar and so on'
    }:
        assert env[k] == v
    start_response('200 ok', [])
    return []

def test_wsgi_vars(env, start_response):
    assert isinstance(env['wsgi.version'], tuple)
    assert env['wsgi.url_scheme']
    assert env['wsgi.input']
    assert hasattr(env['wsgi.input'], 'close')
    assert env['wsgi.errors']
    assert hasattr(env['wsgi.errors'], 'close')
    assert isinstance(env['wsgi.multithread'], bool)
    assert isinstance(env['wsgi.multiprocess'], bool)
    assert isinstance(env['wsgi.run_once'], bool)
    start_response('200 ok', [])
    return []
