from config import PORT, IP_ADDRESS, NODE_ID, NODE_LIST
import requests


def announce():
    for i in range(5000, 5011):
        if i == int(PORT):
            continue
        try:
            response = requests.post(
                f"http://{IP_ADDRESS}:{i}/receive_node_id",
                json={
                    "node_id": NODE_ID,
                    "port": PORT
                },
                timeout=0.2
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


def check_connection():
    connected_port = []
    for node in NODE_LIST:
        ports = NODE_LIST[node]["ports"]
        for port in ports:
            try:
                response = requests.get(f"http://{IP_ADDRESS}:{port}/")
                if response.status_code == 200: connected_port.append(port)
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.Timeout:
                continue
            except Exception as e: print(f"Node {port}: {e}")
    return connected_port
