import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"db", "blockchain.db")

def restart_database():
    # -------------------
    # Delete old database
    # -------------------
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # -------------------
    # Connect Database
    # -------------------
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # -------------------
    # Create mempool table
    # -------------------

    cursor.execute("""
    CREATE TABLE mempool(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        time INTEGER NOT NULL,
        node_id TEXT NOT NULL,
        data TEXT,
        in_chain INTEGER
    )
    """)

    # -------------------
    # Create blockchain table
    # -------------------

    cursor.execute("""
    
    CREATE TABLE blockchain(
        block_hash TEXT PRIMARY KEY,
        previous_hash TEXT,
        height INTEGER,
        timestamp INTEGER,
        difficulty INTEGER,
        miner TEXT,
        data TEXT,
        chain_work INTEGER,
        nonce INTEGER,
        is_main_chain INTEGER
    )
    
    """)

    # -------------------
    # Genesis Block
    # -------------------

    genesis_block = {
        "block_hash": "GENESIS",
        "previous_hash": "NONE",
        "height": 0,
        "timestamp": 0,
        "difficulty": 0,
        "miner": "GENESIS",
        "data": "GENESIS",
        "chain_work": 0,
        "nonce": 0,
        "is_main_chain": 1
    }

    # -------------------
    # Insert Genesis Block
    # -------------------

    cursor.execute("""
    
    INSERT INTO blockchain(
        block_hash,
        previous_hash,
        height,
        timestamp,
        difficulty,
        miner,
        data,
        chain_work,
        nonce,
        is_main_chain
    )
    
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    
    """, (
        genesis_block["block_hash"],
        genesis_block["previous_hash"],
        genesis_block["height"],
        genesis_block["timestamp"],
        genesis_block["difficulty"],
        genesis_block["miner"],
        genesis_block["data"],
        genesis_block["chain_work"],
        genesis_block["nonce"],
        genesis_block["is_main_chain"]
    ))

    # -------------------
    # Save & Close
    # -------------------
    conn.commit()
    conn.close()
    print("Blockchain database initialized!")

if __name__ == "__main__":
    restart_database()