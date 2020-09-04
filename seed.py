#!/usr/bin/python


# THIS IS A SEED NODE WHOSE INFORMATION WILL BE STORED IN CONFIG FILE. A SCRIPT WILL FETCH THE INFO AND GENERATE SEED
# NODES BASED ON THAT

import time
import socket
import threading
import pickle
import sys

# IF IP, PORT ARE NOT SUPPLIED
if len(sys.argv) != 3:
    exit(1)

myIP = sys.argv[1]
myPort = int(sys.argv[2])

peer_list = set()


# ADD THE PEER TO THE PEER_LIST
def register_request(socket_pair):
    # TODO: SYNCHRONIZE THIS PART IF MULTITHREADING IS USED
    peer_list.add(socket_pair)


# REMOVE THE DEAD NODE FROM PEER_LIST
def dead_node_message(msg):
    print(msg)
    msg_parts = msg.split(":")
    dead_node_ip = msg_parts[1]
    if msg_parts[0] == "Dead Node":
        for peer in peer_list:
            if peer[0] == dead_node_ip:
                # TODO: SYNCHRONIZE THIS PART IF MULTITHREADING IS USED
                peer_list.remove(peer)


def new_client(conn):
    # RECEIVE LISTENING SOCKET DETAILS OF THE PEER
    # TODO: ENSURE IT READS COMPLETE DATA
    data = conn.recv(1024)
    ip, port = pickle.loads(data)
    register_request((ip, port))
    # SEND PEER LIST WITH THE PEER
    msg = pickle.dumps(peer_list)
    conn.sendall(msg)
    # while True:
    # WAITING FOR DEAD MESSAGES
    # TODO: ENSURE IT READS COMPLETE DATA
    # data=conn.recv(1024)
    # dead_node_message(data.decode('utf-8'))


def start_seed_node():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connect to me IP: {myIP} PORT {myPort}")
        s.bind((myIP, myPort))
        s.listen()
        while True:
            conn, (ip, port) = s.accept()
            pthread = threading.Thread(target=new_client, args=[conn])
            pthread.start()


t1 = threading.Thread(target=start_seed_node, name='t1')

t1.start()
t1.join()
