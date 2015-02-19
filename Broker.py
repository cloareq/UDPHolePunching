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
                print "found"
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

    def talk_to_client(self, ip_client, socket_client):
        while True:
            msg, ip = socket_client.recvfrom(1024)
            if msg == "connected clients":
                socket_client.sendto(str(self.clients_list), ip)



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
            start_new_thread(self.talk_to_client, (ipclient, s))
   

b = Broker('127.0.0.1', 4242)
b.add_client("quentin", "123")
b.listen_clients()