#!/usr/bin/python
# -*- coding:Utf-8 -*-

from thread import start_new_thread
import hashlib
import sys
import socket

SIZE_MSG = 1024
"""

Broker is a server accessible from the outside. It initiates the connection
with several clients to make a direct connection between them
It uses UDP sockets to send and receive DataGram.
A new thread is open each time a new client sends a message


"""
class Broker():

    def __init__(self, ip, port):
        """ 

        init socket parameters with SO_REUSEADDR to be
        able to reuse the same address with several clients 
        
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.clients_list = []
        self.socklist = []
        self.client_connection_list = []

    def add_client(self, username, password):
        """ 

        Add a client to the database. Client are defined by a username and
        a password

        """
        # delete client if already in the database
        self.delete_client(username)
        # crypt password
        cid = username + ':' + hashlib.sha1(str(password)).hexdigest() + '\n'
        try:
            with open('client_database', 'a') as file:
                # write new client infos in the database
                file.write(cid)
        except:
            f = open('client_database', 'w+')
            f.close()
            self.add_client(username, password)
        
    def delete_client(self, username):
        """ Delete a client from the database """
        try:
            f = open("client_database", "r+")
        except:
            f = open("client_database", "w+")
        lines = f.readlines()
        f.close()
        f = open("client_database", "w")
        for line in lines:
            # try to find "username" in the database file
            if line[:len(username)] != username:
                f.write(line)
        f.close()



    def check_registered(self, userinfo):
        """ 

        Verify that a user is corresponding 
        to someone in the database 

        """
        f = open("client_database", "r")
        flist = f.readlines()
        f.close()
        found = False
        for line in flist:
            if str(userinfo) in line:
                # user found
                found = True
                return True
        if not found:
            return False

    def init_socket(self, username, ipclient):
        """

        initiate a new socket to be able to talk 
        to a specific client

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #bind a free random port
        s.bind(('', 0))
        port = s.getsockname()[1]
        self.socklist.append((username, s, port, ipclient))
        return s, port

    def send_connected_clients(self, ip_client, socket_client):
        """ send all the connected clients """

        for client in self.clients_list:
            socket_client.sendto(str(client), ip_client)
        socket_client.sendto("done", ip_client)

    def client_to_peer(self, ip_client, socket_client, username):
        """

        initiate the connection between two clients by
        sending public ip and port to each of them

        """
        msg, ip = socket_client.recvfrom(1024)
        peer_username = msg
        ip_peer = None
        for client in self.client_connection_list:
            if client[0] == peer_username:
                #send ip and port to the asking client
                ip_peer = client[1]
                socket_client.sendto(ip_peer[0], ip_client)
                socket_client.sendto(str(ip_peer[1]), ip_client)
                #send a connection request to the peer
                client[2].sendto("connection request", ip_peer)
                client[2].sendto(ip_client[0], ip_peer)
                client[2].sendto(str(ip_client[1]), ip_peer)

        if ip_peer == None:
            socket_client.sendto("User not connected", ip_client)



    def client_thread(self, ip_client, socket_client, username):
        """ Listen for a request from a specific client """

        while True:
            msg, ip = socket_client.recvfrom(1024)
            if msg == "connected clients":
                self.send_connected_clients(ip_client, socket_client)
            if msg == "connection socket" :
                self.client_connection_list.append((username, ip, socket_client))
            if msg.find("request connection") != -1:
                self.client_to_peer(ip_client, socket_client, username)

    def start(self):
        """ 
        
        Start the Broker and make it able to wait for clients
        to connect
        
        """
        while True:
            userinfo, ipclient = self.sock.recvfrom(1024)
            if not self.check_registered(userinfo):
                self.sock.sendto("Bad Username or Password", ipclient)
                continue
            self.sock.sendto("connected", ipclient)
            username = userinfo.split(':')[0]
            s, port = self.init_socket(username, ipclient)
            self.clients_list.append(username)
            self.sock.sendto(str(port), ipclient)
            start_new_thread(self.client_thread, (ipclient, s, username))
   

b = Broker('', 4242)
b.start()