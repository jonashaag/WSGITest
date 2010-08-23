from wsgitest import expect
from wsgitest.config import SERVER_HOST, SERVER_PORT

@expect.status(200, 'ok')
def test_GET(env, start_response):
    assert env['REQUEST_METHOD'] == 'GET'
    start_response('200 ok', [])
    return ()

@expect.status(200, 'ok')
def test_POST(env, start_response):
    '''
    POST / HTTP/1.0
    Content-Length: 12

    hello\\nworld! ... stuff that shouldn't be read ...
    '''
    assert env['REQUEST_METHOD'] == 'POST'
    assert env['CONTENT_LENGTH'] == '12'
    assert env['wsgi.input'].read() == 'hello\nworld!'
    start_response('200 ok', [])
    return []

@expect.status(400)
def test_BLAH(env, start_response):
    '''
    BLAH / HTTP/1.0
    '''
    assert env['REQUEST_METHOD'] == 'BLAH'
    start_response('200 ok', [])
    return ''

# TODO: SCRIPT_NAME
#       PATH_INFO

@expect.status(200, 'ok')
def test_query_string(env, start_response):
    '''
    GET /hello?foo=bar&x=y HTTP/1.0
    '''
    try:
        assert env['QUERY_STRING'] == 'foo=bar&x=y'
    except KeyError:
        pass # QUERY_STRING needn't be given
    start_response('200 ok', [])
    return iter(lambda: None, None)

@expect.status(200, 'ok')
def test_content__star(env, start_response):
    '''
    GET / HTTP/1.0
    Content-Type: text/x-python

    Hi!
    '''
    assert env['CONTENT_TYPE'] == 'text/x-python'
    try:
        assert env['CONTENT_LENGTH'] == '3'
    except KeyError:
        # CONTENT_LENGTH may be absent if not stated explicitly in the request
        pass
    start_response('200 ok', [])
    return ['']

@expect.status(200, 'ok')
def test_empty_query_string(env, start_response):
    assert env.get('QUERY_STRING', '') == ''
    start_response('200 ok', [])
    return ['blah']

@expect.status(200, 'ok')
def test_server_star(env, start_response):
    from wsgitest import config
    assert env['SERVER_NAME'] == config.SERVER_HOST
    assert env['SERVER_PORT'] == str(config.SERVER_PORT)
    start_response('200 ok', [])
    return ()

@expect.status(200, 'ok')
def test_server_protocol(env, start_response):
    assert env['SERVER_PROTOCOL'] == 'HTTP/1.0'
    start_response('200 ok', [])
    return []

@expect.status(200, 'ok')
def test_http_vars(env, start_response):
    '''
    GET /foo HTTP/1.0
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
    assert env == {
        'HTTP_X_HELLO_IAM_A_HEADER' : '42,42',
        'HTTP_IGNORETHECASE_PLEAS_E' : 'hello world!',
        'HTTP_AND_A_MULTILINE_VALUE' : 'foo 42 bar and so on'
    }, env
    start_response('200 ok', [])
    return []

@expect.status(200, 'ok')
def test_wsgi_vars(env, start_response):
    assert isinstance(env['wsgi.version'], tuple) \
            and len(env['wsgi.version']) == 2
    assert env['wsgi.url_scheme'].startswith('http')
    assert isinstance(env['wsgi.multithread'], bool)
    assert isinstance(env['wsgi.multiprocess'], bool)
    assert isinstance(env['wsgi.run_once'], bool)
    start_response('200 ok', [])
    return []

@expect.status(200)
@expect.body('yay')
def test_input(env, start_response):
    '''
    GET /foo HTTP/1.1
    Content-Length: 29

    Hello\\nWorld,\\r\\n\twhat's\\r\\n\r\\n\\nup?\\r\\n\\r\\n..thismustbeignored
    '''
    input_ = env['wsgi.input']

    # test wsgi.input:
    assert input_.read(1) == 'H'
    assert input_.readline() == 'ello\n'
    for line in input_:
        assert line == 'World,'
    assert input_.read(3) == 'wha'
    assert input_.readlines() == ["t's\r\n", "\r\n", "\n", "up?"]
    assert input_.read(123) == ''

    start_response('200 ok', [])
    return 'yay'

@expect.status(200)
@expect.body('yay')
def test_errors(env, start_response):
    '''
    GET /foo HTTP/1.1
    Content-Length: 29

    Hello\\nWorld,\\r\\n\twhat's\\r\\n\\r\\n\\nup?\\r\\n\\r\\n.thismustbeignored
    '''
    errors = env['wsgi.errors']

    # test wsgi.errors:
    errors.write("Hello World, this is an error")
    errors.writelines(["Hello", "again"])
    errors.flush()

    start_response('200 ok', [])
    return 'yay'
