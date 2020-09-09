Project Contributors:
1) Rohit Kundu - 203050030
2) Sumit Thorat - 203050087
3) Pramod S Rao - 20305R007

Steps to start the network:
1) cd into the project folder.
2) Start a seed with the command "python3 seed.py <machine_ip_addr> <port_number>"
3) Repeat step 2 for the number of seeds you want in your network.
4) Update the config.csv file in all the machines with the respective ip addresses used to start the seeds in step 2.
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
