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
lock_liveness_dict = threading.Lock()
message_list = dict()

class Peer:
    def __init__(self,conn,sv_ip,sv_port):
        self.conn = conn
        self.sv_ip = sv_ip
        self.sv_port = sv_port
        self.remote_ip, self.remote_port = conn.getpeername()
        self.local_ip, self.local_port = conn.getsockname()
        self.id = get_key_for_node(self.sv_ip,self.sv_port)
        self.terminate_flag = False

def bind_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), 0))  # PORT NO WILL BE ASSIGNED BY OS
    my_ip, my_port = s.getsockname()
    return s, my_ip, my_port


# ACCEPT CONNECTIONS FROM OTHER PEERS
def start_listening(s):
    s.listen()
    print(f"You can connect to me @ {my_ip}:{my_sv_port}")
    while True:
        try:
            conn, (ip, port) = s.accept()
            data=conn.recv(1024)
            if data.decode("utf-8") == "test":
                continue
            peer_sv_socket = data.decode('utf-8').split(":")
            peer_sv_ip = peer_sv_socket[0]
            peer_sv_port = peer_sv_socket[1]
            peer_key = get_key_for_node(peer_sv_ip, peer_sv_port)
            peer = Peer(conn, peer_sv_ip, peer_sv_port)
            inbound_peers[peer_key] = peer
            print(f"Got Connection From IP:{peer.remote_ip}: PORT: {peer.remote_port}")
            threading.Thread(target=handle_conn, args=[peer]).start()
        except KeyboardInterrupt:
            print('Server closing')
            s.close()

def get_key_for_node(ip, port):
    return f"{ip}:{port}"


# HANDLING CONNECTIONS FROM OTHER PEER
def handle_conn(peer):
    threading.Thread(target=check_liveness, args=[peer]).start()
    while not peer.terminate_flag:
        try:
            data = peer.conn.recv(LEN)
            if len(data) <= 0:
                continue
            msg = pickle.loads(data)
            print(f"{msg}, from {peer.remote_ip}:{peer.remote_port}")
            parts = msg.split(":")
            if parts[0] == "Liveness Request":
                handle_liveness_req(peer)
            elif parts[0] == "Liveness Reply":
                handle_liveness_resp(peer)
            else:
                hashval = hashlib.sha256(msg.encode())
                if hashval.hexdigest() in message_list.keys():
                    continue
                message_list[hashval.hexdigest()] = True
                handle_gossip_msg(peer, msg)
        except Exception as ex:
            print(f"handle_conn : {ex}")


def handle_liveness_req(peer):
    msg = f"Liveness Reply:{time.time()}:{peer.remote_ip}:{my_ip}"
    data = pickle.dumps(msg)
    try:
        peer.conn.sendall(data)
    except socket.error as err:
        if err.errno == errno.ECONNRESET or err.errno == errno.EPIPE :
            print(err)
            print("Closing Connection with {peer.remote_ip} {peer.remote_port}")
            key = peer.id
            if key in inbound_peers:
                inbound_peers.pop(key)

            if key in outbound_peers:
                outbound_peers.pop(key)
            # TODO: terminate thread, free obj
            peer.conn.close()


def handle_liveness_resp(peer):
    key = peer.id
    lock_liveness_dict.acquire()
    count = liveness_reply_cnt[key]
    count -= 1
    liveness_reply_cnt[key] = count
    lock_liveness_dict.release()


def handle_dead_node(peer):
    key = peer.id
    dead_node_ip = peer.remote_ip
    dead_node_port = peer.remote_port
    if key in inbound_peers:
        inbound_peers[key].terminate_flag = True
        inbound_peers.pop(key)
        # TODO: free peer in the handle_conn/liveness_chec

    if key in outbound_peers:
        inbound_peers[key].terminate_flag = True
        outbound_peers.pop(key)
        # TODO: free peer in the handle_conn
    
    for sock in connected_seeds:
        msg = f"Dead Node:{dead_node_ip}:{dead_node_port}:{time.time()}:{my_ip}:{my_sv_port}"
        data = pickle.dumps(msg)
        try:
            sock.sendall(data)
        except Exception as ex:
            print(f"handle_dead_node : {ex}")

def handle_gossip_msg(peer, msg):

    for inbound_peer in inbound_peers.values():
        ip = inbound_peer.remote_ip
        port = inbound_peer.remote_port
        if ip == peer.remote_ip and port == peer.remote_port:
            continue
        data = pickle.dumps(msg)
        try:
            inbound_peer.conn.sendall(data)
        except Exception as ex:
            print(f"handle_gossip_msg inbound: {ex}")
    for outbound_peer in outbound_peers.values():
        ip = outbound_peer.remote_ip
        port = outbound_peer.remote_port
        if ip == peer.remote_ip and port == peer.remote_port:
            continue
        data = pickle.dumps(msg)
        try:
            outbound_peer.conn.sendall(data)
        except Exception as ex:
            print(f"handle_gossip_msg outbound: {ex}")


# FOR CONNECTING TO SEEDS
def connect_seeds():
    # GETTING DETAILS OF THE SEEDS
    config = initialise_ip_addresses()
    seed_list = config.get_seed_list()
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
            # data=pickle.dumps((my_ip, my_sv_port))
            data=my_ip+":"+str(my_sv_port)
            s.connect((ip, int(port)))
            s.sendall(data.encode('utf-8'))
        except ConnectionRefusedError as err:
            print(err)
            peer_connection_refused(ip, port)
            continue
        key = get_key_for_node(ip, port)
        connected_to = Peer(s, ip, port)
        outbound_peers[key] = connected_to
        threading.Thread(target=handle_conn, args=[connected_to]).start()


# Generate msgs every 5 seconds 10 times (from inception) and send to all outbound_peers
def generate_msgs():
    count = 0
    while count < 10:
        count += 1
        msg = f"{time.time()}:{my_ip}:Count={count}"
        data = pickle.dumps(msg)
        hashval = hashlib.sha256(msg.encode())
        message_list[hashval.hexdigest()] = True
        for outbound_peer in outbound_peers.values():
            try:
                outbound_peer.conn.sendall(data)
            except Exception as ex:
                print(f"generate_msgs : {ex}")
        time.sleep(5)


# Function that will continually probe a connected node for liveness
def check_liveness(peer):
    while not peer.terminate_flag:
        probe_msg = f"Liveness Request:{time.time()}:{my_ip}"
        msg = pickle.dumps(probe_msg)
        key = peer.id
        lock_liveness_dict.acquire()
        if key in liveness_reply_cnt:
            count = liveness_reply_cnt[key]
            count += 1
            liveness_reply_cnt[key] = count
            if liveness_reply_cnt[key] == 4:
                handle_dead_node(peer)
                lock_liveness_dict.release()
                break
        else:
            liveness_reply_cnt[key] = 1
        lock_liveness_dict.release()

        try:
            peer.conn.sendall(msg)
        except Exception as ex:
            print(f"check_liveness : {ex}")
        time.sleep(13)


def peer_connection_refused(ip,port):
    for sock in connected_seeds:
        msg = f"Connection refused:{ip}:{port}"
        data = pickle.dumps(msg)
        try:
            sock.sendall(data)
        except Exception as ex:
            print(f"handle_dead_node : {ex}")


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
