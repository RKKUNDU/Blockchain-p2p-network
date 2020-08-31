
#   List structure of config files
#    sock_obj: [
#        ( "ip_address": "x.x.x.x", "port": xxxx ),
#        ( "ip_address": "x.x.x.x", "port": xxxx ),
#        ( "ip_address": "x.x.x.x", "port": xxxx ) and so on...    
#       ]


import csv
import json

class  initialise_ip_addresses:
    
    def __init__(self):
        sock_obj = []
        with open('config.csv', 'r') as file:
            reader = csv.reader(file)
            for ip, port in reader:
                sock_obj.append((ip,port))
            self.sock_obj = sock_obj

