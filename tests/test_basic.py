from wsgitest import expect

@expect.status(200, 'Ok')
@expect.header('Content-Length', '5')
@expect.body('hello')
def test_basic(environ, start_response):
    '''
    GET / HTTP/1.1
    '''
    start_response('200 Ok', ())
    return ['hello']
