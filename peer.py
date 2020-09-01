#!/usr/bin/python          
# THIS IS A PEER NODE WHOSE IP, PORT NO IS NOT FIXED.
import time
import pickle
import socket               
import threading
from initialise_ip_addresses import initialise_ip_addresses

# FOR LISTENING
socket_listening = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_listening.bind((socket.gethostbyname(socket.gethostname()),0)) # PORT NO WILL BE ASSIGNED BY OS
print("You can connect to me @ ",socket_listening.getsockname())
socket_listening.listen()
myIP, myPort = socket_listening.getsockname()

# GETTING DETAILS OF THE SEEDS
peer = initialise_ip_addresses()
seed_list = peer.get_seed_list()
cnt = 0

# FOR CONNECTING TO SEEDS
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

# the ordering is not guaranteed in set. so shuffling is not required
peer_cnt = 0
for peer in peer_set:
    # if already 4 peers have been connected, no need to connect more
    if peer_cnt == 4:
        break
    ip, port = peer
    # if peer is this process itself
    if  ip == myIP and port == myPort:
        continue
    peer_cnt += 1
    print(f"PEER-{peer_cnt} : IP {ip}, PORT {port}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(port)))

# ACCEPTING CONNECTION FROM OTHER PEERS
while True:
    c, addr = socket_listening.accept()
    print(f"Got Connection From IP: {addr[0]} PORT: {addr[1]}")
    c.close()
