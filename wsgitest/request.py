from wsgitest.utils import normalize_docstring

class MalformedHeader(Exception):
    pass

class Request(object):
    def __init__(self, method, path, protocol='HTTP/1.1', header=None, body=None):
        self.method = method
        self.path = path
        self.protocol = protocol
        self.header = header or []
        if isinstance(body, (dict, tuple, list)):
            if method != 'POST':
                raise TypeError(
                    "body may only be sequence/mapping if method is 'POST'")
            else:
                raise NotImplementedError()
        self.body = body

    @classmethod
    def from_docstring(cls, docstring):
        lines = normalize_docstring(docstring)
        method, path, protocol = lines.next().split()
        header = []
        name = value = None
        for line in lines:
            if not line:
                # end of header
                body = lines
                break
            if line[0] in ' \t':
                if name is None:
                    raise MalformedHeader('Continuation without field name')
                # continue previous value
                value += '\r\n' + line
            else:
                if name is not None:
                    header.append((name, value))
                    name = value = None
                name, value = line.split(': ')
        else:
            body = None

        return cls(method, path, protocol, header, body)
