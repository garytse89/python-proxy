import socket
import sys, os
from incoming_request_socket import IncomingRequestSocket

class Proxy(object):

    HOST = '10.10.100.114'                 
    PORT = 5001              

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._incoming_requests_list = {}
        self._outgoing_requests_list = {}
        self.stop_flag = True        

    def start(self):
        self.listen()

    def listen(self):
        self.socket.bind((Proxy.HOST, Proxy.PORT))
        self.socket.listen(5)
        try:
            while self.stop_flag:
                sock, addr = self.socket.accept()
                # buff = sock.recv(4096)
                # fp = open('buffer.dat', 'w')
                # fp.write(buff)
                # fp.close()
                # sys.exit(0)
                incoming_request = IncomingRequestSocket(self,sock)
                self.insert_incoming_request(incoming_request.id, sock)
                incoming_request.start()
        except KeyboardInterrupt:
            self.stop_flag = False

        try: 
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        finally:
            self.shutdown()

    def shutdown(self):
        # close down all requests
        for key, sock in self._incoming_requests_list.iteritems():
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        for key, request in self._outgoing_requests_list.iteritems():
            request.stop_flag = False
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

    def drop_incoming_request(self, r_id):
        try:
            request_sock = self._incoming_requests_list[r_id]
        except KeyError, e:
            return 

        if request_sock:            
            try:
                request_sock.shutdown(socket.SHUT_RDWR)
                request_sock.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            finally:
                del self._incoming_requests_list[r_id]

    def drop_outgoing_request(self, r_id):
        try:
            request = self._outgoing_requests_list[r_id]
        except KeyError, e:
            return 

        if request:
            request.stop_flag = False
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            finally:
                del self._outgoing_requests_list[r_id]

    def insert_incoming_request(self, sock_id, sock):
        self._incoming_requests_list[sock_id] = sock # not the thread

    def insert_outgoing_request(self, oreq_thread):
        self._outgoing_requests_list[oreq_thread.id] = oreq_thread # the actual thread

    def write(self, socket_id, response, content):
        content = "{}Content-Length:{}\r\n\r\n{}".format(response, len(content), content)
        try:
            self._incoming_requests_list[socket_id].send(content)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('error on proxy.py write where response = {}', e)
            # close the connection
            self.drop_incoming_request(socket_id)
            # print('error on proxy.py write where response = {}, \ncontent = {}'.format(response, content))

if __name__ == "__main__":
    proxy = Proxy()
    try:
        proxy.start()
    except Exception, e:
        proxy.stop_flag = False
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
    finally:
        sys.exit()

