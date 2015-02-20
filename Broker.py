from thread import start_new_thread
import hashlib
import sys
import socket

SIZE_MSG = 1024

class Broker():

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((ip, port))
        self.clients_list = []
        self.socklist = []
        self.client_connection_list = []

    def add_client(self, username, password):
        self.delete_client(username)
        cid = username + ':' + hashlib.sha1(str(password)).hexdigest() + '\n'
        try:
            with open('clients.txt', 'a') as file:
                file.write(cid)
        except:
            f = open('clients.txt', 'w+')
            f.close()
            self.add_client(username, password)
        
    def delete_client(self, username):
        try:
            f = open("clients.txt", "r+")
        except:
            f = open("clients.txt", "w+")
        lines = f.readlines()
        f.close()
        f = open("clients.txt", "w")
        for line in lines:
            if line[:len(username)] != username:
                f.write(line)
        f.close()

    def check_registered(self, userinfo):
        f = open("clients.txt", "r")
        flist = f.readlines()
        f.close()
        found = False
        for line in flist:
            if str(userinfo) in line:
                found = True
                return True
        if not found:
            return False

    def init_socket(self, username, ipclient):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        self.socklist.append((username, s, port, ipclient))
        return s, port

    def catch_connected_clients(self, ip_client, socket_client):
        for client in self.clients_list:
            socket_client.sendto(str(client), ip_client)
        socket_client.sendto("done", ip_client)

    def connection_to_peer(self, ip_client, socket_client, username):
        msg, ip = socket_client.recvfrom(1024)
        peer_username = msg
        ip_peer = None
        for client in self.client_connection_list:
            if client[0] == peer_username:
                ip_peer = client[1]
                socket_client.sendto(ip_peer[0], ip_client)
                socket_client.sendto(str(ip_peer[1]), ip_client)

                client[2].sendto("connection request", ip_peer)
                client[2].sendto(ip_client[0], ip_peer)
                client[2].sendto(str(ip_client[1]), ip_peer)

        if ip_peer == None:
            socket_client.sendto("User not connnected", ip_client)



    def talk_to_client(self, ip_client, socket_client, username):
        while True:
            msg, ip = socket_client.recvfrom(1024)
            if msg == "connected clients":
                self.catch_connected_clients(ip_client, socket_client)
            if msg == "connection socket" :
                self.client_connection_list.append((username, ip, socket_client))
            if msg.find("request connection") != -1:
                self.connection_to_peer(ip_client, socket_client, username)

    def listen_clients(self):
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
            start_new_thread(self.talk_to_client, (ipclient, s, username))
   

b = Broker('127.0.0.1', 4242)
b.add_client("quentin", "123")
b.add_client("bob", "123")
b.add_client("toto", "123")
b.listen_clients()