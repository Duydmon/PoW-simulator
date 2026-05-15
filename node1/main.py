#chứa menu và lựa chọn, đóng vai trò gọi chức năng và hiển thị cho người dùng
from engine import app
import threading
import requests
import hashlib
import time

from config import IP_ADDRESS, PORT, NODE_ID, URL

# IP_ADDRESS = "127.0.0.1"
# PORT:str = "5000"
# NODE_ID = hashlib.sha256((IP_ADDRESS+PORT).encode()).hexdigest()
# URL = f'http://{IP_ADDRESS}:{PORT}'


# -------------------
# Flask Server Thread
# -------------------
def run_server():

    app.run(
        host=IP_ADDRESS,
        port=int(PORT),
        debug=False
    )

# -------------------
# Menu
# -------------------
#3: thêm dữ liệu
#4: xem blockchain
#5: xem block mới nhất

def menu():
    requests.get(URL)
    while True:

        print("\n1. Start Mining")
        print("2. Stop Mining")
        print("0. Exit")

        choice = input("Select: ")

        # -------------------
        # Start Mining
        # -------------------
        if choice == "1":

            response = requests.get(
                f"{URL}/start"
            )

            print(response.json())

        # -------------------
        # Stop Mining
        # -------------------
        elif choice == "2":

            response = requests.get(
                f"{URL}/stop"
            )

            print(response.json())

        elif choice == "3":
            data = input("Enter your data: ")
            response = requests.post(
                f"{URL}/add_mempool",
                json={
                    "data": data,
                    "node_id": NODE_ID
                }
            )
            print(response.json())

        # elif choice == "4":
        #     response = requests.get()

        elif choice == "5":
            response = requests.get(
                f"{URL}/newest_block"
            )
            print(response.json())

        elif choice == "0":
            break

# -------------------
# Main
# -------------------
if __name__ == "__main__":
    # chạy flask ở thread riêng
    flask_thread = threading.Thread(
        target=run_server
    )
    flask_thread.start()
    time.sleep(1)
    # chạy menu
    menu()