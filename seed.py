#!/usr/bin/python          

import time
import socket               
import threading

peer_list=[]

def register_request(socket_pair):
    peer_list.append(socket_pair)

#Just a placeholder for now, will implement later
def dead_node_message():
    pass

def start_seed_node():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((socket.gethostbyname(socket.gethostname()), 27778))
        s.listen()
        while True:
            conn, (ip,port) = s.accept()
            register_request((ip,port))
            conn.sendall(str(peer_list).encode('utf-8'))

t1 = threading.Thread(target=start_seed_node, name='t1') 

t1.start()
t1.join()