def assert_equal(a, b):
    assert a == b, '%r != %r (expected the latter)' % (a, b)

def assert_isinstance(obj, types):
    assert isinstance(obj, types), \
        '%r object of type %r not of type(s) %r' % (obj, type(obj), types)

def assert_subdict(a, b):
    a_sub = dict((k, a[k]) for k in b)
    assert_equal(a_sub, b)
