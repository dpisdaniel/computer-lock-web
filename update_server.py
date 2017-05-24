import threading
import ssl
import SocketServer
RECEIVE_SIZE = 1024
SERVER_IP_AND_PORT = '127.0.0.1'


class UpdateServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass  # No need to override anything, all gucci


class UpdateServerRequestHandler(SocketServer.StreamRequestHandler):
    """
    Handles one connection to a client
    """
    def handle(self):
        print "connection from %s" % self.client_address[0]


if __name__ == "__main__":
    pass
