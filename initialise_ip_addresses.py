
#   List structure of config files
#    seed_list: [
#        ( "ip_address": "x.x.x.x", "port": xxxx ),
#        ( "ip_address": "x.x.x.x", "port": xxxx ),
#        ( "ip_address": "x.x.x.x", "port": xxxx ) and so on...    
#       ]


import csv
import json


seed_list=[]
node_hash_power=0
global_lambda=0
inter_arrival_time=0

class initialise_ip_addresses:

    def __init__(self):

        with open('config.csv', 'r') as file:
            reader = csv.reader(file)
            for ip, port in reader:
                seed_list.append((ip,port))
            self.seed_list = seed_list
        
        with open('peer_config.csv', 'r') as peer_file:
            reader=csv.reader(peer_file)
            for global_lambda,node_hash_power in reader:
                self.node_hash_power = node_hash_power
                self.global_lambda = global_lambda
        
        with open('inter_arrival_time.txt','r') as iat_file:
            self.inter_arrival_time =  iat_file.readline()


    def get_seed_list(self):
        return self.seed_list
    
    def get_global_lambda(self):
        return self.global_lambda
    
    def get_node_hash_power(self):
        return self.node_hash_power

    def get_inter_arrival_time(self):
        return self.inter_arrival_time    

# config = initialise_ip_addresses()
# inter_arrival_time = config.get_inter_arrival_time()
# print(inter_arrival_time)
