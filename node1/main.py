# chứa menu và lựa chọn, đóng vai trò gọi chức năng và hiển thị cho người dùng
from asyncio import wait

from engine import app
import threading
import requests
import time
import network
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


def menu():
    requests.get(URL)
    time.sleep(0.1)
    while True:
        print("\n1. Start Mining")
        print("2. Stop Mining")
        print("3. Add mempool")
        print("4. Print Node List")
        print("5. Check newest block")
        print("6. re-Announce")
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
            node_port_list = network.check_connection()
            node_port_list.append(PORT)
            timestamp = time.time()
            for port in node_port_list:
                response = requests.post(
                    f"http://{IP_ADDRESS}:{port}/add_mempool",
                    json={
                        "data": data,
                        "node_id": NODE_ID,
                        "time": timestamp
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

        elif choice == "6":
            network.announce()

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
    network.announce()
    print(NODE_LIST)
    menu()
