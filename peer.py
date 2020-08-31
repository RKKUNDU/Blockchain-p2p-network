#!/usr/bin/python          

import time
import socket               
import threading
from initialise_ip_addresses import initialise_ip_addresses

peer = initialise_ip_addresses()
seed_list = peer.get_seed_list()
ip, port = seed_list[0]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip,int(port)))
ip, port = socket.gethostbyname(socket.gethostname()), 27778
s.sendall(str((ip, port)).encode('utf-8'))
peer_list = s.recv(1024)
print(peer_list.decode('utf-8'))
s.close()