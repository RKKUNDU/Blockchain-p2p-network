#!/usr/bin/python          

import time
import socket               
import threading

peer_list=set()

def register_request(socket_pair):
    peer_list.add(socket_pair)

#Just a placeholder for now, will implement later
def dead_node_message():
    pass

def new_client(conn):
    data=conn.recv(1024)
    print(data.decode('utf-8'))
    register_request(eval(data.decode('utf-8')))
    conn.sendall(str(peer_list).encode('utf-8'))
    while True:
        data=conn.recv(1024)
        conn.sendall(data)

def start_seed_node():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((socket.gethostname(), 27778))
        s.listen()
        while True:
            conn, (ip,port) = s.accept()
            pthread=threading.Thread(target=new_client,args=[conn])
            pthread.start()

t1 = threading.Thread(target=start_seed_node, name='t1') 

t1.start()
t1.join()