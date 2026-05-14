import sqlite3
import json

conn = sqlite3.connect("./node1/db/blockchain.db")

cursor = conn.cursor()

# lấy block
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
WHERE block_hash = ?
""", ("TEST",))

row = cursor.fetchone()

# convert thành dict
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

# convert sang JSON
block_json = json.dumps(
    block,
    sort_keys=True
)

print(block_json)

