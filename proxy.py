import socket
import sys
from incoming_request_socket import IncomingRequestSocket

class Proxy(object):

    HOST = '10.10.100.114'                 
    PORT = 5001              

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._incoming_requests_list = []
        self._outgoing_requests_list = []
        self.stop_flag = True        

    def start(self):
        self.listen()

    def listen(self):
        self.socket.bind((Proxy.HOST, Proxy.PORT))
        self.socket.listen(5)
        try:
            while self.stop_flag:
                sock, addr = self.socket.accept()
                incoming_request = IncomingRequestSocket(self,sock)
                self._incoming_requests_list.append(incoming_request)
                incoming_request.start()
        except KeyboardInterrupt:
            self.stop_flag = False

        try: 
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except Exception, e:
            print e
        finally:
            self.shutdown()

    def shutdown(self):
        # close down all requests
        for request in self._incoming_requests_list:
            request.stop_flag = False
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception, e:
                print e

        for request in self._outgoing_requests_list:
            request.stop_flag = False
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception, e:
                print e

    def drop_incoming_request(self, r_id):
        for request in self._incoming_requests_list:
            if r_id == request.id:
                request.stop_flag = False
                try:
                    request.socket.shutdown(socket.SHUT_RDWR)
                    request.socket.close()
                except Exception, e:
                    print e
                finally:
                    self._incoming_requests_list.remove(request)

    def drop_outgoing_request(self, r_id):
        for request in self._outgoing_requests_list:
            if r_id == request.id:
                request.stop_flag = False
                try:
                    request.socket.shutdown(socket.SHUT_RDWR)
                    request.socket.close()
                except Exception, e:
                    print e
                finally:
                    self._outgoing_requests_list.remove(request)

    def insert_outgoing_request(self, oreq):
        self._outgoing_requests_list.append(oreq)


if __name__ == "__main__":
    proxy = Proxy()
    try:
        proxy.start()
    except Exception, e:
        proxy.stop_flag = False
        print e
    finally:
        sys.exit()

