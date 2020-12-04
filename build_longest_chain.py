from queue import Queue 
from block import Block
import hashlib
import random 
from peer_db_conn import peer_db_conn

class BuildLongestChain:
    def __init__(self, q, db, my_sv_port): 
        '''
        Input:
            q (queue): the pending queue
            db (database connection)
            my_sv_port (int): server port no of the peer
        '''
        blocks = list() 
        while(not q.empty()):
            block = Block.set_block(q.get())
            block_hash = hashlib.new("sha3_512", str(block).encode()).hexdigest()[-4:] # last 16 bits of the hash 
            block_prev_hash = block.get_prev_block_hash()
            block_timestamp = block.get_timestamp()

            # set parent to itself
            # this block will be inserted at `len(blocks)` index of `blocks` list
            # depth = -1 depicts depth is not calculated
            this_block = {'block': str(block), 'parentBlockIndex': len(blocks), 'depth': -1} 

            for i in range(len(blocks)):
                block_i_prev_hash = blocks[i]['block'][:Block.PREV_HASH_FIELD]
                # block_i_timestamp = block[i]['block'][-TIMESTAMP_FIELD:]
                
                block_i_hash = hashlib.new("sha3_512", blocks[i]['block'].encode()).hexdigest()[-4:]

                # block is parent of i'th block
                if block_hash == block_i_prev_hash: 
                    blocks[i]['parentBlockIndex'] = len(blocks)
                # i'th block is parent of the block
                elif block_i_hash == block_prev_hash: 
                    this_block['parentBlockIndex'] = i

            blocks.append(this_block)

        # self.print_longest_chain(blocks)
        self.insert_longest_chain_to_db(blocks, db, my_sv_port)
        # self.print_all_blocks(blocks)

    def insert_longest_chain_to_db(self, blocks, db, my_sv_port):
        if len(blocks) == 0:
            return

        longest = 0
        for i in range(len(blocks)):
            self.set_depth(blocks, i)
            if blocks[longest]['depth'] < blocks[i]['depth']:
                longest = i

        blocks_in_longest_chain = list()
        while blocks[longest]['parentBlockIndex'] != longest:
            blocks_in_longest_chain.append(blocks[longest]['block'])
            longest = blocks[longest]['parentBlockIndex']

        blocks_in_longest_chain.append(blocks[longest]['block'])

        # insert blocks to DB in order (older block first)
        for i in range(len(blocks_in_longest_chain)-1, -1, -1):
            # we will insert {len(blocks_in_longest_chain) - i} -th block at the i-th iteration
            # so the blocks height will be {len(blocks_in_longest_chain) - i}
            # and the blocks parent_id will be {len(blocks_in_longest_chain) - i - 1}
            # except for 1st block whose parent_id will be 1
            
            block_no = len(blocks_in_longest_chain) - i
            parent_id = len(blocks_in_longest_chain) - i - 1
            height = len(blocks_in_longest_chain) - i

            if block_no == 1:
                parent_id = 1

            print(f"Block {block_no}: {blocks_in_longest_chain[i]}")
            db.db_insert(blocks_in_longest_chain[i], parent_id, height, my_sv_port)

    def print_longest_chain(self, blocks):
        if len(blocks) == 0:
            return

        longest = 0
        for i in range(len(blocks)):
            self.set_depth(blocks, i)
            if blocks[longest]['depth'] < blocks[i]['depth']:
                longest = i

        print("Longest Chain:")  
        while blocks[longest]['parentBlockIndex'] != longest:
            print(blocks[longest])
            longest = blocks[longest]['parentBlockIndex']

        print(blocks[longest])

    def print_all_blocks(self, blocks):
        print("All blocks:")
        for x in blocks:
            print(x)

    def set_depth(self, blocks, i):
        # depth is already calculated, so just return the value
        if blocks[i]['depth'] != -1: 
            return blocks[i]['depth'] 

        # no parent (Maybe Genesis block)
        if blocks[i]['parentBlockIndex'] == i: 
            blocks[i]['depth'] = 1
            # print(f"Setting 1: {blocks[i]['block'][0]} depth={blocks[i]['depth']}")
            return 1

        blocks[i]['depth'] = 1 + self.set_depth(blocks, blocks[i]['parentBlockIndex'])
        # print(f"Setting 2: {blocks[i]['block'][0]} depth={blocks[i]['depth']}")
        return blocks[i]['depth']
 

if __name__ == '__main__':
    all_blocks = [
            "0000MR0908",
            "8c6fMR1908",
            "6cddMR0963",
            "20f5MR1963",
            "f7a1MR2908",
            "6cddMR3908",
            "eaeaMR4908",
            "ddb7MR5908",
            "8c6fMR0825",
            "da7eMR1825",
            "34afMR2825"
            ]

    random.shuffle(all_blocks)
    # print(all_blocks)
    q = Queue(maxsize = 0) # infinite queue 
    for block in all_blocks:
        q.put(block)

    obj = BuildLongestChain()
    obj.start_building(q)