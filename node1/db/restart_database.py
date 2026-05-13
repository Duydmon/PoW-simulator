import sqlite3
import os

if  os.path.exists('mempool.db'):
    os.remove('mempool.db')
conn1 = sqlite3.connect('mempool.db')
cursor1 = conn1.cursor()
cursor1.execute('''
               CREATE TABLE mempool(
                   id INTERGER PRIMARY KEY,
                   time INTEGER NOT NULL,
                   data TEXT,
                   signature TEXT,
                   publickey TEXT                     
)''')

if os.path.exists('blockchain.db'):
    os.remove('blockchain.db')
conn2 = sqlite3.connect('blockchain.db')
cursor2 = conn2.cursor()
cursor2.execute('''CREATE TABLE blockchain(
                   block_hash TEXT PRIMARY KEY,
                   previous_hash TEXT, 
                   height INTEGER, 
                   timestamp INTEGER, 
                   difficulty INTEGER, 
                   miner TEXT, 
                   data TEXT,
                   chain_work INTEGER,
                   nonce INTEGER, 
                   is_main_chain INTEGER
                   )''')

# conn3 = sqlite3.connect('blockchain.db')
# cursor3 = conn3.cursor()
# cursor3.execute('''CREATE TABLE block_data(
#                    block_hash TEXT PRIMARY KEY,(''')

