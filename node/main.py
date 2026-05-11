from engine import app
import threading
import requests

# -------------------
# Flask Server Thread
# -------------------
def run_server():

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

# -------------------
# Menu
# -------------------
def menu():

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
                "http://127.0.0.1:5000/start"
            )

            print(response.json())

        # -------------------
        # Stop Mining
        # -------------------
        elif choice == "2":

            response = requests.get(
                "http://127.0.0.1:5000/stop"
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