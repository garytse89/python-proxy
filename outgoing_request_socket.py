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


    def __init__(self, incoming_request, proxy):
        self.proxy = proxy
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = str(uuid4())
        self.stop_flag = True
        self.buffer = ''
        self.parsing_header = True

        self.proxy.insert_outgoing_request(self)

        super(OutgoingRequestSocket,self).__init__()

        host = incoming_request.host
        request_string = incoming_request.render()
        self.send_request(host, request_string)

    def run(self):
        while self.stop_flag:
            self.read()   
            print(self.buffer)
            try:
                parsed_response = parse.parse_response_header(self.buffer)
                if parsed_response:
                    # determine whether chunked
                    if parsed_response.is_chunked:
                        pass
                    else:
                        pass
            except:
                pass
                      
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


    def send_request(self, host, request):
        try:
            self.socket.connect((host, 80))
            self.socket.send(request)
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
        pass

