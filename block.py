class Block:

    def __init__(self, prev_hash, merkel_root, timestamp):
        self.prev_hash = prev_hash # 4 characters
        self.merkel_root = merkel_root # 2 characters
        self.timestamp = timestamp # 10 characters

    def __str__(self):
        return f'{self.prev_hash}{self.merkel_root}{self.timestamp}'

    def get_prev_block_hash(self):
        return self.prev_hash

    def get_merket_root(self):
        return self.merkel_root

    def get_timestamp(self):
        return self.timestamp
