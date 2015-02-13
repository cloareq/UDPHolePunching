import socket
import threading
import hashlib
import sys


class Broker():

    def __init__(self, broker_ip, broker_port):
        self.bip = broker_ip
        self. bport = broker_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((broker_ip, broker_port))

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

b = Broker('127.0.0.1', 1212)
b.delete_client("titi")