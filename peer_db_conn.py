import mysql.connector

class peer_db_conn:

    def __init__(self):
        database_not_exists=1
        self.mydb = mysql.connector.connect(host="localhost",user="root",password="12345678")
        mycursor = self.mydb.cursor()
        mycursor.execute("show databases")
        for x in mycursor:
            if x[0] == 'blockchain':
                print('Database already exists...')
                database_not_exists=0
        if database_not_exists:
            mycursor.execute("CREATE DATABASE blockchain")
        self.mydb = mysql.connector.connect(host="localhost",user="root",password="12345678",database="blockchain")
        print('Connected to \'blockchain\' database...')
    
    def create_table(self):
        table_not_exists=1
        mycursor = self.mydb.cursor()
        mycursor.execute("show tables")
        for x in mycursor:
            if x[0] == 'blocks':
                print('Table already exists...')
                table_not_exists=0    
        if table_not_exists:
            print('Created blocks table')
            mycursor.execute("CREATE TABLE blocks (id INT AUTO_INCREMENT PRIMARY KEY, block VARCHAR(255))")


    def db_insert(self, block):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO blocks(block) VALUES (%s)"
        val = str(block)
        mycursor.execute(sql, (val,))
        self.mydb.commit()
    
    def db_fetch_latest_block(self):
        mycursor = self.mydb.cursor()
        sql = "select block from blocks where id=(select max(id) from blocks)"
        mycursor.execute(sql)
        block = mycursor.fetchall()
        return str(block[0][0])

    def db_fetch_blocks_till(self, block):
        all_blocks = list()
        block = str(block)
        mycursor = self.mydb.cursor()
        sql = "select id from blocks where block=(%s)"
        mycursor.execute(sql, (block,))
        id = mycursor.fetchall()[0][0]
        sql = "select block from blocks where id>=1 and id<(%s)"
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