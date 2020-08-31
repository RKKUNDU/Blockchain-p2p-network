#!/usr/bin/python          

import time
import socket               
import threading

HOST = '192.168.0.182'
PORT = 27777

CONNECT_TO = '192.168.56.102'

# class node:
#     def __init__(self):
#         pass

def receive_message():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                print(data.decode('utf-8'))
                if not data:
                    break

def send_message():
    time.sleep(7)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((CONNECT_TO, PORT))
        while True:
            inp = input()
            if inp=='exit':
                return
            s.sendall(inp.encode('utf-8'))
        

t1 = threading.Thread(target=receive_message, name='t1') 
t2 = threading.Thread(target=send_message, name='t2')   
  
# starting threads 
t1.start() 
t2.start() 
  
# wait until all threads finish 
t1.join() 
t2.join() 