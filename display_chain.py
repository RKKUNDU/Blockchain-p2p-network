from graphviz import Digraph # graph creating tool
from peer_db_conn import peer_db_conn # DB connection to fetch the blocks
import sys # Parses the command line argument
import queue
from build_longest_chain import BuildLongestChain


def display_chain_for_node(port):

    # Fetch all the blocks from database
    db = peer_db_conn('127.0.0.1', port)
    blocks = db.fetch_all_blocks(port)

    # Uncomment the below line to test if graph creates fork.
    blocks.append((8, 'abcdefgdifhijklm', '1234', 5, 6))

    # Initialise the graph to be visualised.
    dot = Digraph(comment='Blockchain')


    # Generate the nodes and edges for the blockchain graph.
    for index in range(len(blocks)):
        # If it is first node, just add the node.
        if index == 0:
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



# Return the fraction of blocks that are adversary's in the longest chain at node with port no. 'port'
def get_fraction(port):
    db = peer_db_conn('127.0.0.1', port)
    block_headers = db.fetch_block_headers(port)

    q = queue.Queue()

    for block in block_headers:
        q.put(block[0])

    build_helper = BuildLongestChain()

    longest_chain = build_helper.get_longest_chain(q)

    total = float(len(longest_chain))
    adv_count = 0.0

    for block_tuple in longest_chain:
        if block_tuple['block'][4] == 'A':
            adv_count += 1

    return (total, adv_count / total)


# Return the fraction from the longest chain
def get_fraction_from_longest():
    db = peer_db_conn('127.0.0.1')
    tables = db.get_all_ports()

    ans = 0.0
    curr_len = 0
    for table in tables:
        t = get_fraction(int(table[0][6:]))
        if curr_len < t[0]:
            curr_len = t[0]
            ans = t[1]
    
    return ans
    
    
print(get_fraction_from_longest())
