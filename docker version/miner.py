import hashlib
import json
from typing import Any

import database
import time
from config import NODE_ID, DIFFICULTY, NODE_LIST, IP_ADDRESS
import network

mining = False
mempool_have_data = False

def prepare_data_to_hash() -> tuple[str, list[Any]] | tuple[None, None]:
    global mining
    mempool = database.get_data_from_mempool()
    if not mempool:
        return None, None
    transactions = []
    message_hash = []
    for row in mempool:
        tx = {
            "hash": row[0],
            "time": row[1],
            "data": row[2],
            "node_id": row[3]
        }
        message_hash.append(row[0])
        transactions.append(tx)
    transactions_json = json.dumps(transactions, sort_keys=True)
    return transactions_json, message_hash

def mine():
    global mining
    while mining:
        # bước 1: lấy state mới mỗi lần bắt đầu mine một block
        tip_block_data = database.get_active_tip_block_data()
        tip_block_hash = tip_block_data["block_hash"]
        data, message_hash = prepare_data_to_hash()
        if not data or not message_hash:
            print("No more data in mempool")
            print("Stopping mining")
            mining = False
            return
        else:
            print("Mempool still have data, keep mining")
        timestamp = time.time()
        nonce = 0
        found = False

        while mining:
            # bước 3: hash liên tục, kiểm tra tip mỗi 100 nonce
            this_block_data = {
                "previous_hash": tip_block_hash,
                "height": tip_block_data["height"] + 1,
                "timestamp": timestamp,
                "difficulty": DIFFICULTY,
                "miner": NODE_ID,
                "data": data,
                "chain_work": tip_block_data["chain_work"] + DIFFICULTY,
                "nonce": nonce
            }
            hashed_block: str = hashlib.sha256(json.dumps(this_block_data, sort_keys=True).encode()).hexdigest()
            if hashed_block.startswith("0" * DIFFICULTY):
                found = True
                break
            nonce += 1
            if nonce % 1000 == 0:
                if nonce % 100000 == 0:
                    timestamp = time.time()
                new_tip_block_data = database.get_active_tip_block_data()
                if new_tip_block_data["block_hash"] != tip_block_hash:
                    print("New tip detected, restart mining")
                    break  # thoát vòng trong, vòng ngoài tự lấy state mới

        # bước 4: chỉ chạy khi found = True
        if found:
            fresh_data, fresh_message_hash = prepare_data_to_hash()
            if fresh_data != data:
                print("Data in mempool changed, restart mining")
                continue  # quay lại vòng ngoài, lấy state mới
            print("mine success")
            print(hashed_block)
            print(this_block_data)
            database.add_new_block(this_block_data, hashed_block)
            network.send_mined_block(this_block_data, hashed_block)
            database.mark_data_in_chain(message_hash)
            print("Block mined, checking mempool...")
            # không set mining = False, vòng ngoài tự kiểm tra mempool lần sau