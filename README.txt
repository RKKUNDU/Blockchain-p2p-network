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

References:
1) https://docs.python.org/3/library/socket.html
2) https://www.geeksforgeeks.org/socket-programming-python/
3) https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
4) https://www.geeksforgeeks.org/multithreading-python-set-1/