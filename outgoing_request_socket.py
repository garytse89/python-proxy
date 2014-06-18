import socket
import parse
from threading import Thread
from uuid import uuid4
from response_factory import ResponseFactory
import sys
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
        self.incoming_socket_id = incoming_request.id
        self.stop_flag = True
        self.buffer = ''

        self.parsing_header = True
        self._header = None
        self._chunked_body = ''
        self._chunked_size = 0

        self.proxy.insert_outgoing_request(self)

        super(OutgoingRequestSocket,self).__init__()

        host = incoming_request.host
        request_string = incoming_request.render()
        self.send_request(host, request_string)

    def run(self):
        while self.stop_flag:
            self.read_header()
            self.read_body()

    def read_header(self):      
        if self.parsing_header:
            self.read()
            try:
                parsed_response, remaining_buffer = parse.parse_response_header(self.buffer)
                if parsed_response:
                    self._header = parsed_response
                    self.buffer = remaining_buffer
                    self.parsing_header = False
                else:
                    print('buffer is ... ', self.buffer)
            except:                
                pass

    def read_body(self):
        if not self.parsing_header:
            self.read()
            if self._header.is_chunked:
                if self._chunked_size == 0:
                    try:
                        self._chunked_size, remaining_buffer = parse.parse_response_body_chunked_size(self.buffer)
                        if self._chunked_size > 0:
                            self.buffer = remaining_buffer
                        elif self._chunked_size == 0: # last chunk
                            print('getting last chunk = ', self.buffer)
                            self.buffer = remaining_buffer[5:] # 0\r\n\r\n
                            self.parsing_header = True
                    except:
                        pass
                elif self._chunked_size > 0:
                    # get body, but only write it out if valid
                    try:
                        self._chunked_body, remaining_buffer = parse.parse_response_body_chunked(self._chunked_size, self.buffer)
                        if self._chunked_body:
                            print('we shud be writing content of size = ', self._chunked_size)
                            self.write(self._chunked_body)
                            self.buffer = remaining_buffer
                            # set chunked size back to 0 to anticipate next chunk
                            self._chunked_size = 0     
                    except:
                        pass               
            else:
                parse.parse_response_body_content(self.buffer)
                      
    def parse(self):
        if self.parsing_header:
            self.read_header()
        else:
            self.read_body()

    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer = self.buffer + data
        except Exception, e:
            print e
            data = ''

        if data == '':
            print('drop orq')
            self.proxy.drop_outgoing_request(self.id)

        return data

    def write(self, content):
        self.proxy.write(self.incoming_socket_id, content)

    def send_request(self, host, request):
        try:
            self.socket.connect((host, 80))
            self.socket.send(request)
            self.start()
        except Exception, e:
            print e

