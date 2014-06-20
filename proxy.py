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
                #print('new request!!!! {} {}'.format(sock,addr))
                incoming_request = IncomingRequestSocket(self,sock)
                #print('made a socket for it with id ={}'.format(incoming_request.id))
                self.insert_incoming_request(incoming_request)
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
        for key, request in self._incoming_requests_list.iteritems():
            request.stop_flag = False
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(e, exc_type, fname, exc_tb.tb_lineno)

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
        request = self._incoming_requests_list[r_id]
        if request:  
            request.stop_flag = False          
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception as e:
                pass
            finally:
                del self._incoming_requests_list[r_id]

    def drop_outgoing_request(self, r_id):
        request = self._outgoing_requests_list[r_id]
        if request:
            request.stop_flag = False
            try:
                request.socket.shutdown(socket.SHUT_RDWR)
                request.socket.close()
            except Exception as e:
                pass
            finally:
                del self._outgoing_requests_list[r_id]

    def insert_incoming_request(self, ireq_thread):
        self._incoming_requests_list[ireq_thread.id] = ireq_thread
        print('Current # of ireq = ', len(self._incoming_requests_list))

    def insert_outgoing_request(self, oreq_thread):
        self._outgoing_requests_list[oreq_thread.id] = oreq_thread

    def write(self, r_id, response, content):
        #content = "{}Content-Length:{}\r\n\r\n{}".format(response, len(content), content)
        try:
            ireq_thread = self._incoming_requests_list[r_id]
            ireq_thread.socket.send(content)
        except Exception as e:
            #self.drop_incoming_request(r_id)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('{} is causing error on proxy.py write where response = {}'.format(r_id,e))
            # close the connection
            # self.drop_incoming_request(socket_id)
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

