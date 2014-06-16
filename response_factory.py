class ResponseFactory(object):


    def __init__(self, proxy):
        self.proxy = proxy
        self.chunked_response = ChunkedResponse()
        self.normal_response = NormalResponse()

    def process(self, request, header):
        if 'Transfer-Encoding' in header and not 'Content-Length' in header:
            return self.chunked_response.execute()
        elif 'Content-Length' in header:
            return self.normal_response.execute()
        raise Exception


class IResponseAction(object):


    @property
    def name(self):
        return self._name

    def execute(self):
        raise NotImplementedError


class NormalResponse(IResponseAction):


    def __init__(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self):
        print ('hi')

    # def execute(self, incoming_request, host):
    #     # create a socket to request from actual website
    #     o = OutgoingRequestSocket(incoming_request, host)
    #     self.proxy.insert_outgoing_request(o)
    #     o.request()


class ChunkedResponse(IResponseAction):


    def __init__(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self):
        print ('hi')
        
    # def execute(self, incoming_request, host):
    #     # create a socket to request from actual website
    #     o = OutgoingRequestSocket(incoming_request, host)
    #     self.proxy.insert_outgoing_request(o)
    #     o.request()