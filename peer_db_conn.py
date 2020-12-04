import mysql.connector
import hashlib 

class peer_db_conn:

    def __init__(self, my_ip, my_sv_port):
        database_not_exists=1
        self.mydb = mysql.connector.connect(host="localhost",user="root",password="")
        mycursor = self.mydb.cursor()
        mycursor.execute("show databases")
        for x in mycursor:
            if x[0] == 'blockchain':
                print('Database already exists...')
                database_not_exists=0
        
        if database_not_exists:
            mycursor.execute("CREATE DATABASE blockchain")

        self.mydb = mysql.connector.connect(host="localhost",user="root", password="",database="blockchain")
        self.create_table(my_ip, my_sv_port)
        print('Connected to \'blockchain\' database...')
    
    def create_table(self, my_ip, my_sv_port):
        table_not_exists=1
        mycursor = self.mydb.cursor()
        mycursor.execute("show tables")
        for x in mycursor:
            if x[0] == f'blocks{my_sv_port}':
                print('Table already exists...')
                # mycursor.execute(f"DELETE FROM blocks{my_sv_port}")
                table_not_exists=0   
                 
        if table_not_exists:
            print(f'Created blocks{my_sv_port} table')
            mycursor.execute(f"CREATE TABLE blocks{my_sv_port} (id INT AUTO_INCREMENT PRIMARY KEY, block VARCHAR(255), hash VARCHAR(4), parent_id INT, height INT)")

    def db_insert(self, block, parent_id, height, my_sv_port):
        mycursor = self.mydb.cursor()
        sql = f"INSERT INTO blocks{my_sv_port} (block, hash, parent_id, height) VALUES (%s, %s, %s, %s)"
        val = str(block)
        hash = get_hash(val)
        mycursor.execute(sql, (val, hash, parent_id, height))
        self.mydb.commit()
    
    def db_fetch_latest_block(self, my_sv_port):
        '''
            Return block, id, height of the latest block
        '''
        mycursor = self.mydb.cursor()
        sql = f"select block, id, height from blocks{my_sv_port} where height=(select max(height) from blocks{my_sv_port})"
        mycursor.execute(sql)
        block = mycursor.fetchall()
        return str(block[0][0]), int(block[0][1]), int(block[0][2])

    def db_fetch_blocks_till(self, block, my_sv_port):
        all_blocks = list()
        block = str(block)
        mycursor = self.mydb.cursor()
        sql = f"select id, parent_id from blocks{my_sv_port} where block=(%s)"
        mycursor.execute(sql, (block,))
        print(block)
        id, parent_id = mycursor.fetchall()[0] # id, parent_id of the latest block "block" in DB
       
        # fetch all the blocks from DB
        sql = f"select id, block, parent_id from blocks{my_sv_port}"
        mycursor.execute(sql)
        blocks = mycursor.fetchall()

        # create the chain that ends with 'block'
        while id != parent_id:
            all_blocks.append(blocks[id - 1][1]) # index is 0-based but id is 1-based
            id = parent_id
            parent_id = blocks[id - 1][2] # index is 0-based but id is 1-based

        all_blocks.append(blocks[id - 1][1]) # index is 0-based but id is 1-based
        all_blocks.reverse()
        return all_blocks

    def is_block_present(self, hash, my_sv_port):
        '''
            Return is_present, id, height of the block (if present) whose hash is 'hash'
        '''
        mycursor = self.mydb.cursor()
        sql = f"select id, height from blocks{my_sv_port} where hash=(%s)"
        mycursor.execute(sql, (hash,))
        parent_block = mycursor.fetchall()

        if len(parent_block) > 0:
            return True, parent_block[0][0], parent_block[0][1]
        
        return False, None, None


def get_hash(block):
    return hashlib.new("sha3_512", str(block).encode()).hexdigest()[-4:]
