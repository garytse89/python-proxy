from outgoing_request_socket import OutgoingRequestSocket

class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class HTTPRequestFactory(Borg):


    def __init__(self, proxy):
        Borg.__init__(self)
        self._actions = []
        self._actions.append(Get(proxy))

    def process(self, request_type, host, incoming_request):

        for a in self._actions:
           if a.name.upper() in request_type: # if msg has a GET field, pass the message onto get request
                a.execute(incoming_request, host)

class IRequestAction(object):


    @property
    def name(self):
        return self._name

    def execute(self, path, args):
        raise NotImplementedError


class Get(IRequestAction):


    def __init__(self, proxy):
        self.proxy = proxy

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self, incoming_request, host):
        # create a socket to request from actual website
        ors = OutgoingRequestSocket(incoming_request, host)
        self.proxy.insert_outgoing_request(ors)
        ors.send_request()