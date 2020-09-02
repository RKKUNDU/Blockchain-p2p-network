#!/usr/bin/python          
# THIS IS A PEER NODE WHOSE IP, PORT NO IS NOT FIXED.
import time
import pickle
import socket               
import threading
from initialise_ip_addresses import initialise_ip_addresses

def bind_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()),0)) # PORT NO WILL BE ASSIGNED BY OS
    myIP, myPort = s.getsockname()
    return (s, myIP, myPort) 

def start_listening(s):
    s.listen()
    print(f"You can connect to me {myIP} {myPort} ")
    handle_request(s)

# ACCEPTING CONNECTIONS FROM OTHER PEER
def handle_request(s):
    while True:
        conn, (ip,port) = s.accept()
        print(f"Got Connection From IP: {ip} PORT: {port}")
        conn.close()

# FOR CONNECTING TO SEEDS
def connect_seeds():
    # GETTING DETAILS OF THE SEEDS
    peer = initialise_ip_addresses()
    seed_list = peer.get_seed_list()
    cnt = 0
    peer_set = set()
    for seed in seed_list:
        cnt += 1
        ip, port = seed
        print("Connecting to Seed-{} {} {}".format(cnt,ip,port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,int(port)))

        # SEND DETAILS OF LISTENING SOCKET
        msg = pickle.dumps((myIP, myPort))
        s.sendall(msg)
        # NEED TO GENERALIZE FOR HIGHER BYTES OF DATA
        msg = s.recv(1024)
        PEER_LIST = pickle.loads(msg)
        for peer in PEER_LIST:
            peer_set.add(peer)
    connect_peers(peer_set)

# FOR CONNECTING TO PEER NODES
def connect_peers(peer_set):
    # THE ORDERING IS NOT GUARANTEED IN SET. SO SHUFFLING IS NOT REQUIRED
    peer_cnt = 0
    for peer in peer_set:
        # IF ALREADY 4 PEERS HAVE BEEN CONNECTED, NO NEED TO CONNECT MORE
        if peer_cnt == 4:
            break
        ip, port = peer
        # IF PEER IS THIS PROCESS ITSELF
        if  ip == myIP and port == myPort:
            continue
        peer_cnt += 1
        print(f"PEER-{peer_cnt} : IP {ip}, PORT {port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))

s, myIP, myPort = bind_socket()
t1 = threading.Thread(target=start_listening, args=[s], name='t1') 
t1.start()
connect_seeds()
t1.join()
