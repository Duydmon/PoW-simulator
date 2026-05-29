import hashlib
import os

# --- Bind address: Flask luôn bind 0.0.0.0 trong Docker ---
BIND_ADDRESS = "0.0.0.0"

# --- Port của node này ---
PORT = os.environ.get("PORT", "5000")

# --- Hostname để node KHÁC gọi đến (tên container Docker, vd: "node1") ---
# Đây cũng là định danh của node trong mạng
IP_ADDRESS = os.environ.get("IP_ADDRESS", "node1")

# --- NODE_ID dựa trên hostname + port → unique mỗi node ---
NODE_ID = hashlib.sha256((IP_ADDRESS + PORT).encode()).hexdigest()

# --- URL nội bộ: menu() tự gọi Flask của chính mình ---
URL = f'http://127.0.0.1:{PORT}'

DIFFICULTY = int(os.environ.get("DIFFICULTY", "3"))
NODE_LIST = {}
BLOCK_COUNT = 0
BLOCK_LIMIT = 3
DATA_IN_BLOCK_LIMIT = 2

# Danh sách peer Docker: "node2:5001,node3:5002"
PEER_HOSTS = os.environ.get("PEER_HOSTS", "")
