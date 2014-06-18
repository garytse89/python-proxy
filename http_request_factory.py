from outgoing_request_socket import OutgoingRequestSocket

class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class HTTPRequestFactory(Borg):


    def __init__(self):
        Borg.__init__(self)
        self._actions = []
        self._actions.append(Get())

    def process(self, req_socket_id, req, proxy):
        for a in self._actions:
            if req._method == a.name.upper():
                a.execute(req_socket_id, req, proxy)

class IRequestAction(object):


    @property
    def name(self):
        return self._name

    def execute(self, path, args):
        raise NotImplementedError


class Get(IRequestAction):


    def __init__(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self, req_socket_id, req, proxy):
        try:
            ors = OutgoingRequestSocket(req_socket_id, req, proxy)
        except Exception, e:
            print 'Invalid GET Request', e

class Post(IRequestAction):


    def __init__(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self, req_socket_id, req, proxy):
        try:
            ors = OutgoingRequestSocket(req_socket_id, req, proxy)
        except Exception, e:
            print 'Invalid POST Request', e