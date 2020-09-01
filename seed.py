#!/usr/bin/python          
# THIS IS A SEED NODE WHOSE INFORMATION WILL BE STORED IN CONFIG FILE. A SCRIPT WILL FETCH THE INFO AND GENERATE SEED NODES BASED ON THAT

import time
import socket               
import threading
import pickle
import sys

# if ip, port are not supplied
if len(sys.argv) != 3:
    exit(1)
        
myIP = sys.argv[1]
myPort = int(sys.argv[2])

peer_list=set()

def register_request(socket_pair):
    peer_list.add(socket_pair)

#Just a placeholder for now, will implement later
def dead_node_message():
    pass

def new_client(conn):
    # receive listening socket details of the peer
    data = conn.recv(1024)
    ip, port = pickle.loads(data)
    register_request((ip,port))
    # send peer list with the peer
    msg = pickle.dumps(peer_list)
    conn.sendall(msg)
    while True:
        data=conn.recv(1024)
        conn.sendall(data)

def start_seed_node():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connect to me IP: {myIP} PORT {myPort}")
        s.bind((myIP, myPort))
        s.listen()
        while True:
            conn, (ip,port) = s.accept()
            pthread=threading.Thread(target=new_client,args=[conn])
            pthread.start()

t1 = threading.Thread(target=start_seed_node, name='t1') 

t1.start()
t1.join()
