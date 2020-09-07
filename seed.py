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
peer_map=dict()

lock = threading.Lock()

# ADD THE PEER TO THE PEER_LIST
def register_request(socket_pair):
    # TODO: SYNCHRONIZE THIS PART IF MULTITHREADING IS USED
    lock.acquire()
    peer_list.add(socket_pair)
    lock.release()

def check_if_node_alive(ip, port):
    i=0
    key=ip+":"+str(port)
    conn = peer_map[key]
    while i<3:
        try:
            conn.sendall(b"test")
        except Exception as ex:
            print(f"Testing if node alive: count ={i+1}")
            time.sleep(2)
            i+=1
    if i==3:
        lock.acquire()
        peer_list.remove((ip,int(port)))
        peer_map.pop(key)
        lock.release()
    print("Peer list:",peer_list)

# REMOVE THE DEAD NODE FROM PEER_LIST
def dead_node_message(msg):
    
    print(msg)
    msg_parts = msg.split(":")
    dead_node_ip = msg_parts[1]
    dead_node_port = msg_parts[2]
    key=dead_node_ip+":"+str(dead_node_port)
    print(f"Received dead message from:{msg_parts[4]}:{msg_parts[5]}")
    if msg_parts[0] == "Dead Node":
        for peer in peer_list:
            if peer[0] == dead_node_ip and peer[1]==int(dead_node_port):
                # TODO: SYNCHRONIZE THIS PART IF MULTITHREADING IS USED
                lock.acquire()
                peer_list.remove(peer)
                peer_map.pop(key)
                lock.release()
                break
    print("Peer list:",peer_list)


def new_client(conn):
    # RECEIVE LISTENING SOCKET DETAILS OF THE PEER
    # TODO: ENSURE IT READS COMPLETE DATA
    data = conn.recv(1024)
    ip, port = pickle.loads(data)
    register_request((ip, port))
    key=ip+":"+str(port)
    peer_map[key]=conn
    print(f"Peer list: {peer_list}")
    # SEND PEER LIST WITH THE PEER
    msg = pickle.dumps(peer_list)
    conn.sendall(msg)
    while True:
        # WAITING FOR DEAD MESSAGES
        # TODO: ENSURE IT READS COMPLETE DATA
        data=conn.recv(1024)
        if len(data) <= 0:
            continue
        msg = pickle.loads(data)
        msg_parts=msg.split(":")
        if msg_parts[0]=="Connection refused":
            check_if_node_alive(msg_parts[1], msg_parts[2])
        elif msg_parts[0]=="Dead Node":
            dead_node_message(msg)
        


def start_seed_node():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connect to me IP: {myIP} PORT {myPort}")
        s.bind((myIP, myPort))
        s.listen()
        while True:
            conn, (ip, port) = s.accept()
            print(f"{myIP}:{myPort}:) Got a new connection from {ip}:{port}")
            
            pthread = threading.Thread(target=new_client, args=[conn])
            pthread.start()


t1 = threading.Thread(target=start_seed_node, name='t1')

t1.start()
t1.join()
