import socket

class Broker():

    def __init__(self, broker_ip, broker_port):
        self.bip = broker_ip
        self. bport = broker_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


    def listen_client_connection(self):

# import SocketServer

# list_client = []
# client_file = open("test", "r+")

# class Broker(SocketServer.BaseRequestHandler):

#     def handle(self):
#         data = self.request[0].strip()
#         self.socket = self.request[1]
#         list_client.append(self.client_address)
#         self.content_file = client_file.read()
#         self.client_identification()


#     def client_identification(self):

#         data = self.request[0].strip()
#         socket = self.request[1]
#         if content_file.find(data) != -1:
#             self.socket.sendto("connection ok", self.client_address)
#         else:
#             self.socket.sendto("Unkown", self.client_address)
#         for user in content_file:
#             if data == user:
#                 self.socket.sendto("connection ok", self.client_address)
#         