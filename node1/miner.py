import hashlib
import json
import threading
import database
import time

from config import NODE_ID, DIFFICULTY
mining = False

def prepare_data_to_hash() -> str:
    mempool = database.get_data_from_mempool()
    transactions =[]
    for row in mempool:
        tx ={
            "time": row[0],
            "data": row[1],
            "node_id": row[2]
        }
        transactions.append(tx)

    transactions_json = json.dumps(transactions, sort_keys=True)
    return transactions_json

def mine():
    global mining
    nonce = 0
    while mining:
        data = prepare_data_to_hash()
        previous_block_data = database.get_tip_block_data() #block_hash, height, chain_work
        this_block_data ={
            "previous_hash": previous_block_data["block_hash"],
            "height": previous_block_data["height"]+1,
            "timestamp": time.time(),
            "difficulty": DIFFICULTY,
            "miner": NODE_ID,
            "data": data,
            "chain_work": previous_block_data["chain_work"]+DIFFICULTY,
            "nonce": nonce
        }
        this_block_data_for_hash = json.dumps(this_block_data, sort_keys=True)
        hashed_block = hashlib.sha256(this_block_data_for_hash.encode()).hexdigest()
        if hashed_block.startswith("0"*DIFFICULTY):
            mining = False
            print("mine success")
            print(hashed_block)
            print(this_block_data_for_hash)
        else:
            nonce += 1
            print("mining...")
            print(f"Failed hassh:{hashed_block}")

#cần trả lại kiểm soát về menu