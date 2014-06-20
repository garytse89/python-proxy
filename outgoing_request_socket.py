import socket
import parse
from threading import Thread
from uuid import uuid4
from response_factory import ResponseFactory
import sys, os
import logging
import gzip
import zlib
from StringIO import StringIO
logging.basicConfig(filename='example.log',level=logging.DEBUG)

response_handler = ResponseFactory()

class OutgoingRequestSocket(Thread):

    '''
    Sends out a request to remote host and retrieves the header
    '''

    BUFFER_SIZE = 4096


    def __init__(self, incoming_socket_id, incoming_request, proxy):
        self.proxy = proxy
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = str(uuid4())
        self.incoming_socket_id = incoming_socket_id
        self.stop_flag = True
        self.buffer = ''
        self.remaining_buffer = '' # used for storing remaining data received that isn't part of header/chunked size

        self.parsing_header = True
        self._header = None
        self._content_body = ''
        self._content_length = 0
        self._chunked_body = ''
        self._chunked_size = 0 # would contain 17751 in int
        self._chunked_size_line = '' # contains '455d\r\n' for a chunked body size of 17751
        self._first_chunk = True

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
                parsed_response, self.remaining_buffer = parse.parse_response_header(self.buffer)
                if parsed_response:
                    self._header = parsed_response
                    print(self.incoming_socket_id + '\n' + parsed_response.render())                    
                    self.buffer = self.remaining_buffer
                    if not self._header.is_chunked:
                        self._content_length = int(self._header.get_argument('Content-Length'))
                    self.parsing_header = False
                else:
                    print('buffer is ... ', self.buffer)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

    def read_body(self):
        if not self.parsing_header:            
            # no need to do a read if the expected content length is already equal to the remaining buffer (leftover from reading the response header)
            if len(self.buffer) != self._content_length:
                self.read()

            if self._header.is_chunked:
                if self._chunked_size == 0:
                    try:
                        self._chunked_size, self._chunked_size_line = parse.parse_response_body_chunked_size(self.buffer)
                        self.handle_chunked_size()                        
                    except Exception as e:
                        print('ors read_body line 85', e)
                        
                elif self._chunked_size > 0:
                    # get body, but only write it out if valid
                    try:
                        self._chunked_body, self.remaining_buffer = parse.parse_response_body_chunked(self._chunked_size + len(self._chunked_size_line), self.buffer)
                        self.handle_chunked_body()
                            #print('{} trying to receive complete chunk, size of buffer = {}'.format(self.id, len(self.buffer)))
                    except Exception as e:
                        print('ors read_body line 94', e)       
            else:               
                self._content_body += parse.parse_response_body_content(self._content_length, self.buffer)
                if self._content_body:
                    self.write(self._content_body)

    def debugwrite1(self):
        fp = open('workingchunk.txt', 'w')
        fp.write(self._chunked_body)
        fp.close()

    def debugwrite2(self):
        fp = open('nonworkingchunk.txt', 'w')
        fp.write(self._chunked_body)
        fp.close()

    def handle_chunked_size(self):
        if self._chunked_size > 0:
            print('{} now trying to get chunk of size {}'.format(self.id, self._chunked_size))
        elif self._chunked_size == 0: # last chunk
            #print('getting last chunk = ', self.buffer)
            #temp = self.socket.recv(1024)
            self.proxy.drop_outgoing_request(self.id)

    def handle_chunked_body(self):
        if self._chunked_body:
            print('{} got complete chunk of size = {}, theres remaining buffer of size = {}'.format(self.id, len(self._chunked_body) - len(self._chunked_size_line), len(self.remaining_buffer)))
            self.write(self._chunked_body)
            self.debugwrite1()
            self.buffer = self.remaining_buffer
            # set chunked size back to 0 to anticipate next chunk
            self._chunked_size = 0 
            self._first_chunk = False
        else:
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
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            data = ''

        return data

    def write(self, content):
        # if content is gzipped, decode it
        #response_header = "{}\r\nContent-Length:{}\r\n\r\n{}".format(status, len(res), res)
        
        try:
            reader = StringIO(self._header.render())
            response = reader.readline() 
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        content = self._header.render() + content        
        self.proxy.write(self.incoming_socket_id, response, content)  

    def send_request(self, host, request):
        try:
            self.socket.connect((host, 80))
            self.socket.send(request)
            self.start()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

