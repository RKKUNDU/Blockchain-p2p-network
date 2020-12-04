import mysql.connector

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
            mycursor.execute(f"CREATE TABLE blocks{my_sv_port} (id INT AUTO_INCREMENT PRIMARY KEY, block VARCHAR(255))")


    def db_insert(self, block, my_sv_port):
        mycursor = self.mydb.cursor()
        sql = f"INSERT INTO blocks{my_sv_port} (block) VALUES (%s)"
        val = str(block)
        mycursor.execute(sql, (val,))
        self.mydb.commit()
    
    def db_fetch_latest_block(self, my_sv_port):
        mycursor = self.mydb.cursor()
        sql = f"select block from blocks{my_sv_port} where id=(select max(id) from blocks{my_sv_port})"
        mycursor.execute(sql)
        block = mycursor.fetchall()
        return str(block[0][0])

    def db_fetch_blocks_till(self, block, my_sv_port):
        all_blocks = list()
        block = str(block)
        mycursor = self.mydb.cursor()
        sql = f"select id from blocks{my_sv_port} where block=(%s)"
        mycursor.execute(sql, (block,))
        id = mycursor.fetchall()[0][0]
        sql = f"select block from blocks{my_sv_port} where id>=1 and id<(%s)"
        mycursor.execute(sql,(id,))
        blocks = mycursor.fetchall()
        for block in blocks:
            all_blocks.append(block[0])
        return all_blocks


# obj = peer_db_conn()
# obj.create_table()
# obj.db_insert('abcdef')
# print(obj.db_fetch_latest_block())
# obj.db_fetch_blocks_till('abcdef')
