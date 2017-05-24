import threading
import ssl
import SocketServer
RECEIVE_SIZE = 1024
SERVER_IP_AND_PORT = '127.0.0.1'


class UpdateServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, request_handler_class, certfile, keyfile, ssl_version=ssl.PROTOCOL_TLSv1, bind_and_activate=True):
        SocketServer.TCPServer.__init__(self, server_address, request_handler_class, bind_and_activate)
        self.certfile = certfile
        self.keyfile = keyfile
        self.ssl_version = ssl_version

    def get_request(self):
        new_socket, from_address = self.socket.accept()
        connstream = ssl.wrap_socket(new_socket, server_side=True, keyfile=self.keyfile, certfile=self.certfile, ssl_version=self.ssl_version)
        return connstream, from_address


class UpdateServerRequestHandler(SocketServer.StreamRequestHandler):
    """
    Handles one connection to a client
    """
    def handle(self):
        data = buffer(self.connection.recv(RECEIVE_SIZE))
        length = int((data[0] + data[1]).encode('hex'), 16)
        print length
        for byte in data:
            print byte
        self.wfile.write(data)


if __name__ == "__main__":
    UpdateServer(('127.0.0.1', 5151), UpdateServerRequestHandler, "cert.pem", "key.pem").serve_forever()
