#!/usr/bin/python          
# THIS IS A PEER NODE WHOSE IP, PORT NO IS NOT FIXED.
import time
import pickle
import socket
import threading
from initialise_ip_addresses import initialise_ip_addresses

peer_set = set()
inbound_peers = []
outbound_peers = []

def bind_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), 0)) # PORT NO WILL BE ASSIGNED BY OS
    myIP, myPort = s.getsockname()
    return s, myIP, myPort

# ACCEPT CONNECTIONS FROM OTHER PEERS
def start_listening(s):
    s.listen()
    print(f"You can connect to me {my_sv_ip} {my_sv_port} ")
    while True:
        conn, (ip, port) = s.accept()
        inbound_peers.append(conn)
        threading.Thread(target=handle_incoming_conn, args=[conn, ip, port]).start()


# HANDLING CONNECTIONS FROM OTHER PEER
def handle_incoming_conn(conn, ip, port):
    print(f"Got Connection From IP: {ip} PORT: {port}")
    threading.Thread(target=check_liveness, args=conn)
    while True:
        data = conn.recv(1024)
        # if data == gosip_message then handle_gossip()
        # else if data == liveness_reply then revive_conn()
        # else if data == liveness_req
        print(f"Received: {data} from {ip}:{port}")


# FOR CONNECTING TO SEEDS
def connect_seeds():
    # GETTING DETAILS OF THE SEEDS
    peer = initialise_ip_addresses()
    seed_list = peer.get_seed_list()
    cnt = 0

    for seed in seed_list:
        cnt += 1
        ip, port = seed
        print("Connecting to Seed-{} {} {}".format(cnt, ip, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))

        # SEND DETAILS OF LISTENING SOCKET
        msg = pickle.dumps((my_sv_ip, my_sv_port))
        s.sendall(msg)
        # NEED TO GENERALIZE FOR HIGHER BYTES OF DATA
        msg = s.recv(1024)
        peer_list = pickle.loads(msg)
        for peer in peer_list:
            peer_set.add(peer)


# FOR CONNECTING TO PEER NODES
def connect_peers():
    # THE ORDERING IS NOT GUARANTEED IN SET. SO SHUFFLING IS NOT REQUIRED
    peer_cnt = 0
    for peer in peer_set:
        # IF ALREADY 4 PEERS HAVE BEEN CONNECTED, NO NEED TO CONNECT MORE
        if peer_cnt == 4:
            break
        ip, port = peer
        # IF PEER IS THIS PROCESS ITSELF
        if ip == my_sv_ip and port == my_sv_port:
            continue
        peer_cnt += 1
        print(f"PEER-{peer_cnt} : IP {ip}, PORT {port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        outbound_peers.append(s)


# Generate msgs every 5 seconds 10 times (from inception) and send to all outbound_peers
def generate_msgs():
    count = 0
    while count < 10:
        count += 1
        for sock in outbound_peers:
            sock.send(b"Msg")
        time.sleep(5)


# Function that will continually probe a connected node for liveness
def check_liveness(conn):
    while True:
        probe_msg = f"Liveness Request:{time.time()}:{my_sv_ip}"
        msg = pickle.dumps(probe_msg)
        # count += 1
        conn.send(msg)
        time.sleep(13)


# 1. Setup listening (server)
s, my_sv_ip, my_sv_port = bind_socket()
t1 = threading.Thread(target=start_listening, args=[s], name='t1')
t1.start()

# 2. Parse config file, connect to seed nodes and collate peers list
connect_seeds()

# 3. Connect to 4 distinct peers
connect_peers()

# 4. Generate messages and send to outbound peers
generate_msgs()


t1.join()
