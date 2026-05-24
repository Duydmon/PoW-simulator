# chứa các đường dẫn đến các hàm gọi chức năng.
import json

import requests
from flask import Flask, jsonify, request
import threading
import miner
import database
from config import NODE_ID, PORT, NODE_LIST
from node1 import network

app = Flask(__name__)


# -------------------
# Routes
# -------------------

@app.route("/")
def home():
    return jsonify({"message": "Blockchain Node Running"})


@app.route("/start")
def start_mining():
    if not miner.mining:
        miner.mining = True
        thread = threading.Thread(
            target=miner.mine
        )
        thread.start()
        return jsonify({
            "message": "Mining started"
        })
    return jsonify({
        "message": "Already mining"
    })


@app.route("/newest_block")
def newest_block():
    new_block = database.query_newest_block()
    block_json_str = json.dumps(
        new_block,
    )
    return block_json_str


@app.route("/add_mempool", methods=["POST"])
def add_to_mempool():
    body = request.get_json()
    data = body['data']
    node_id = body['node_id']
    time = body['time']
    if database.check_data_if_in_db(data, node_id, time):
        return jsonify({
            "message": "Data already in database"
        })
    database.add_data_mempool(data, node_id, time)
    return jsonify({
        "message": "Data added to mempool",
        "data": f'{data} from node {node_id}'
    })


@app.route("/stop")
def stop_mining():
    miner.mining = False

    return jsonify({
        "message": "Mining stopped"
    })


@app.route("/receive_node_id", methods=["POST"])
def receive_node_id():
    body = request.get_json()
    if body["node_id"] not in NODE_LIST:
        NODE_LIST[body['node_id']] = {
            "port": body['port']
        }
    return jsonify({
        "node_id": NODE_ID,
        "port": PORT
    })


@app.route('/get_mined_block', methods=["POST"])
def get_mined_block():
    body = request.get_json()
    validate_result = network.validate_block(body["block_data"], body["hashed_block"], body["sender_node_id"])
    if validate_result == False:
        return jsonify({
            "message": "Block not added to database"
        })
    tip_block_data = database.get_active_tip_block_data()
    is_main_chain = 0
    if tip_block_data["block_hash"] == body["block_data"]["previous_hash"]:
        is_main_chain = 1
    message_hash_list = []
    block_data_list = json.loads(body['block_data']['data'])
    for data in block_data_list:
        message_hash_list.append(data['hash'])
    database.mark_data_in_chain(message_hash_list)
    database.add_new_block(body["block_data"], body["hashed_block"], is_main_chain)
    return jsonify({
        "message": f"Block sent to {PORT}"
    })


# INSERT INTO blockchain(
#     block_hash,
#     previous_hash,
#     height,
#     timestamp,
#     difficulty,
#     miner,
#     data,
#     chain_work,
#     nonce,
#     is_main_chain
# )
# nhận yêu cầu và gửi full branch
@app.route('/get_missing_branch', methods=["POST"])
def get_missing_branch():
    body = request.get_json()
    receiver_node_id = body['receiver_node_id']
    requested_block_hash = body['block_hash']
    chain_hash_list = body['hash_list']
    requested_chain_hash_list = database.get_chain_from_tip(requested_block_hash)
    share_root = database.get_latest_shared_root(chain_hash_list, requested_chain_hash_list)
    if not share_root:
        return jsonify({
            "message": "Share root not found in database, block not added",
            "status": False
        })
    hash_list_to_send = database.get_blocks_after_shared_root(share_root, requested_chain_hash_list)
    for hash in hash_list_to_send:
        block_data = database.query_block_by_hash(hash)
        block_data_dict = {
            'block_hash': block_data[0],
            'previous_hash': block_data[1],
            'height': block_data[2],
            'timestamp': block_data[3],
            'difficulty': block_data[4],
            'miner': block_data[5],
            'data': block_data[6],
            'chain_work': block_data[7],
            'nonce': block_data[8]
        }
        network.send_block_to_node(block_data_dict, receiver_node_id)
    return jsonify({
        "message": "Missing branch sent",
        "status": True
    })

    # nhận: block yêu cầu + list dữ liệu
    # tìm share root #nếu không tìm được thì break và trả lại lỗi.
    # liên tục lặp qua chuôi để lấy dữ liệu và gọi thêm vào.
    # return
