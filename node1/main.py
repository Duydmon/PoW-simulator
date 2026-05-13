from engine import app
import threading
import requests
import hashlib

IP_ADDRESS = "127.0.0.1"
PORT:str = "5000"
NODE_ID = hashlib.sha256((IP_ADDRESS+PORT).encode()).hexdigest()
URL = f'http://{IP_ADDRESS}:{PORT}'


# -------------------
# Flask Server Thread
# -------------------
def run_server():

    app.run(
        host=URL,
        port=int(PORT),
        debug=False
    )

# -------------------
# Menu
# -------------------
def menu():
    requests.get(URL)
    while True:

        print("\n1. Start Mining")
        print("2. Stop Mining")
        print("3. Exit")

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

        # -------------------
        # Exit
        # -------------------
        elif choice == "3":
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
    # chạy menu
    menu()