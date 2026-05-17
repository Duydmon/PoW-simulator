#chứa các hàm và code truy xuât, nhập liệu dữ liệu vào cơ sở dữ liệu
import hashlib
import json
import sqlite3
import time

# khi đưa data vào, sẽ ký số và

def add_data_mempool(data,node_id,timestamp):
    data_to_hash = {
        "data": data,
        "node_id": node_id,
        "timestamp": timestamp
    }
    hased_data = hashlib.sha256(json.dumps(data_to_hash,sort_keys=True).encode()).hexdigest()
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mempool(
            hash,
            time,
            data,
            node_id,
            in_chain
        )
        VALUES (?, ?, ?, ?,?)
    """, (
        hased_data,
        timestamp,
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
     SELECT hash, time, data, node_id, id
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

def mark_data_in_chain(message_hash_list):
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.executemany("""
                   UPDATE mempool
                   SET in_chain = 1
                   WHERE hash = ?
                   """, [(hash,) for hash in message_hash_list])
    conn.commit()
    conn.close()

def add_new_block(block_data_dict, block_hash):
    # this_block_data = {
    #     "previous_hash": previous_block_data["block_hash"],
    #     "height": previous_block_data["height"] + 1,
    #     "timestamp": time.time(),
    #     "difficulty": DIFFICULTY,
    #     "miner": NODE_ID,
    #     "data": data,
    #     "chain_work": previous_block_data["chain_work"] + DIFFICULTY,
    #     "nonce": nonce
    # }
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO blockchain(
        block_hash,
        previous_hash,
        height,
        timestamp,
        difficulty,
        miner,
        data,
        chain_work,
        nonce,
        is_main_chain
        ) 
    VALUES ( ?, ?, ?, ?, ? ,? ,? ,? ,?, 1)
        """, (
        block_hash,
        block_data_dict["previous_hash"],
        block_data_dict["height"],
        block_data_dict["timestamp"],
        block_data_dict["difficulty"],
        block_data_dict["miner"],
        block_data_dict["data"],
        block_data_dict["chain_work"],
        block_data_dict["nonce"]
    ))
    conn.commit()
    conn.close()

def check_data_if_in_db(data,node_id,timestamp):
    data_to_hash = {
        "data": data,
        "node_id": node_id,
        "timestamp": timestamp
    }
    hased_data = hashlib.sha256(json.dumps(data_to_hash, sort_keys=True).encode()).hexdigest()
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT COUNT(*) FROM mempool
                   WHERE hash = ?
                   """, (hased_data,))
    count = cursor.fetchone()[0]
    conn.close()
    return count>0

# def get_all_block_data():
#     conn = sqlite3.connect('./db/blockchain.db')
#     cursor = conn.cursor()
#     cursor.execute("""
#                    SELECT * FROM blockchain
#                    WHERE is_main_chain = 1
#