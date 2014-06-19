from threading import Thread
from uuid import uuid4
import parse
from http_request_factory import HTTPRequestFactory
import logging
import sys, os
LOGNAME = 'incoming'
f = '%(levelname)-6s %(filename)s ln.%(lineno)-4d %(message)s'
#logging.basicConfig(format=f,stream=sys.stdout)
logging.basicConfig(format=f, filename='example.log')
logger = logging.getLogger(LOGNAME).setLevel(logging.DEBUG)

request_handler = HTTPRequestFactory()

class IncomingRequestSocket(Thread):


    BUFFER_SIZE = 4096


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
                    request_handler.process(self.id, parsed_request, self.proxy)
                    #print(self.id + '\n' + parsed_request.render())
                    #self.stop_flag = False # end thread
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)


    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer += data

            print('{}\n{}'.format(self.id,self.buffer))
        except:
            data = ''

        if '' in data:
            pass #print('\'\' detected in socket id = {}'.format(self.id))

        if data == '':
            self.stop_flag = False
        else:
            return data

