
#   List structure of config files
#    seed_list: [
#        ( "ip_address": "x.x.x.x", "port": xxxx ),
#        ( "ip_address": "x.x.x.x", "port": xxxx ),
#        ( "ip_address": "x.x.x.x", "port": xxxx ) and so on...    
#       ]


import csv
import json


seed_list=[]
class  initialise_ip_addresses:

    def __init__(self):

        with open('config.csv', 'r') as file:
            reader = csv.reader(file)
            for ip, port in reader:
                seed_list.append((ip,port))
            self.seed_list = seed_list

    def get_seed_list(self):
        return self.seed_list
    


