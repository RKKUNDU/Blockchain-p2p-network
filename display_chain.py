from graphviz import Digraph # graph creating tool
from peer_db_conn import peer_db_conn # DB connection to fetch the blocks
import sys # Parses the command line argument

# Fetch all the blocks from database
db = peer_db_conn('127.0.0.1', sys.argv[1])
blocks = db.fetch_all_blocks(sys.argv[1])

# Uncomment the below line to test if graph creates fork.
blocks.append((8, 'abcdefgdifhijklm', '1234', 5, 6))

# Initialise the graph to be visualised.
dot = Digraph(comment='Blockchain')


# Generate the nodes and edges for the blockchain graph.
for index in range(len(blocks)):
    # If it is first node, just add the node.
    if index==0:
        dot.node(str(index), blocks[index][2])
        continue

    # Below code is execute for second node onwards.
    dot.node(str(index), blocks[index][2])

    # Inner for loop searches for the parent.
    for inner_index in range(len(blocks)):
        if blocks[index][3] == blocks[inner_index][0]:
            dot.edge(str(inner_index), str(index))
            continue


#Render the output and save it into the test-output folder.
dot.render(f'test-output/node{sys.argv[1]}.gv', view=True)  
