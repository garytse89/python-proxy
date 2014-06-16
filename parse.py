from StringIO import StringIO

class HTTPObject(object):


    def add_parameter(self, k, v):
        self._parameters[k.title()] = v

    def get_content_length(self):
        try:
            return self._parameters['Content-Length']
        except KeyError:
            return None

    def _render(self, a, b, c):
        output = '{} {} {}\r\n'.format(a, b, c)
        for k,v in self._parameters.iteritems():
            output += '{}: {}\r\n'.format(k,v)
        output += '\r\n'
        return output



class HTTPRequest(HTTPObject): 

    def __init__(self):
        self._method = None
        self._path = None
        self._version = None
        self._parameters = {}

    def render(self):
        return self._render(self._method, self._path, self._version)



class HTTPResponse(HTTPObject): 

    def __init__(self):
        self._version = None
        self._status_number = None
        self._status_message = None
        self._parameters = {}


    def is_chunked(self):
        if self._parameters['Transfer-Encoding'] == 'chunked':
            return True
        return False

    def render(self):
        return self._render(self._version, self._status_number, self._status_message)


def read_parameters(reader, http_object):
    line = reader.readline()
    while line:
        line = line.strip('\r\n')
        args = line.split(':')
        if len(args) == 1:
            break
        http_object.add_parameter(args[0], args[1].strip(' '))
        line = reader.readline()

    return http_object



def parse_request_header(s):
    if '\r\n\r\n' not in s:
        raise Exception('Header not complete')

    reader = StringIO(s)
    http_info = reader.readline()
    http_info = http_info.strip('\r\n')
    http_info = http_info.split(' ')

    if len(http_info) != 3:
        raise Exception('Invalid HTTP info')

    http_request = HTTPRequest()
    http_request._method = http_info[0].upper()
    http_request._path = http_info[1]
    http_request._version = http_info[2] 

    read_parameters(reader, http_request)

    return http_request





def parse_response_header(s):

    if '\r\n\r\n' not in s:
        raise Exception('Header not complete')

    reader = StringIO(s)
    http_info = reader.readline()
    http_info = http_info.strip('\r\n')
    http_info = http_info.split(' ')

    if len(http_info) < 3:
        raise Exception('Invalid HTTP Response')

    http_response = HTTPResponse()
    http_response._version = http_info[0].upper()
    http_response._status_number = int(http_info[1])
    http_response._status_message = ' '.join(http_info[2:])

    read_parameters(reader, http_response)

    return http_response





    

