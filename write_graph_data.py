from peer_db_conn import peer_db_conn
from build_longest_chain import BuildLongestChain
import queue

def get_fraction(db, port):
    # db = peer_db_conn('127.0.0.1', port)
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

    try:
        ret = (total, adv_count / total)
    except:
        ret = 0.0, 0.0

    return ret


def get_util(db, my_sv_port):
    blocks = db.fetch_all_blocks(my_sv_port)
    blocks = [block[4] for block in blocks]
    total_blocks = len(blocks)
    try:
        longest_chain_length = max(blocks)
    except:
        longest_chain_length = 0

    return longest_chain_length, total_blocks


def write_graph_data_for_one_peer(db, my_sv_port):
    with open('configs/inter_arrival_time.txt','r') as iat_file:
        iat =  iat_file.readline()

        longest_chain_length, total_blocks = get_util(db, my_sv_port)
        string = str(iat) +':'+ str(total_blocks) + ':' + str(longest_chain_length) + '\n'
        with open('graph_data/graph_mining_util_data.txt', 'a') as file:
            file.write(string)
        
        f = get_fraction(db, my_sv_port)
        string = str(iat) +':'+ str(f[0]) + ':' + str(f[1]) + '\n'
        with open('graph_data/graph_fraction_data.txt', 'a') as file:
            file.write(string)


def write_graph_data():
    db = peer_db_conn('127.0.0.1')
    tables = db.get_all_ports()
    for table in tables:
        write_graph_data_for_one_peer(db, int(table[0][6:]))


write_graph_data()

# drop the database
db = peer_db_conn('127.0.0.1')
db.drop_database()
