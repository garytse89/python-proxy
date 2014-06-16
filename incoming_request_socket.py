from threading import Thread
from uuid import uuid4
import parse
from http_request_factory import HTTPRequestFactory

request_handler = HTTPRequestFactory()

class IncomingRequestSocket(Thread):


    BUFFER_SIZE = 1024


    def __init__(self, proxy, sock):
        self.proxy = proxy
        self.id = str(uuid4())
        self.socket = sock
        self.stop_flag = True
        self.buffer = ''

        self.request_string = None
        self.request = None

        super(IncomingRequestSocket,self).__init__()


    def run(self):
        while self.stop_flag:
            self.read()
            try:
                parsed_request = parse.parse_request_header(self.buffer)
                if parsed_request:
                    request_handler.process(parsed_request)
            except:
                pass
                

    def parse(self):
        pass
        # if '\r\n\r\n' in self.buffer:
        #     self.request_string = self.buffer
        #     print self.buffer
        #     self.request = self.buffer.split('\r\n')
        #     host = (self.request[1])[6:]
        #     request_type = self.request[0] # 'GET'
        #     self.proxy.HTTPRequestFactory.process(request_type, host, self)


    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer += data
        except:
            self.proxy.drop_incoming_request(self.id)
            data = ''
        return data

