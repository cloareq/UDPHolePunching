import socket
import hashlib
from getpass import getpass
import sys
from thread import start_new_thread

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
		self.tmp_sock = None
		self.ip_peer = None
		self.port_peer = None

	def identification(self):
		self.passwd = hashlib.sha1(str(self.passwd)).hexdigest()
		id_string = self.username + ':' + self.passwd
		self.sock.sendto(str(id_string), (self.broker_ip, self.broker_port))
		msg, broker = self.sock.recvfrom(1024)
		port, broker = self.sock.recvfrom(1024)
		self.broker_port = int(port)
		start_new_thread(self.wait_connection, ())

	def connection_request(self):
		self.ip_peer, b = self.tmp_sock.recvfrom(1024)
		print self.ip_peer
		self.port_peer, b = self.tmp_sock.recvfrom(1024)
		print self.port_peer
		self.tmp_sock.sendto("I'm your peer", (self.ip_peer, int(self.port_peer)))


	def wait_connection(self):
		self.tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.tmp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tmp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.tmp_sock.sendto("connection socket", (self.broker_ip, self.broker_port))

		while True:
			msg, ip = self.tmp_sock.recvfrom(1024)
			if msg == "connection request":
				self.connection_request()


	def connected_clients(self):
		self.sock.sendto("connected clients", (self.broker_ip, self.broker_port))
		client = ""
		while client != "done":
			client, b = self.sock.recvfrom(1024)
			if client != "done":
				self.clients.append(client)

	def connect_to_client(self, username):
		c = False
		for client in self.clients:
			if client == username:
				c = True
		if not c:
			return -1
		self.sock.sendto("request connection", (self.broker_ip, self.broker_port))
		self.sock.sendto(username, (self.broker_ip, self.broker_port))
		msg, b = self.sock.recvfrom(1024)
		if msg == "User not connected":
			print msg
			return -1
		self.ip_peer = msg
		self.port_peer, b = self.sock.recvfrom(1024)
		self.sock.sendto("peer", (self.ip_peer, int(self.port_peer)))
		msg, peer = self.sock.recvfrom(1024)
		print msg
		print peer


def main():
	if sys.argv[5] == "1":
		print 1
		c = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
		c.identification()
		c.connected_clients()
	else:
		print 2
		c = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
		c.identification()
		c.connected_clients()
		c.connect_to_client("bob")
	while True:
		pass

if __name__ == '__main__':
	main()
