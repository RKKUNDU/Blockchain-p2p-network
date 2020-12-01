from queue import Queue 
import hashlib
import random 
PREV_HASH_FIELD = 4
TIMESTAMP_FIELD = 10
class BuildLongestChain:
    def start_building(self, q): # q is the pending queue
        blocks = list() 
        while(not q.empty()):
            block = q.get()
            block_hash = hashlib.new("sha3_512", block.encode()).hexdigest()[-4:] # last 16 bits of the hash 
            block_prev_hash = block[:PREV_HASH_FIELD] # first 4 byte is prevHash hex digest
            # block_timestamp = block[-TIMESTAMP_FIELD:] # last 10 byte is unix timestamp

            # set parent to itself
            # this block will be inserted at `len(blocks)` index of `blocks` list
            # depth = -1 depicts depth is not calculated
            this_block = {'block': block, 'parentBlockIndex': len(blocks), 'depth': -1} 

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


# class Build:
# def start_building(q):
#     blocks = list()
#     while(not q.empty()):
#         block = q.get()
#         this_block = {'block': block, 'parent': block[0] , 'height': -1} # set parent to itself

#         for i in range(len(blocks)):
#             if blocks[i]['block'][1] == block[0]: # block is parent of i'th block 
#                 blocks[i]['parent'] = len(blocks)
#             elif block[1] == blocks[i]['block'][0]: # i'th block is parent of block
#                 this_block['parent'] = i

#         blocks.append(this_block)

#     longest = 0
#     for i in range(len(blocks)):
#         set_height(blocks, i)
#         if blocks[longest]['height'] < blocks[i]['height']:
#             longest = i

#     print("Longest Chain:")  
#     while blocks[longest]['parent'] != blocks[longest]['block'][0]:
#         print(blocks[longest])
#         longest = blocks[longest]['parent']

#     print(blocks[longest])
#     # for x in blocks:
#     #     print(x)
    


# def set_height(blocks, i):
#     if blocks[i]['height'] != -1:
#         return blocks[i]['height'] 

#     if blocks[i]['parent'] == blocks[i]['block'][0]: # Genesis block
#         blocks[i]['height'] = 1
#         # print(f"Setting 1: {blocks[i]['block'][0]} Height={blocks[i]['height']}")
#         return 1

#     blocks[i]['height'] = 1 + set_height(blocks, blocks[i]['parent'])
#     # print(f"Setting 2: {blocks[i]['block'][0]} Height={blocks[i]['height']}")
#     return blocks[i]['height']
    

# all_blocks = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 3), (8, 7), (9, 1), (10, 9), (11, 10)]
# q = Queue(maxsize = 0) # infinite queue 
# for block in all_blocks:
#     q.put(block)

# # obj = Build()
# start_building(q)