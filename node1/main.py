#chứa menu và lựa chọn, đóng vai trò gọi chức năng và hiển thị cho người dùng
from engine import app
import threading
import requests
import time

from config import IP_ADDRESS, PORT, NODE_ID, URL, NODE_LIST

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
        print("3. Add mempool")
        print("4. Print Node List")
        print("5. Check newest block")
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

        elif choice == "4":
            print(NODE_LIST)

        elif choice == "5":
            response = requests.get(
                f"{URL}/newest_block"
            )
            print(response.json())

        elif choice == "0":
            break

def announce():
    for i in range(5000, 5011):
        if i == int(PORT):
            continue
        try:
            response = requests.post(
                f"http://{IP_ADDRESS}:{i}/receive_node_id",
                json={
                    "node_id": NODE_ID,
                    "port": int(PORT)
                },
                timeout=0.1
            )
            if response.status_code != 200:
                continue
            response_node_data = response.json()
            if response_node_data["node_id"] in NODE_LIST:
                continue
            NODE_LIST[
                response_node_data["node_id"]
            ] = {
                "port": response_node_data["port"]
            }
            print(f"Connected node {i}")
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"Node {i}: {e}")

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
    announce()
    print(NODE_LIST)
    menu()