from flask import Flask, jsonify
import threading

import miner

app = Flask(__name__)

# -------------------
# Routes
# -------------------

@app.route("/")
def home():

    return "Blockchain Node Running"

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

@app.route("/stop")
def stop_mining():

    miner.mining = False

    return jsonify({
        "message": "Mining stopped"
    })