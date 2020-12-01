from queue import Queue 
from block import Block
import hashlib
import random 

class BuildLongestChain:
    def start_building(self, q): # q is the pending queue
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
                block_i_prev_hash = blocks[i]['block'][:PREV_HASH_FIELD]
                # block_i_timestamp = block[i]['block'][-TIMESTAMP_FIELD:]
                
                block_i_hash = hashlib.new("sha3_512", blocks[i]['block'].encode()).hexdigest()[-4:]

                # block is parent of i'th block
                if block_hash == block_i_prev_hash: 
                    blocks[i]['parentBlockIndex'] = len(blocks)
                # i'th block is parent of the block
                elif block_i_hash == block_prev_hash: 
                    this_block['parentBlockIndex'] = i

            blocks.append(this_block)

        self.print_longest_chain(blocks)
        self.print_all_blocks(blocks)

    def print_longest_chain(self, blocks):
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