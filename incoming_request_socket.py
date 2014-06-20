from threading import Thread
from uuid import uuid4
import parse
from http_request_factory import HTTPRequestFactory
import logging
import sys, os

logging.basicConfig(filename='example.log',level=logging.DEBUG)

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
            print(self.id, self.buffer)
            try:
                parsed_request = parse.parse_request_header(self.buffer)
                if parsed_request:                    
                    request_handler.process(self.id, parsed_request, self.proxy)

                    # clear buffer because another request will come in, if not, only the original request will be loaded
                    
                    self.buffer = ''

                    print(self.id + '\n' + parsed_request.render())
                    #self.stop_flag = False # end thread (don't do this, this thread continues to receive new requests)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)


    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer += data

            if data == '':
                print('dropped this connection because \'\' sighted', self.id)
                self.proxy.drop_incoming_request(self.id)
        except Exception as e:
            print(self.id, 'IRS socket receive error', e)
            self.proxy.drop_incoming_request(self.id)

        

