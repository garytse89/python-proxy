import socket
from threading import Thread
from uuid import uuid4
from response_factory import ResponseFactory

import logging
logging.basicConfig(filename='example.log',level=logging.DEBUG)

response_handler = ResponseFactory()

class OutgoingRequestSocket(Thread):

    '''
    Sends out a request to remote host and retrieves the header
    '''

    BUFFER_SIZE = 1024


    def __init__(self, incoming_request, host):
        self.proxy = incoming_request.proxy
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = str(uuid4())
        self.stop_flag = True
        self.buffer = ''

        self.host = host
        self.request = incoming_request.request_string

        self.parsing_header = True

        super(OutgoingRequestSocket,self).__init__()

    def run(self):
        while self.stop_flag:
            self.read()            
            self.parse()
                      
    def parse(self):
        if self.parsing_header:
            self.read_header()
        else:
            self.read_body()

    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer = self.buffer + data
        except:
            self.proxy.drop_outgoing_request(self.id)
            data = ''
        return data


    def send_request(self):
        try:
            self.socket.connect((self.host, 80))
            self.socket.send(self.request)
            self.start()
        except Exception, e:
            print e

    def read_header(self):
        if '\r\n\r\n' in self.buffer: # unreliable

            logging.debug('THE OUTGOING REQUEST\n\n' + self.buffer)

            response = self.buffer.split('\n')
            header_dict = {}
            for field in response:
                field = field.split(': ')
                if len(field) > 1:
                    header_dict[field[0]] = field[1]

            # HTTP/1.1 200 OK field does not have a colon to use for parsing, add in manually
            header_dict['Status'] = response[0]        
            self.proxy.ResponseFactory.process(self, header_dict)
            self.parsing_header = False

    def read_body(self):
        

