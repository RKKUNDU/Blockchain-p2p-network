#!/usr/bin/python          
# THIS IS A PEER NODE WHOSE IP, PORT NO IS NOT FIXED.
import time
import pickle
import socket
import threading
from initialise_ip_addresses import initialise_ip_addresses
import hashlib


LEN = 4096
rcvd_peer_set = set()
connected_seeds = []
inbound_peers = dict()
outbound_peers = dict()
liveness_reply_cnt = dict()
terminate_flag = dict()
lock_liveness_dict = threading.Lock()
message_list = dict()

def bind_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), 0))  # PORT NO WILL BE ASSIGNED BY OS
    my_ip, my_port = s.getsockname()
    return s, my_ip, my_port


# ACCEPT CONNECTIONS FROM OTHER PEERS
def start_listening(s):
    s.listen()
    print(f"You can connect to me @ {my_ip}:{my_sv_port} ")
    while True:
        try:
            conn, (ip, port) = s.accept()
            key = get_key_for_node(ip, port)
            inbound_peers[key] = conn
            terminate_flag[key] = False
            print(f"Got Connection From IP: {ip} PORT: {port}")
            threading.Thread(target=handle_conn, args=[conn, ip, port]).start()
        except KeyboardInterrupt:
            print('Server closing')
            s.close()

def get_key_for_node(ip, port):
    return f"{ip}:{port}"


# HANDLING CONNECTIONS FROM OTHER PEER
def handle_conn(conn, ip, port):
    threading.Thread(target=check_liveness, args=[conn, ip, port]).start()
    while not terminate_flag[get_key_for_node(ip,port)]:
        try:
            data = conn.recv(LEN)
            if len(data) <= 0:
                continue
            msg = pickle.loads(data)
            #print(f"Received: {msg}, from {ip}:{port}, on thread {threading.get_native_id()}")
            print(f"Received: {msg}, from {ip}:{port}, on thread ")
            parts = msg.split(":")
            if parts[0] == "Liveness Request":
                handle_liveness_req(conn, ip)
            elif parts[0] == "Liveness Reply":
                handle_liveness_resp(conn, ip, port)
            else:
                hashval = hashlib.sha256(msg.encode())
                if hashval.hexdigest() in message_list.keys():
                    continue
                message_list[hashval.hexdigest()] = True
                # print(f"Received: {msg}, from {ip}:{port}")
                handle_gossip_msg(conn, ip, port, msg)
        except Exception as ex:
            print(f"handle_conn : {ex}")


def handle_liveness_req(conn, ip):
    msg = f"Liveness Reply:{time.time()}:{ip}:{my_ip}"
    data = pickle.dumps(msg)
    try:
        conn.sendall(data)
    except socket.error as err:
        if err.errno == errno.ECONNRESET or err.errno == errno.EPIPE :
            print(err)
            print("Closing Connection with {conn.getpeername()[0]} {conn.getpeername()[1]}")
            key = get_key_for_node(conn.getpeername()[0], conn.getpeername[1])
            if key in inbound_peers:
                inbound_peers.pop(key)

            if key in outbound_peers:
                outbound_peers.pop(key)
            conn.close()


def handle_liveness_resp(conn, sender_ip, sender_port):
    key = f"{sender_ip}:{sender_port}"
    lock_liveness_dict.acquire()
    count = liveness_reply_cnt[key]
    count -= 1
    liveness_reply_cnt[key] = count
    lock_liveness_dict.release()


def handle_dead_node(dead_node_ip, dead_node_port):
    key = get_key_for_node(dead_node_ip, dead_node_port)
    if key in inbound_peers:
        inbound_peers.pop(key)
        terminate_flag[key] = True

    if key in outbound_peers:
        outbound_peers.pop(key)
        terminate_flag[key] = True

    for sock in connected_seeds:
        msg = f"Dead Node:{dead_node_ip}:{time.time()}:{my_ip}"
        data = pickle.dumps(msg)
        try:
            sock.sendall(data)
        except Exception as ex:
            print(f"handle_dead_node : {ex}")

def handle_gossip_msg(connection, from_ip, from_port, msg):
    for conn in inbound_peers.values():
        ip, port = conn.getpeername()
        if ip == from_ip and port == from_port:
            continue
        data = pickle.dumps(msg)
        try:
            conn.sendall(data)
        except Exception as ex:
            print(f"handle_gossip_msg inbound: {ex}")
    for conn in outbound_peers.values():
        ip, port = conn.getpeername()
        if ip == from_ip and port == from_port:
            continue
        data = pickle.dumps(msg)
        try:
            conn.sendall(data)
        except Exception as ex:
            print(f"handle_gossip_msg outbound: {ex}")


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
        connected_seeds.append(s)
        # SEND DETAILS OF LISTENING SOCKET
        msg = pickle.dumps((my_ip, my_sv_port))
        try:
            s.sendall(msg)
        except Exception as ex:
            print(f"connect_seeds: {ex}")
        # NEED TO GENERALIZE FOR HIGHER BYTES OF DATA
        try:
            msg = s.recv(LEN)
        except Exception as ex:
            print(ex)
        peer_list = pickle.loads(msg)
        for peer in peer_list:
            rcvd_peer_set.add(peer)


# FOR CONNECTING TO PEER NODES
def connect_peers():
    # THE ORDERING IS NOT GUARANTEED IN SET. SO SHUFFLING IS NOT REQUIRED
    peer_cnt = 0
    for peer in rcvd_peer_set:
        # IF ALREADY 4 PEERS HAVE BEEN CONNECTED, NO NEED TO CONNECT MORE
        if peer_cnt == 4:
            break
        ip, port = peer
        # IF PEER IS THIS PROCESS ITSELF
        if ip == my_ip and port == my_sv_port:
            continue
        peer_cnt += 1
        print(f"PEER-{peer_cnt} : IP {ip}, PORT {port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, int(port)))
        except ConnectionRefusedError as err:
            print(err)
            continue
        key = get_key_for_node(ip, port)
        outbound_peers[key] = s
        terminate_flag[key] = False
        threading.Thread(target=handle_conn, args=[s, ip, port]).start()


# Generate msgs every 5 seconds 10 times (from inception) and send to all outbound_peers
def generate_msgs():
    count = 0
    while count < 10:
        count += 1
        msg = f"{time.time()}:{my_ip}:Count={count}"
        data = pickle.dumps(msg)
        hashval = hashlib.sha256(msg.encode())
        message_list[hashval.hexdigest()] = True
        for sock in outbound_peers.values():
            try:
                sock.sendall(data)
            except Exception as ex:
                print(f"generate_msgs : {ex}")
        time.sleep(5)


# Function that will continually probe a connected node for liveness
def check_liveness(conn, other_ip, other_port):
    while True:
        probe_msg = f"Liveness Request:{time.time()}:{my_ip}"
        msg = pickle.dumps(probe_msg)
        key = f"{other_ip}:{other_port}"
        lock_liveness_dict.acquire()
        if key in liveness_reply_cnt:
            count = liveness_reply_cnt[key]
            count += 1
            liveness_reply_cnt[key] = count
            if liveness_reply_cnt[key] == 4:
                handle_dead_node(other_ip, other_port)
                lock_liveness_dict.release()
                break
        else:
            liveness_reply_cnt[key] = 1
        lock_liveness_dict.release()

        try:
            conn.sendall(msg)
        except Exception as ex:
            print(f"check_liveness : {ex}")
        time.sleep(13)


# 1. Setup listening (server)
s, my_ip, my_sv_port = bind_socket()
t1 = threading.Thread(target=start_listening, args=[s], name='t1')
t1.start()

# 2. Parse config file, connect to seed nodes and collate peers list
connect_seeds()

# 3. Connect to 4 distinct peers
connect_peers()

# 4. Generate messages and send to outbound peers
generate_msgs()


t1.join()
