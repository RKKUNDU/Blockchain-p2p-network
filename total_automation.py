import os
import time
from datetime import datetime

num_of_peers = 2
num_of_adversaries = 1
seed_ip = '127.0.0.1'
seed_port = '12345'
node_hash_power = 6.7
adversary_hash_power = 33
experiment_time = 10
flood_percentage = 10 


iit_list = [0.5]

for iit in iit_list:
    iat_list = [2, 4, 6, 8]    
    
    for iat in iat_list:
        with open("./configs/inter_arrival_time.txt", 'w') as iat_file:
            iat_file.write(str(iat))

        print("Running for iat:", iat)

        cmd = "python3 seed.py " + seed_ip + " "+seed_port+" &"
        os.system(cmd)

        i = 0
        while i < num_of_peers:
            cmd = "python3 peer.py " + str(node_hash_power) + " &"
            os.system(cmd)
            time.sleep(2)
            i+=1
        
        i = 0
        while i < num_of_adversaries:
            cmd = "python3 adversary.py " + str(adversary_hash_power) + " " + str(iit) + " " + str(flood_percentage) + " &"
            os.system(cmd)
            time.sleep(2)
            i+=1
        
        time.sleep(experiment_time)

        os.system("killall -15 python3")
        time.sleep(5)
        os.system("killall -9 python3")
        time.sleep(10)

        output_folder = "test_output_iat" + str(iat) + "_iit" + str(iit) + "_fp" + str(flood_percentage)
        os.system("mkdir -p " + output_folder)
        os.system("mv peer_output/* " + output_folder)


    os.system("python3 graph_generation.py " + str(iit) + " " + str(flood_percentage))
    os.system("make clean")


