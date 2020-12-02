class Block:
    PREV_HASH_FIELD = 4
    MERKEL_ROOT_FIELD = 2
    TIMESTAMP_FIELD = 10
    def __init__(self, prev_hash, merkel_root, timestamp):
        self.prev_hash = prev_hash # 4 characters
        self.merkel_root = merkel_root # 2 characters
        self.timestamp = timestamp # 10 characters

    @classmethod
    def set_block(self, block_string):
        prev_hash = block_string[:self.PREV_HASH_FIELD] # first 4 byte is prevHash hex digest
        merkel_root = block_string[self.PREV_HASH_FIELD:self.PREV_HASH_FIELD + self.MERKEL_ROOT_FIELD]
        timestamp = block_string[-self.TIMESTAMP_FIELD:]
        return Block(prev_hash, merkel_root, timestamp)

    def __str__(self):
        return f'{self.prev_hash}{self.merkel_root}{self.timestamp}'

    def get_prev_block_hash(self):
        return self.prev_hash

    def get_merkel_root(self):
        return self.merkel_root

    def get_timestamp(self):
        return self.timestamp
