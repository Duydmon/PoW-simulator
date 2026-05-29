import threading
import time
import sys
import requests

from engine import app
import network
from config import BIND_ADDRESS, PORT, NODE_ID, URL, NODE_LIST
import miner
import restart_database

# -------------------
# Flask Server Thread
# -------------------
def run_server():
    # BIND_ADDRESS luôn là 0.0.0.0 → Flask nhận kết nối từ mọi interface
    app.run(
        host=BIND_ADDRESS,
        port=int(PORT),
        debug=False
    )

def safe_input(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    raw = sys.stdin.buffer.readline()
    return raw.decode('utf-8', errors='replace').rstrip('\n').rstrip('\r')

def menu():
    # Chờ Flask khởi động (tối đa 5 giây)
    for _ in range(10):
        try:
            requests.get(URL, timeout=0.5)
            break
        except Exception:
            time.sleep(0.5)

    while True:
        print("\n1. Start Mining")
        print("2. Stop Mining")
        print("3. Add mempool")
        print("4. Print Node List")
        print("5. Check newest block")
        print("6. re-Announce")
        print("7. Syncronize blockchain")
        print("8. Syncronize mempool")
        print("100. Restart database")
        print("0. Exit")

        choice = safe_input("Select: ")

        if choice == "1":
            try:
                response = requests.get(f"{URL}/start")
                print(response.json())
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            try:
                response = requests.get(f"{URL}/stop")
                print(response.json())
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            data = safe_input("Enter your data: ")
            connected_node_dict = network.check_connection()
            timestamp = time.time()
            for node in connected_node_dict:
                host = node["host"]
                port = node["port"]
                try:
                    response = requests.post(
                        f"http://{host}:{port}/add_mempool",
                        json={"data": data, "node_id": NODE_ID, "time": timestamp}
                    )
                    print(response.json())
                except Exception as e:
                    print(f"Could not reach {host}:{port} — {e}")
            # Thêm vào mempool của chính mình
            try:
                requests.post(
                    f"{URL}/add_mempool",
                    json={"data": data, "node_id": NODE_ID, "time": timestamp}
                )
            except Exception as e:
                print(f"Could not add to local mempool — {e}")

        elif choice == "4":
            print(NODE_LIST)
            print(network.check_connection())

        elif choice == "5":
            try:
                response = requests.get(f"{URL}/newest_block")
                print(response.json())
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":
            network.announce()

        elif choice == "7":
            network.syncronize_database()

        elif choice == "8":
            network.syncronize_mempool()

        elif choice == "100":
            restart_database.restart_database()

        elif choice == "0":
            if miner.mining:
                miner.mining = False
                print("Stopping miner")
                time.sleep(0.5)
            break


# -------------------
# Main
# -------------------
if __name__ == "__main__":
    import os
    from restart_database import DB_PATH
    if not os.path.exists(DB_PATH):
        print("Database not found, initializing...")
        restart_database.restart_database()

    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()
    time.sleep(1)

    network.announce()
    print(f"NODE_LIST: {NODE_LIST}")

    menu()
    print("Goodbye")
