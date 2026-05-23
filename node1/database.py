#chứa các hàm và code truy xuât, nhập liệu dữ liệu vào cơ sở dữ liệu
import hashlib
import json
import sqlite3
from config import BLOCK_COUNT, BLOCK_LIMIT

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

def get_active_tip_block_data() -> dict:
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

def mark_data_in_chain(message_hash_list,chain_status = 1):
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.executemany("""
                   UPDATE mempool
                   SET in_chain = ?
                   WHERE hash = ?
                   """, [(chain_status,hash) for hash in message_hash_list])
    conn.commit()
    conn.close()

def add_new_block(block_data_dict, block_hash, main_chain_value = 1):
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
    global BLOCK_COUNT
    BLOCK_COUNT += 1
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
    VALUES ( ?, ?, ?, ?, ? ,? ,? ,? ,?, ?)
        """, (
        block_hash,
        block_data_dict["previous_hash"],
        block_data_dict["height"],
        block_data_dict["timestamp"],
        block_data_dict["difficulty"],
        block_data_dict["miner"],
        block_data_dict["data"],
        block_data_dict["chain_work"],
        block_data_dict["nonce"],
        main_chain_value
    ))
    conn.commit()
    conn.close()
    if BLOCK_COUNT >= BLOCK_LIMIT:
        BLOCK_COUNT = 0
        reorg()

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

def query_block_by_hash(hash)-> tuple:
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT * FROM blockchain WHERE block_hash = ?""", (hash,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_tip_block_list()->list[dict]:
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT *
                   FROM blockchain b1
                   WHERE NOT EXISTS (SELECT 1
                       FROM blockchain b2
                       WHERE b2.previous_hash = b1.block_hash
                   )
                   ORDER BY chain_work DESC;""")
    rows = cursor.fetchall()
    conn.close()
    tip_block_list = []
    for row in rows:
        tip_block_data = {
            "block_hash": row[0],
            "previous_hash": row[1],
            "height": row[2],
            "chain_work": row[7],
            "is_main_chain": row[9]
        }
        tip_block_list.append(tip_block_data)
    return tip_block_list

def reorg():
    # lấy danh sách dữ liệu của các tip block
    tip_block_list = get_tip_block_list()
    #duyệt danh sách, tìm tip có nhiều work nhất
    highest_work = 0
    highest_work_block_hash:str = ""
    for block_data in tip_block_list:
        if block_data["chain_work"] > highest_work:
            highest_work = block_data["chain_work"]
            highest_work_block_hash = block_data["block_hash"]
    current_tip_data = get_active_tip_block_data()
    if highest_work_block_hash == current_tip_data["block_hash"]:
        print("Active chain is the longest, no re-organize")
        return
    #query recursive để lấy tất cả hash của nhánh của tip
    current_tip_chain_hash = get_chain_from_tip(current_tip_data["block_hash"])
    highest_work_chain_hash = get_chain_from_tip(highest_work_block_hash)
    # tìm common root (function)
    last_share_root = get_latest_shared_root(current_tip_chain_hash,highest_work_chain_hash)
    if not last_share_root:
        print("No last share root")
        return
    old_block_hash_list_to_change = get_blocks_after_shared_root(last_share_root,current_tip_chain_hash)
    new_block_hash_list_to_change = get_blocks_after_shared_root(last_share_root,highest_work_chain_hash)
    mark_block_in_database(new_block_hash_list_to_change,1)
    print("Main chain updated")
    mark_block_in_database(old_block_hash_list_to_change,0)
    print("old chain updated")
    block_data_in_old_chain_list = get_data_in_block_by_hash(old_block_hash_list_to_change)
    block_data_in_new_chain_list = get_data_in_block_by_hash(new_block_hash_list_to_change)
    #lấy list dữ liệu trong chain cũ
    data_hash_in_old_chain_json_list = []
    #weird data save in block in blockchain: str of list of json(dict)
    #[{"data": "data in chain 1", "hash": "b6d9ab2cb7d5f8c319561d678215379b0cd038fa45e2cbb6cc967f3f6162792a", "node_id": "54dfa451cf9896851bdf9b37061062b5297b8fb83a061c46e5054d8118667daa", "time": 1779117665.6297834}]
    for i in block_data_in_old_chain_list:
        list_of_json = json.loads(i)
        for a in list_of_json:
            data_hash_in_old_chain_json_list.append(a["hash"])
    #lấy list dữ liệu trong chain mới
    data_hash_in_new_chain_json_list = []
    for i in block_data_in_new_chain_list:
        list_of_json = json.loads(i)
        for a in list_of_json:
            data_hash_in_new_chain_json_list.append(a["hash"])
    data_hash_in_old_chain_json_set = set(data_hash_in_old_chain_json_list)
    data_hash_in_new_chain_json_set = set(data_hash_in_new_chain_json_list)
    # Kiểm tra xem trong chain cũ có dữ liệu trong chain mới không
    data_to_rollback = (data_hash_in_old_chain_json_set - data_hash_in_new_chain_json_set)
    data_to_in_chain = (data_hash_in_new_chain_json_set - data_hash_in_old_chain_json_set)
    # set mempool not in_chain.
    # set mempool in_chain
    mark_data_in_chain(data_to_rollback,0)
    mark_data_in_chain(data_to_in_chain,1)
    print("Mempool re-organized")
    # the data is so fucking weird

def mark_block_in_database(
        block_hash_list: list,
        in_chain_value: int
):
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    cursor.executemany("""
        UPDATE blockchain
        SET is_main_chain = ?
        WHERE block_hash = ?
    """, [
        (in_chain_value, block_hash)
        for block_hash in block_hash_list
    ])
    conn.commit()
    conn.close()

def get_blocks_after_shared_root(
        shared_root: str,
        chain_hash_list: list
) -> list:

    try:
        root_index = chain_hash_list.index(shared_root)

        return chain_hash_list[root_index+1:]

    except ValueError:
        print("Shared root not found")
        return []

def get_latest_shared_root(chain1: list, chain2: list)-> str:
    latest_shared:str = ""
    for block1, block2 in zip(chain1, chain2):
        if block1 == block2:
            latest_shared = block1
        else:
            break
    return latest_shared

def get_chain_from_tip(tip_hash):
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()

    cursor.execute("""
    WITH RECURSIVE chain_path AS (
        SELECT
            block_hash,
            previous_hash,
            height
        FROM blockchain
        WHERE block_hash = ?
            
        UNION ALL
            
        SELECT
            b.block_hash,
            b.previous_hash,
            b.height
        FROM blockchain b
        JOIN chain_path c
        ON b.block_hash = c.previous_hash
    )
    SELECT block_hash
    FROM chain_path
    ORDER BY height ASC
    """, (tip_hash,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_data_in_block_by_hash(block_hash_list: list) -> list:
    conn = sqlite3.connect('./db/blockchain.db')
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(block_hash_list))
    cursor.execute(f"""
            SELECT data
            FROM blockchain
            WHERE block_hash IN ({placeholders})
        """, block_hash_list)
    rows = cursor.fetchall()
    rows_list = [row[0] for row in rows]
    conn.close()
    return rows_list
