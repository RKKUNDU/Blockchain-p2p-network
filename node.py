#!/usr/bin/python          

import time
import socket               
import threading

def receive_message():
    
    host = socket.gethostname() 
    port = 12345                
    s = socket.socket()         
    s.bind((host, port))        
    s.listen(5) 
    c, addr = s.accept()
    print('Got connection from', addr)  
    while True:
        print(c.recv(1024))   


def send_message():
    host = socket.gethostname() 
    port = 12345
    s = socket.socket()
    s.connect((host, port))
    while True:
        time.sleep(5)
        s.send("Sending this every 5 seconds as a sender")

t1 = threading.Thread(target=receive_message, name='t1') 
t2 = threading.Thread(target=send_message, name='t2')   
  
# starting threads 
t1.start() 
t2.start() 
  
# wait until all threads finish 
t1.join() 
t2.join() 

        
    





