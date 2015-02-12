import socket
import threading
import hashlib



class Broker():

    def __init__(self, broker_ip, broker_port):
        self.bip = broker_ip
        self. bport = broker_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((broker_ip, broker_port))

    def add_client(self, username, password):
        try:
            cid = username + ':' + hashlib.sha1(str(password)).hexdigest() + '\n'
            with open('clients.txt', 'a') as file:
                file.write(cid)
        except Exception, e:
            raise e
        
    def delete_client(self, username):
        f = open("clients.txt", "r")
        lines = f.readlines()
        f.close()
        f = open("clients.txt", "w")
        for line in lines:
            if line[:len(username)] != username:
                f.write(line)
        f.close()

