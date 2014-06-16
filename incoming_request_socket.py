from threading import Thread
from uuid import uuid4

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
        print 'run'
        while self.stop_flag:
            self.read()            
            self.parse()
                

    def parse(self):
        if '\r\n\r\n' in self.buffer:
            self.request_string = self.buffer
            self.request = self.buffer.split('\r\n')
            host = (self.request[1])[6:]
            request_type = self.request[0] # 'GET'
            self.proxy.HTTPRequestFactory.process(request_type, host, self)


    def read(self):
        try:
            data = self.socket.recv(self.BUFFER_SIZE)
            self.buffer = self.buffer + data
        except:
            self.proxy.drop_incoming_request(self.id)
            data = ''
        return data

