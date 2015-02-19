import socket
import hashlib
from getpass import getpass

class Client():
	""" TODO Docstring client """
	def __init__(self, broker_ip, broker_port, username, passwd):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		self.username = username
		self.passwd = passwd
		self.broker_ip = broker_ip
		self.broker_port = broker_port
		self.clients = []

	def identification(self):
		self.passwd = hashlib.sha1(str(self.passwd)).hexdigest()
		id_string = self.username + ':' + self.passwd
		self.sock.sendto(str(id_string), (self.broker_ip, self.broker_port))
		msg, broker = self.sock.recvfrom(1024)
		port, broker = self.sock.recvfrom(1024)
		self.broker_port = int(port)
	
	def connected_clients(self):
		self.sock.sendto("connected clients", (self.broker_ip, self.broker_port))
		l_clients, b = self.sock.recvfrom(1024)
		print l_clients

c = Client('127.0.0.1', 4242, "quentin", "123")
c.identification()
c.connected_clients()