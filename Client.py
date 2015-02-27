#!/usr/bin/python
# -*- coding:Utf-8 -*-

import socket
import hashlib
from getpass import getpass
import sys
from thread import start_new_thread
from subprocess import call

SIZE_MSG = 1024

"""  
	A client is able to communicate with the outside and connect
	to the Broker. It can request a connection with another 
	conneted client and make a direct connection using 
	the UDP Hole Punching method.
	It can be behind firewall/nat.

 """

class Client():
	def __init__(self, broker_ip, broker_port, username, passwd):
		""" 
		
		Initialize all parameters 
		Socket are initiate with SO_REUSEADDR option to be able
		to use UDP Hole Punching to send DataGrams to a peer and 
		set up an UDP Tunnel

		"""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.username = username
		self.passwd = passwd
		self.broker_info = (broker_ip, broker_port)
		self.clients = []
		self.tmp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.tmp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		self.peer_info = None
		self.peer = None

	def identification(self):
		""" 

		identification to the Broker by sending username and password


		"""
		
		# Crypt password
		self.passwd = hashlib.sha1(str(self.passwd)).hexdigest()
		id_string = self.username + ':' + self.passwd
		# Send username and password to the Broker
		self.sock.sendto(str(id_string), self.broker_info)
		msg, broker = self.sock.recvfrom(SIZE_MSG)
		if msg.find("Bad Username or Password") != -1:
			return -1
		# Client is correctly identify
		port, broker = self.sock.recvfrom(SIZE_MSG)
		self.broker_port = int(port)
		# start a new thread
		start_new_thread(self.wait_connection, ())

        def connection_request(self):
        	# get info from the peer who wants to connect
            ip_peer, b = self.tmp_sock.recvfrom(SIZE_MSG)
            port_peer, b = self.tmp_sock.recvfrom(SIZE_MSG)
            self.peer_info = (ip_peer, int(port_peer))
            # punch a hole in the NAT
            self.tmp_sock.sendto("I'm your peer", self.peer_info)
            # receive a response
            msg, ip = self.tmp_sock.recvfrom(SIZE_MSG)
            self.peer_info = ip
            #get own public ip                                                           
            myip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0],\
            	s.close()) for s in [socket.socket(socket.AF_INET,\
            	socket.SOCK_DGRAM)]][0][1]

            exec_line = "./udptunnelpatch/udptunnel -v -v -v -s " + \
            str(myip) + " " + str(self.tmp_sock.getsockname()[1])
            # Udp Tunnel serv mode
            call([exec_line], shell=True,)


	def wait_connection(self):
		# send to the broker the socket able to receive connection from peer
		self.tmp_sock.sendto("connection socket", self.broker_info)

		while True:
			msg, ip = self.tmp_sock.recvfrom(SIZE_MSG)
			if msg == "connection request":
				# someone ask for a connection
				self.connection_request()


	def get_connected_clients(self):
		""" get clients username connected to the Broker """

		self.sock.sendto("connected clients", self.broker_info)
		client = ""
		while client != "done":
			client, b = self.sock.recvfrom(SIZE_MSG)
			if client != "done":
				self.clients.append(client)

	def connect_to_client(self, username, service_port):
		""" 

		Ask for a client to make a direct connection and initiate
		an UDP Tunnel on the service_port
		

		"""

		# check if client's username is in the connected client's list
		c = False
		for client in self.clients:
			if client == username:
				c = True
		if not c:
			return -1
		# send the client's username to the broker
		self.sock.sendto("request connection", self.broker_info)
		self.sock.sendto(username, self.broker_info)

		# check if the client is connected to the broker
		msg, b = self.sock.recvfrom(SIZE_MSG)
		if msg == "User not connected":
			return -1
		
		# get public ip and port of the client
		self.ip_peer = msg
		self.port_peer, b = self.sock.recvfrom(SIZE_MSG)
		# make a hole in the NAT
		self.sock.sendto("peer", (self.ip_peer, int(self.port_peer)))
		# receive a direct response from the client
		msg, peer = self.sock.recvfrom(SIZE_MSG)
		self.peer = peer
        self.sock.sendto("peer", self.peer)
        # get own public ip
		myip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close())	\
		for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
		
		# initiate the UDP tunnel on the service port as a client

		exec_line = "./udptunnelpatch/udptunnel -c " + str(myip) + \
		" 4444 " + str(self.peer[0]) + " " + str(self.peer[1])\
		+ " 127.0.0.1 " + service_port + " " +\
		str(self.sock.getsockname()[1])
        
        # exec UDPTunnel        
		call([exec_line], shell=True,)


def main():
	if sys.argv[5] == "1":
		c = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
		c.identification()
		c.get_connected_clients()
	else:
		c = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
		c.identification()
		c.get_connected_clients()
		c.connect_to_client("bob")
	while True:
		pass

if __name__ == '__main__':
	main()
