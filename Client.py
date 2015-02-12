import socket
import hashlib
from getpass import getpass

class Client():
	""" TODO Docstring client """
	def __init__(self, broker_ip, broker_port, username, passwd):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		self.username = ""
		self.passwd = ""
		self.broker_ip = broker_ip
		self.broker_port = broker_port
		self.identification(username, passwd)

	def identification(self, username, passwd):
		id_string = username + '=' + passwd
		self.sock.sendto(id_string, ("127.0.0.1", 4242))
		msg, broker = self.sock.recvfrom(1024)
		