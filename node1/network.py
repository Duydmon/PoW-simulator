# chứa các hàm giúp giao tiếp với node khác trong mạng lưới
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
        except Exception as e:
            print(f"Node {port}: {e}")
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
# transactions_json = json.dumps(transactions, sort_keys=True)

def validate_block(block_data_json: dict, block_hash: str, sender_node_id: str):
    hash_recalculate = hashlib.sha256(json.dumps(block_data_json, sort_keys=True).encode()).hexdigest()
    if hash_recalculate != block_hash:
        print("hash mismatch")
        return False
    previous_block_data = database.query_block_by_hash(block_data_json["previous_hash"])
    if not previous_block_data:
        print("Previous block not found")
        if get_missing_block(block_hash, sender_node_id):
            print("getting missing block")
        else:
            print("missing block not in branch")
        return False
    if previous_block_data[2] + 1 != block_data_json["height"]:
        print("Previous block height mismatch")
        return False
    if block_data_json["difficulty"] != DIFFICULTY:
        print("Block difficulty mismatch")
        return False
    # sau này validate miner sử dụng chứng thư số
    if block_data_json["chain_work"] - block_data_json["difficulty"] != previous_block_data[7]:
        print("Block difficulty mismatch")
        return False
    if not validate_data_in_block(block_data_json["data"]):
        print("Data mismatch")
        return False
    print("Block validated")
    return True


def validate_data_in_block(data_in_block_str: str):
    data_list = json.loads(data_in_block_str)
    for data in data_list:
        data_to_hash = {
            "data": data["data"],
            "node_id": data["node_id"],
            "timestamp": data["time"],
        }
        recaculate_hash = hashlib.sha256(json.dumps(data_to_hash, sort_keys=True).encode()).hexdigest()
        if recaculate_hash != data["hash"]:
            print("Hash mismatch")
            return False
        # block tạo thì sẽ validate sau
    print("Data validated")
    return True


def send_mined_block(this_block_data: dict, hashed_block: str):
    node_port_list = check_connection()
    for port in node_port_list:
        response = requests.post(
            f"http://{IP_ADDRESS}:{port}/get_mined_block",
            json={
                "block_data": this_block_data,
                "hashed_block": hashed_block,
                "sender_node_id": NODE_ID
                # sau này thêm hash của message đã đưa vào block nữa.
            }
        )
        print(response.json())


def send_block_to_node(block_data_dict, receiver_node_id):
    port = NODE_LIST[receiver_node_id]["port"]
    block_data_to_add = block_data_dict.copy()
    block_hash = block_data_to_add.pop("block_hash")
    response = requests.post(
        f'http://{IP_ADDRESS}:{port}/get_mined_block',
        json={
            "block_data": block_data_to_add,
            "hashed_block": block_hash,
            "sender_node_id": NODE_ID
        }
    )
    print(response.json())


# this_block_data ={
#             "previous_hash": previous_block_data["block_hash"],
#             "height": previous_block_data["height"]+1,
#             "timestamp": timestamp,
#             "difficulty": DIFFICULTY,
#             "miner": NODE_ID,
#             "data": data,
#             "chain_work": previous_block_data["chain_work"]+DIFFICULTY,
#             "nonce": nonce
#         }
def get_missing_block(block_hash: str, sender_node_id: str):
    sender_port = NODE_LIST[sender_node_id]["port"]
    tip_hash = database.get_active_tip_block_data()
    main_chain_hash_list = database.get_chain_from_tip(tip_hash["block_hash"])
    response = requests.post(f"http://{IP_ADDRESS}:{sender_port}/get_missing_branch",
                             json={"receiver_node_id": NODE_ID,
                                   "block_hash": block_hash,
                                   "hash_list": main_chain_hash_list
                                   }
                             )
    result = response.json()
    print(result)
    if result["status"] == False:
        print("Branch mismatch")
        return False
    else:
        return True
#gửi yêu cầu đến với từng node cùng với chain của nó.
def syncronize_database():
    response = {
        "message": "No port connected"
    }
    node_port_list = check_connection()
    hash_list = database.get_chain_from_tip(database.get_active_tip_block_data()["block_hash"])
    for port in node_port_list:
        response = requests.post(
            f"http://{IP_ADDRESS}:{port}/get_missing_branch",
            json={
                "receiver_node_id": NODE_ID,
                "block_hash": "get_all",
                "hash_list": hash_list
            }
        )
        database.reorg()
    print(response.json())

def syncronize_mempool():
    node_port_list = check_connection()
    response = {
        "message": "No port connected"
    }
    for port in node_port_list:
        data_hash_list = database.get_all_hash_in_mempool()
        response = requests.post(
            f"http://{IP_ADDRESS}:{port}/syncronize_mempool",
            json={
                "request_node_id": NODE_ID,
                "mempool_hash": data_hash_list
            }
        )
    print(response.json())
    # post: gửi danh sách tất cả hash trong ữ liệu.
    # B: lấy tất cả dữ liệu không ở trong danh sách
    # B: gửi lại sử dụng add to mempool
