import sqlite3
import sys
import time

def add_data_mempool():
    conn = sqlite3.connect('mempool.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE mempool''')
