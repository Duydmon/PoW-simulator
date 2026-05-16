#chứa các đường dẫn đến các hàm gọi chức năng.
import json
from flask import Flask, jsonify, request
import threading
import miner
import database
from config import NODE_ID, PORT, NODE_LIST
app = Flask(__name__)

# -------------------
# Routes
# -------------------

@app.route("/")
def home():
    return jsonify({"message":"Blockchain Node Running"})

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
    database.add_data_mempool(data,node_id)
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
        "port": int(PORT)
    })

