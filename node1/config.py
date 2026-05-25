import hashlib
IP_ADDRESS = "127.0.0.1"
PORT:str = "5000"
NODE_ID = hashlib.sha256((IP_ADDRESS+PORT).encode()).hexdigest()
URL = f'http://{IP_ADDRESS}:{PORT}'
DIFFICULTY = 5
NODE_LIST = {}
BLOCK_COUNT = 0
BLOCK_LIMIT = 3