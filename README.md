# Peer to peer network
## This is a multithreaded p2p network, which has some basic functionalities: 
* ### Seed nodes which have list of peers in the network
* ### Peers which check the liveness of it's adjacent peers
* ### Peer produces gossip messages to the network upon arrival
* ### Sending a dead node message to seed node if a peer is non-responsive
* ### Seed nodes maintain consistency of peer lists

### Project contrbutors
Name | Roll Number
--- | --- | 
Rohit Kundu | 203050030
Sumit Thorat | 203050087
Pramod S Rao | 20305R007

<br>

### <b>Steps to start the network:</b>
1) <b>cd</b> into the project folder.
2) Start a seed with the command <b>"python3 seed.py <machine_ip_addr> <port_number>" </b>
3) Repeat step 2 for the number of seeds you want in your network.
4) Update the config.csv file in all the machines with the respective ip addresses used to start the seeds in step 2.
5) Start a peer with the command <b>"python3 peer.py"</b>
6) Repeat step 5 for the number of peers you want.

### Output files: 
* seed_output_*
* peer_output_*

Seperate output files are generated for every peer and every seed.

### References
1) https://docs.python.org/3/library/socket.html
2) https://www.geeksforgeeks.org/socket-programming-python/
3) https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
4) https://www.geeksforgeeks.org/multithreading-python-set-1/