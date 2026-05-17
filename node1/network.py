#chứa các hàm giúp giao tiếp với node khác trong mạng lưới
import hashlib
import json
import time
from config import PORT, IP_ADDRESS, NODE_ID, NODE_LIST, DIFFICULTY
import requests
import database


def announce():
    for i in range(5000, 5011):
        if i == int(PORT):
            continue
        try:
            response = requests.post(
                f"http://{IP_ADDRESS}:{i}/receive_node_id",
                json={
                    "node_id": NODE_ID,
                    "port": PORT
                },
                timeout=0.2
            )
            if response.status_code != 200:
                continue
            response_node_data = response.json()
            if response_node_data["node_id"] in NODE_LIST:
                continue
            NODE_LIST[
                response_node_data["node_id"]
            ] = {
                "port": response_node_data["port"]
            }
            print(f"Connected node {i}")
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"Node {i}: {e}")


def check_connection():
    connected_port = []
    for node in NODE_LIST:
        port = NODE_LIST[node]["port"]
        try:
            response = requests.get(f"http://{IP_ADDRESS}:{port}/")
            if response.status_code == 200:
                connected_port.append(port)
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            continue
        except Exception as e: print(f"Node {port}: {e}")
    return connected_port

# CREATE TABLE blockchain(
#  0   block_hash TEXT PRIMARY KEY,
#  1  previous_hash TEXT,
#  2  height INTEGER,
#  3  timestamp INTEGER,
#  4  difficulty INTEGER,
#  5  miner TEXT,
#  6  data TEXT,
#  7  chain_work INTEGER,
#  8  nonce INTEGER,
#  9  is_main_chain INTEGER
# )
# this_block_data ={
#             "previous_hash": previous_block_data["block_hash"],
#             "height": previous_block_data["height"]+1,
#             "timestamp": time.time(),
#             "difficulty": DIFFICULTY,
#             "miner": NODE_ID,
#             "data": data,
#             "chain_work": previous_block_data["chain_work"]+DIFFICULTY,
#             "nonce": nonce
#         }
# tx = {
#     "hash": row[0],
#     "time": row[1],
#     "data": row[2],
#     "node_id": row[3]
# }
#transactions_json = json.dumps(transactions, sort_keys=True)

def validate_block(block_data_json:dict,block_hash:str):
     hash_recalculate = hashlib.sha256(json.dumps(block_data_json,sort_keys=True).encode()).hexdigest()
     if hash_recalculate != block_hash:
         print("hash mismatch")
         return False
     previous_block_data = database.query_block_by_hash(block_data_json["previous_hash"])
     if not previous_block_data:
         print("Previous block not found")
         return False
     if previous_block_data[2]+1 != block_data_json["height"]:
         print("Previous block height mismatch")
         return False
     if not 0 <= time.time() - block_data_json["timestamp"] <= 7200:
         print("Block timestamp too old or in the future")
         return False
     if block_data_json["difficulty"] != DIFFICULTY:
         print("Block difficulty mismatch")
         return False
     #sau này validate miner sử dụng chứng thư số
     if block_data_json["chain_work"]- block_data_json["difficulty"] != previous_block_data[7]:
         print("Block difficulty mismatch")
         return False
     if not validaate_data_in_block(block_data_json["data"]):
         print("Data mismatch")
         return False
     print("Block validated")
     return True

def validaate_data_in_block(data_in_block_str:str):
    data_list = json.loads(data_in_block_str)
    for data in data_list:
        data_to_hash ={
            "data": data["data"],
            "node_id": data["node_id"],
            "timestamp": data["time"],
        }
        recaculate_hash = hashlib.sha256(json.dumps(data_to_hash,sort_keys=True).encode()).hexdigest()
        if recaculate_hash != data["hash"]:
            print("Hash mismatch")
            return False
        if not 0 <= time.time() - data["time"] <= 7200:
            print("Block timestamp too old or in the future")
            return False
        #block tạo thì sẽ validate sau
    print("Data validated")
    return True
