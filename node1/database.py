#chứa các hàm và code truy xuât, nhập liệu dữ liệu vào cơ sở dữ liệu
import sqlite3
import sys
import time
import json

# khi đưa data vào, sẽ ký số và

def add_data_mempool(data,node_id):
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mempool(
            time,
            data,
            node_id,
            in_chain
        )
        VALUES (?, ?, ?, ?)
    """, (
        int(time.time()),
        data,
        node_id,
        0
    ))
    conn.commit()
    conn.close()
    print("Data added to mempool!")

def get_data_from_mempool() -> list:
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
     SELECT time, data, node_id 
     FROM mempool WHERE in_chain = 0 LIMIT 5""")
    row = cursor.fetchall()
    conn.close()
    return row


def query_newest_block():

    conn = sqlite3.connect('./db/blockchain.db')

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            block_hash,
            previous_hash,
            height,
            timestamp,
            difficulty,
            miner,
            data,
            chain_work,
            nonce

        FROM blockchain
        WHERE is_main_chain = 1
        ORDER BY chain_work DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    block = {

        "block_hash": row[0],

        "previous_hash": row[1],

        "height": row[2],

        "timestamp": row[3],

        "difficulty": row[4],

        "miner": row[5],

        "data": row[6],

        "chain_work": row[7],

        "nonce": row[8]
    }

    return block

def get_tip_block_data() -> dict:
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""

        SELECT
            block_hash,
            height,
            chain_work

        FROM blockchain
        WHERE is_main_chain = 1
        ORDER BY chain_work DESC
        LIMIT 1
    """)
    data = cursor.fetchone()
    conn.close()
    data_for_hash = {
        "block_hash": data[0],
        "height": data[1],
        "chain_work": data[2],
    }
    return data_for_hash