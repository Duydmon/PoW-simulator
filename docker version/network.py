import hashlib
import json

from config import PORT, IP_ADDRESS, NODE_ID, NODE_LIST, DIFFICULTY, PEER_HOSTS
import requests
import database


def announce():
    peer_list = [p for p in PEER_HOSTS.split(",") if p.strip()]

    for peer in peer_list:
        try:
            response = requests.post(
                f"http://{peer}/receive_node_id",
                json={"node_id": NODE_ID, "port": PORT, "host": IP_ADDRESS},
                timeout=1.0
            )
            if response.status_code != 200:
                continue

            response_data = response.json()
            peer_node_id = response_data["node_id"]
            peer_host = peer.split(":")[0]
            peer_port = response_data["port"]

            if peer_node_id not in NODE_LIST:
                NODE_LIST[peer_node_id] = {"host": peer_host, "port": peer_port}

            print(f"Connected to peer {peer} (node_id: {peer_node_id[:8]}...)")

        except requests.exceptions.ConnectionError:
            print(f"Peer {peer} not reachable yet")
        except requests.exceptions.Timeout:
            print(f"Peer {peer} timeout")
        except Exception as e:
            print(f"Peer {peer}: {e}")


def check_connection():
    connected_node_list = []
    for node_id in list(NODE_LIST):
        host = NODE_LIST[node_id]["host"]
        port = NODE_LIST[node_id]["port"]
        try:
            response = requests.get(f"http://{host}:{port}/", timeout=0.5)
            if response.status_code == 200:
                connected_node_list.append({"host": host, "port": port, "node_id": node_id})
        except Exception:
            continue
    return connected_node_list


def validate_block(block_data_json: dict, block_hash: str, sender_node_id: str):
    hash_recalculate = hashlib.sha256(json.dumps(block_data_json, sort_keys=True).encode()).hexdigest()
    if hash_recalculate != block_hash:
        print("hash mismatch")
        return False
    previous_block_data = database.query_block_by_hash(block_data_json["previous_hash"])
    if not previous_block_data:
        print("Previous block not found, requesting missing branch...")
        if get_missing_block(block_hash, sender_node_id):
            print("Missing branch retrieved")
        else:
            print("Could not retrieve missing branch")
        return False
    if previous_block_data[2] + 1 != block_data_json["height"]:
        print("Height mismatch")
        return False
    if block_data_json["difficulty"] != DIFFICULTY:
        print("Difficulty mismatch")
        return False
    if block_data_json["chain_work"] - block_data_json["difficulty"] != previous_block_data[7]:
        print("chain_work mismatch")
        return False
    if not validate_data_in_block(block_data_json["data"]):
        print("Data hash mismatch")
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
        recalculate_hash = hashlib.sha256(json.dumps(data_to_hash, sort_keys=True).encode()).hexdigest()
        if recalculate_hash != data["hash"]:
            print("Data hash mismatch")
            return False
    print("Data validated")
    return True


def send_mined_block(this_block_data: dict, hashed_block: str):
    for node in check_connection():
        host = node["host"]
        port = node["port"]
        try:
            response = requests.post(
                f"http://{host}:{port}/get_mined_block",
                json={"block_data": this_block_data, "hashed_block": hashed_block, "sender_node_id": NODE_ID}
            )
            print(response.json())
        except Exception as e:
            print(f"Failed to send block to {host}:{port} — {e}")


def send_block_to_node(block_data_dict, receiver_node_id):
    if receiver_node_id not in NODE_LIST:
        print(f"receiver_node_id {receiver_node_id[:8]}... not in NODE_LIST")
        return
    host = NODE_LIST[receiver_node_id]["host"]
    port = NODE_LIST[receiver_node_id]["port"]
    block_data_to_add = block_data_dict.copy()
    block_hash = block_data_to_add.pop("block_hash")
    try:
        response = requests.post(
            f'http://{host}:{port}/get_mined_block',
            json={"block_data": block_data_to_add, "hashed_block": block_hash, "sender_node_id": NODE_ID}
        )
        print(response.json())
    except Exception as e:
        print(f"Failed to send block to {host}:{port} — {e}")


def get_missing_block(block_hash: str, sender_node_id: str):
    if sender_node_id not in NODE_LIST:
        print(f"Sender {sender_node_id[:8]}... not in NODE_LIST")
        return False
    sender_host = NODE_LIST[sender_node_id]["host"]
    sender_port = NODE_LIST[sender_node_id]["port"]

    tip_data = database.get_active_tip_block_data()
    main_chain_hash_list = database.get_chain_from_tip(tip_data["block_hash"])

    try:
        response = requests.post(
            f"http://{sender_host}:{sender_port}/get_missing_branch",
            json={"receiver_node_id": NODE_ID, "block_hash": block_hash, "hash_list": main_chain_hash_list}
        )
        result = response.json()
        print(result)
        return result.get("status", False)
    except Exception as e:
        print(f"get_missing_block error: {e}")
        return False


def syncronize_database():
    connected_nodes = check_connection()
    if not connected_nodes:
        print("No nodes connected")
        return
    hash_list = database.get_chain_from_tip(database.get_active_tip_block_data()["block_hash"])
    for node in connected_nodes:
        host = node["host"]
        port = node["port"]
        try:
            response = requests.post(
                f"http://{host}:{port}/get_missing_branch",
                json={"receiver_node_id": NODE_ID, "block_hash": "get_all", "hash_list": hash_list}
            )
            database.reorg()
            print(response.json())
        except Exception as e:
            print(f"syncronize_database error with {host}:{port} — {e}")


def syncronize_mempool():
    connected_nodes = check_connection()
    if not connected_nodes:
        print("No nodes connected")
        return
    for node in connected_nodes:
        host = node["host"]
        port = node["port"]
        try:
            data_hash_list = database.get_all_hash_in_mempool()
            response = requests.post(
                f"http://{host}:{port}/syncronize_mempool",
                json={"request_node_id": NODE_ID, "mempool_hash": data_hash_list}
            )
            print(response.json())
        except Exception as e:
            print(f"syncronize_mempool error with {host}:{port} — {e}")
