import hashlib
import json
from typing import Any

import database
import time
from config import NODE_ID, DIFFICULTY, NODE_LIST, IP_ADDRESS
import network

mining = False


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
    nonce = 0
    data, message_hash = prepare_data_to_hash()
    if not data or not message_hash:
        print("No more data in mempool")
        mining = False
        return
    timestamp = time.time()
    while mining:
        previous_block_data = database.get_active_tip_block_data()  # block_hash, height, chain_work
        this_block_data = {
            "previous_hash": previous_block_data["block_hash"],
            "height": previous_block_data["height"] + 1,
            "timestamp": timestamp,
            "difficulty": DIFFICULTY,
            "miner": NODE_ID,
            "data": data,
            "chain_work": previous_block_data["chain_work"] + DIFFICULTY,
            "nonce": nonce
        }
        this_block_data_for_hash = json.dumps(this_block_data, sort_keys=True)
        hashed_block = hashlib.sha256(this_block_data_for_hash.encode()).hexdigest()
        if hashed_block.startswith("0" * DIFFICULTY):
            mining = False
            print("mine success")
            print(hashed_block)
            print(this_block_data_for_hash)
            database.add_new_block(this_block_data, hashed_block)
            network.send_mined_block(this_block_data, hashed_block)
            # node_port_list = network.check_connection()
            # for port in node_port_list:
            #     response = requests.post(
            #         f"http://{IP_ADDRESS}:{port}/get_mined_block",
            #         json = {
            #             "block_data": this_block_data,
            #             "hashed_block": hashed_block
            #             #sau này thêm hash của message đã đưa vào block nữa.
            #         }
            #     )
            #     print(response.json())
            database.mark_data_in_chain(message_hash)
        else:
            nonce += 1
            print("mining...")
            print(f"Failed hassh:{hashed_block}")

# cần trả lại kiểm soát về menu
# khi xong thì vẫn dừng mine. cần thêm cái để mine đến khi mempool rỗng, khi nào mempool có thì tiếp tục mine.
