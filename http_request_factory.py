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

    def process(self, req, proxy):
        # fp = open('buffer2.dat', 'w')
        # fp.write(req.render())
        # fp.close()
        # req is a HTTPRequest object from parse.py
        for a in self._actions:
            if req._method == a.name.upper():
                a.execute(req, proxy)

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

    def execute(self, req, proxy):
        try:
            ors = OutgoingRequestSocket(req, proxy)
        except Exception, e:
            print 'Invalid GET Request', e


class Post(IRequestAction):


    def __init__(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self, req, proxy):
        try:
            ors = OutgoingRequestSocket(req, proxy)
        except Exception, e:
            print 'Invalid GET Request', e