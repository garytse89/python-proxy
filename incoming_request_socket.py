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


    # what if POST
    # parse request header wont work under all conditions
    def run(self):
        while self.stop_flag:
            self.read()
            try:
                parsed_request = parse.parse_request_header(self.buffer)
                if parsed_request:                    
                    request_handler.process(parsed_request, self.proxy)
                    self.stop_flag = False # end thread
            except:
                pass


    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer += data
        except:
            self.stop_flag = False
            self.proxy.drop_incoming_request(self.id)
            data = ''
        return data

