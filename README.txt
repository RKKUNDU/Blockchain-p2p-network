Project Contributors:
1) Rohit Kundu - 203050030
2) Sumit Thorat - 203050087
3) Pramod S Rao - 20305R007

Specific to project part-1:

Steps to start the network:
1) cd into the project folder.
2) Start a seed with the command "python3 seed.py <machine_ip_addr> <port_number>"
3) Repeat step 2 for the number of seeds you want in your network.
4) Update the configs/config.csv file in all the machines with the respective ip addresses used to start the seeds in step 2.
5) Start a peer with the command "python3 peer.py"
6) Repeat step 5 for the number of peers you want.

Output files (per peer/seed): 
1) seed_output_*
2) peer_output_*

Mentions on requirement understanding:
"after it connects to selected neighbors after registration"
1) Gossip messages by a peer are generated for the first 50 seconds (with a time interval of 5 seconds) after connecting to selected peers(if any) and sent to all neighbors. After 50 seconds message generation is stopped but gossiping(broadcasting messages received from other peer) continues.
2) Gossip count starts from 1 to 10
3) Timestamp used "yyyy-MM-dd-HH:mm:ss.microsecond"
4) Gossip message written to the peer output file is "<Received gossip from:> <local timestamp> <sender_IP> <message>"
5) Dead node message written to the seed output file "<Receiving Dead Node Message:> <Dead node message>"
5) Dead node message written to the peer output file "<Reporting Dead Node Message:> <Dead node message>"

References:
1) https://docs.python.org/3/library/socket.html
2) https://www.geeksforgeeks.org/socket-programming-python/
3) https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
4) https://www.geeksforgeeks.org/multithreading-python-set-1/
5) https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/


Specific to project part-2:

Steps to start the network:
1) cd into the project folder.
2) Start a seed with the command "python3 seed.py <machine_ip_addr> <port_number>"
3) Repeat step 2 for the number of seeds you want in your network.
4) Update the configs/config.csv file in all the machines with the respective ip addresses used to start the seeds in step 2.
5) Start a peer with the command "python3 peer.py NODE_HASH_POWER" where NODE_HASH_POWER is the numerical value of the percentage of nodes hashing power
6) Repeat step 5 for the number of peers you want.
7) Start an adversary with the command "python3 adversary.py NODE_HASH_POWER INTER_INVALID_BLOCK_GENERATION_TIME PERCENTAGE_OF_NODE_TO_FLOOD" 
8) Repeat step 7 for the number of adversaries you want.

Output:
A. Log files (per peer/adversary): 
    1) log/peer_log_*/peer_output_*  (eg. log/peer_log_iat2_iit0.5_fp10/peer_output_127.0.1.1:52917.txt)
    2) log/peer_log_*/adversary_output_*  (eg. log/peer_log_iat2_iit0.5_fp10/adversary_output_127.0.1.1:56041.txt)

    log/peer_log_iat2_iit0.5_fp10/peer_output_127.0.1.1:52917.txt contains the log for the peer whose server port = 52917, server IP = 127.0.1.1 when run with the following configuration
        1. inter-arrival time = 2s
        2. inter-invalid block generation time = 0.5s
        3. percentage of nodes to be flooded (by adversary) = 10%

B. Graphs:
    1) graphs/mining_power_utilization_vs_inter_arrival_time_*
    2) graphs/fraction_vs_inter_arrival_time_*

    graphs/mining_power_utilization_vs_inter_arrival_time_0.5s_10% contains the plot of "mining power utilization vs inter-arrival time" for the following configuration
        1. inter-invalid block generation time = 0.5s
        2. percentage of nodes to be flooded (by adversary) = 10%

    For each plot we run the network (with 1 seed, 10 peer node, 1 adversary node) with the inter-arrival time {2s, 4s, 6s, 8s}. We have several configuration for the plots. Those configurations are combination of flooding percentage {10%, 20%, 30%} and inter-invalid block generation time {0.5s, 1.0s}

C. Blockchain Tree:
    1) blockchain_tree/node* (eg. blockchain_tree/node39929.gv.pdf)

    blockchain_tree/node39929.gv.pdf contains the blockchain tree for the peer node whose server port is 39929

Determining the longest chain from the blocks stored in the database:
    We store the following things in the database
        1) id of the block (in the table of the database)
        2) block
        2) hash of the block
        3) parent_id of the block
        4) height of the block
    When we receive a block, we check in the database whether there exists a block (that means its the parent block) whose hash is stored in this blocks "previous hash" field. If we don't find, then we will discard the block (as the block's parent block is not present). Otherwise, we insert the received block in the database and we store id of the parent block as parent_id of the received block and we store (the height of the parent block + 1) as height of the received block.
    Before starting mining, we find the block (in database) which has the highest height that means the last block of the longest chain (if there are multiple, use any one). Then the peer mines on that block (or other way we can say that it mines on the longest chain).

References:
1) https://pypi.org/project/graphviz/