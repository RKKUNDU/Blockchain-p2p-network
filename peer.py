#!/usr/bin/python          
# THIS IS A PEER NODE WHOSE IP, PORT NO IS NOT FIXED.
import time
from datetime import datetime
import pickle
import socket
import threading
from initialise_ip_addresses import initialise_ip_addresses
import hashlib
import errno
import math
import random
import os


#Inititalising the sets and variables used by this peer node.
HEADER_SIZE = 10
LEN = 4096
rcvd_peer_set = set()
connected_seeds = []
inbound_peers = dict()
outbound_peers = dict()
message_list = dict()

#This is a peer object which contains all the information required to communicate with the other peers.
class Peer:
    def __init__(self,conn,sv_ip,sv_port):
        self.conn = conn
        self.sv_ip = sv_ip
        self.sv_port = sv_port
        self.remote_ip, self.remote_port = conn.getpeername()
        self.local_ip, self.local_port = conn.getsockname()
        self.id = get_key_for_node(self.sv_ip,self.sv_port)
        self.terminate_flag = False
        self.pending_liveness_reply_cnt = 0
        self.conn_lock = threading.Lock()
        self.pending_liveness_reply_cnt_lock = threading.Lock()

#Utility function to create a listening socket for the peer.
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
            data = conn.recv(LEN)
            if len(data) == 0:
                break
            msglen = int(data[:HEADER_SIZE].decode('utf-8'))

            msg = data[HEADER_SIZE:]
            while len(msg)  < msglen:
                data = conn.recv(msglen-len(msg))
                msg += data

            msg = pickle.loads(msg)
            # print(f'{msg}')
            
            # Used by seed node for liveness checking
            if msg == "test":
                continue
            peer_sv_socket = msg.split(":")
            peer_sv_ip = peer_sv_socket[0]
            peer_sv_port = peer_sv_socket[1]
            peer_key = get_key_for_node(peer_sv_ip, peer_sv_port)
            peer = Peer(conn, peer_sv_ip, peer_sv_port)
            inbound_peers[peer_key] = peer
            print(f"Got Connection From IP:{peer.remote_ip}: PORT: {peer.remote_port} whose server: {peer.sv_ip} {peer.sv_port}")
            threading.Thread(target=handle_conn, args=[peer]).start()
        except KeyboardInterrupt:
            print('Server closing')
            s.close()

#Utility function for generating a key to store/access dict values
def get_key_for_node(ip, port):
    return f"{ip}:{port}"


# HANDLING CONNECTIONS FROM OTHER PEER
def handle_conn(peer):
    threading.Thread(target=check_liveness, args=[peer]).start()
    while not peer.terminate_flag:
        try:
            data = peer.conn.recv(LEN)
            if len(data) == 0:
                break
           
            msglen = int(data[:HEADER_SIZE].decode('utf-8'))
            msg = data[HEADER_SIZE:]
            
            while len(msg) > msglen:
                part = msg[:msglen]
                message = pickle.loads(part)
                #Received message is split and depending on the message further processing happens.
                parts = message.split(":")
                if parts[0] == "Liveness Request":
                    handle_liveness_req(peer)
                elif parts[0] == "Liveness Reply":
                    handle_liveness_resp(peer)
                else:
                    #Received gossip message is hashed into a Message list
                    hashval = hashlib.sha256(message.encode())
                    if hashval.hexdigest() in message_list.keys():
                        pass
                    else:
                        message_list[hashval.hexdigest()] = True
                        handle_gossip_msg(peer, message)

                data = msg[msglen:]
                msglen = int(data[:HEADER_SIZE].decode('utf-8'))
                msg = data[HEADER_SIZE:]

            while len(msg) < msglen:
                data = peer.conn.recv(msglen-len(msg))
                msg += data

            msg = pickle.loads(msg)
            # print(f"{msg}, from {peer.remote_ip}:{peer.remote_port}")
            parts = msg.split(":")
            if parts[0] == "Liveness Request":
                handle_liveness_req(peer)
            elif parts[0] == "Liveness Reply":
                handle_liveness_resp(peer)
            else:
                #Received gossip message is hashed into a Message list
                hashval = hashlib.sha256(msg.encode())
                if hashval.hexdigest() in message_list.keys():
                    continue
                message_list[hashval.hexdigest()] = True
                handle_gossip_msg(peer, msg)
        except Exception as ex:
            pass
            # print(f"handle_conn : {ex}")

#Once we receive a liveness request from any of the adjacent peers, this function handles that and sends a directed liveness reply.
def handle_liveness_req(peer):
    msg = f"Liveness Reply:{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}:{peer.remote_ip}:{my_ip}"
    # print(f'\tSending: {msg}')
    data = pickle.dumps(msg)
    data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
    try:
        peer.conn_lock.acquire()
        peer.conn.sendall(data)
    except socket.error as err:
        pass
        # if err.errno == errno.ECONNRESET or err.errno == errno.EPIPE :
        #     print(err)
    except Exception as ex:
        pass
    finally:
        peer.conn_lock.release()

#When we get a liveness reply/response from the peer whom we requested a livness request, we handle that
def handle_liveness_resp(peer):
    peer.pending_liveness_reply_cnt_lock.acquire()
    peer.pending_liveness_reply_cnt -= 1
    peer.pending_liveness_reply_cnt_lock.release()

#This function is called when a node is non-responsive upon 3 liveness requests.
def handle_dead_node(peer):
    key = peer.id
    dead_node_ip = peer.sv_ip
    dead_node_port = peer.sv_port
    if key in inbound_peers:
        inbound_peers[key].terminate_flag = True
        inbound_peers.pop(key)

    if key in outbound_peers:
        outbound_peers[key].terminate_flag = True
        outbound_peers.pop(key)
    
    msg = f"Dead Node:{dead_node_ip}:{dead_node_port}:{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}:{my_ip}"
    data = pickle.dumps(msg)
    msg1 = "Reporting Dead Node Message: "+ msg
    write_to_file(msg1)
    print(msg)
    data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
    #We send which node is dead to all the connected seeds.
    for sock in connected_seeds:
        try:
            sock.sendall(data)
        except Exception as ex:
            pass
            # print(f"handle_dead_node : {ex}")

#When the message received in handle_conn function is a gossip message, we forward the message to all adjacent peers if required.
def handle_gossip_msg(peer, msg):
    msg1="Received gossip from:"+str(peer.sv_ip)+":"+str(peer.sv_port)+" "+str(msg)
    write_to_file(msg1)
    print(msg)
    # print(f"Received gossip from:{peer.sv_ip}:{peer.sv_port} {msg}")
    #Forwarding messages to all inbound peers
    for inbound_peer in inbound_peers.values():
        ip = inbound_peer.remote_ip
        port = inbound_peer.remote_port
        if ip == peer.remote_ip and port == peer.remote_port:
            continue
        data = pickle.dumps(msg)
        data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
        try:
            inbound_peer.conn_lock.acquire()
            inbound_peer.conn.sendall(data)
        except Exception as ex:
            pass
            # print(f"handle_gossip_msg inbound: {ex}")
        finally:
            inbound_peer.conn_lock.release()
    #Forwarding message to all outbound peers.
    for outbound_peer in outbound_peers.values():
        ip = outbound_peer.remote_ip
        port = outbound_peer.remote_port
        if ip == peer.remote_ip and port == peer.remote_port:
            continue
        data = pickle.dumps(msg)
        data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
        try:
            outbound_peer.conn_lock.acquire()
            outbound_peer.conn.sendall(data)
        except Exception as ex:
            pass
            # print(f"handle_gossip_msg outbound: {ex}")
        finally:
            outbound_peer.conn_lock.release()




# FOR CONNECTING TO SEEDS
def connect_seeds():
    # GETTING DETAILS OF THE SEEDS
    config = initialise_ip_addresses()
    seed_list = config.get_seed_list()
    cnt = 0
    n = len(seed_list)
    seeds_to_connect = math.floor(n/2)+1
    # Due to the below line, peer connects to any of the floor(n/2)+1 seeds
    seed_list = random.sample(seed_list, seeds_to_connect)
    for seed in seed_list:
        cnt += 1
        ip, port = seed
        print("Connecting to Seed-{} {} {}".format(cnt, ip, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        connected_seeds.append(s)
        # SEND DETAILS OF LISTENING SOCKET
        data = pickle.dumps((my_ip, my_sv_port))
        data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
        try:
            s.sendall(data)
        except Exception as ex:
            pass
            # print(f"connect_seeds: {ex}")
        try:
            data = s.recv(LEN)
            if len(data) == 0:
                break
            msglen = int(data[:HEADER_SIZE].decode('utf-8'))
            msg = data[HEADER_SIZE:]
            while len(msg)  < msglen:
                data = peer.conn.recv(msglen-len(msg))
                msg += data

            peer_list = pickle.loads(msg)
            # write_to_file(repr(peer_list))
            # print(repr(peer_list))

        except Exception as ex:
            pass
            # print(ex)
        
        # print(f'{peer_list}')
        for peer in peer_list:
            rcvd_peer_set.add(peer)

# Function to write the logs to an output file.
def write_to_file(line):
    file.write(line + "\n")
    file.flush()
    os.fsync(file.fileno())


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
        print(f"PEER-{peer_cnt} : IP {ip}, PORT {port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            data = my_ip+":"+str(my_sv_port)
            s.connect((ip, int(port)))
            peer_cnt += 1
            data = pickle.dumps(data)
            data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
            s.sendall(data)
        except ConnectionRefusedError as err:
            # print(err)
            peer_connection_refused(ip, port)
            continue
        key = get_key_for_node(ip, port)
        connected_to = Peer(s, ip, port)
        outbound_peers[key] = connected_to
        threading.Thread(target=handle_conn, args=[connected_to]).start()


# Generate msgs every 5 seconds 10 times (from inception) and send to all inbound and outbound_peers
def generate_msgs():
    count = 0
    while count < 10:
        count += 1
        msg = f"{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}:{my_ip}:Count={count}"
        data = pickle.dumps(msg)
        data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
        hashval = hashlib.sha256(msg.encode())
        message_list[hashval.hexdigest()] = True
        for outbound_peer in outbound_peers.values():
            try:
                outbound_peer.conn_lock.acquire()
                outbound_peer.conn.sendall(data)
            except Exception as ex:
                pass
                # print(f"generate_msgs : {ex}")
            finally:
                outbound_peer.conn_lock.release()

        for inbound_peer in inbound_peers.values():
            try:
                inbound_peer.conn_lock.acquire()
                inbound_peer.conn.sendall(data)
            except Exception as ex:
                pass
                # print(f"generate_msgs : {ex}")
            finally:
                inbound_peer.conn_lock.release()
        time.sleep(5)


# Function that will continually probe a connected node for liveness
def check_liveness(peer):
    while not peer.terminate_flag:
        probe_msg = f"Liveness Request:{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}:{my_ip}"
        # print(f'\tSending Req: {probe_msg}')
        data = pickle.dumps(probe_msg)
        peer.pending_liveness_reply_cnt_lock.acquire()
        peer.pending_liveness_reply_cnt += 1
        if peer.pending_liveness_reply_cnt == 4:
            peer.pending_liveness_reply_cnt_lock.release()
            handle_dead_node(peer)
            break
        else:
            peer.pending_liveness_reply_cnt_lock.release()
        try:
            data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
            peer.conn_lock.acquire()
            peer.conn.sendall(data)
        except Exception as ex:
            # print(f"check_liveness : {ex}")
            pass
        finally:
            peer.conn_lock.release()
        time.sleep(13)

# This function sends a message to a seed saying it was not able to connect to this peer 
# and asks the seed to check if this node is still alive.
def peer_connection_refused(ip,port):
    for sock in connected_seeds:
        msg = f"Connection refused:{ip}:{port}"
        data = pickle.dumps(msg)
        data = bytes(f'{len(data):<{HEADER_SIZE}}','utf-8') + data
        try:
            sock.sendall(data)
        except Exception as ex:
            pass
            # print(f"handle_dead_node : {ex}")


# 1. Setup listening (server)
s, my_ip, my_sv_port = bind_socket()
t1 = threading.Thread(target=start_listening, args=[s], name='t1')
t1.start()

# 2. Open file
file = open(f"peer_output_{get_key_for_node(my_ip, my_sv_port)}.txt", "a+")

# 3. Parse config file, connect to seed nodes and collate peers list
connect_seeds()

# 4. Connect to 4 distinct peers
connect_peers()

# 5. Generate messages and send to outbound peers
generate_msgs()

t1.join()
file.close()
