import requests
import socket
import json
import time
import pprint
from datetime import datetime

#Json
def json_config():
    with open('config.json', "r") as x:
        json_file = json.load(x)
        return json_file['mode'], json_file['delay_mins'], json_file['ip_socket'], json_file['port_socket'], json_file['url']
### ---------------

#data dias e tals
def update_datatime():   
    data_atual = datetime.today()
    return data_atual.strftime("%Y-%m-%d %H:%M:%S")
### ------------------

# Socket setup
conn = None 
def setup_socket():
    print("[SOCKET] Initializing socket...")
    Host, Port = ip_socket, port_socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((Host, Port))
    s.listen()
    print(f"[SOCKET] Server initialized on: {Host}:{Port}\n[SOCKET] Waiting for connection")
    global conn
    conn, addr = s.accept()
    print(f"[SOCKET] Connection established with {addr}")

def send_delay(timeout):
    timeout = str(timeout)
    conn.sendall(str.encode(timeout))
    eco = conn.recv(1024)
    if not eco:
        print("[SOCKET] Error trying to send delay, trying again")
        time.sleep(1)
        send_delay(int(timeout))    
    eco = eco.decode()
    print(f"[SOCKET] {eco} is the delay returned by the esp32")

def update_data():
    try:
        global conn
        data = conn.recv(1024)
        if not data:
            print("[SOCKET] No data received, connection may have been closed.")
            return None
        data = data.decode('utf-8')
        print(f"[SOCKET] Received: {data}")
        if data != "TEST":
            return data
        else:
            conn.sendall(data)
            return None
    except Exception as e:
        print(f"[SOCKET] Error: {e}")
        return None
#------

# Tratament of data
def process_data(updated_data):
    print(f"[Data Processing] Received data: {updated_data}")
    time.sleep(1)  
    if updated_data is None:
        print("[Data Processing] No data to process.")
        return None
    data_dict = {
        "Temperature": 0.0,
        "Pressure": 0.0,
        "Datetime": 0
    }
    temp_pressure = updated_data.split("/")
    temp = temp_pressure[0].strip()
    pressure = temp_pressure[1].strip()
    data_dict["Temperature"] = float(temp)
    data_dict["Pressure"] = float(pressure)
    data_dict["Datetime"] = update_datatime()
    print(f"[Data Processed] Temperature: {data_dict['Temperature']} °C, Pressure: {data_dict['Pressure']} Pa, Datetime: {data_dict['Datetime']}")
    return data_dict
#------

# Enviando para o Firebase
def send_to_firebase(data):
    try:
        _url = f"{url}atual.json"
        headers = {"Content-Type": "application/json"}
        response = requests.post(_url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print(f"[Firebase] Status code: {response.status_code}.")
            time.sleep(0.3)
            print("[Firebase] Data sent successfully.")
            print(f"[Firebase] {response.text}")
        else:
            print(f"[Firebase] Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        print(f"[Firebase] Error sending data: {e}")

# Recebendo do Firebase
def receive_from_firebase(id):
    try:
        _url = f"{url}{id}.json"
        response = requests.get(_url)
        if response.status_code == 200:
            print(f"[Firebase] Status code: {response.status_code}.")
            data = response.json()
            print("[Firebase] Data received successfully.")
            pprint.pprint(data)
            return data
        else:
            print(f"[Firebase] Failed to receive data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Firebase] Error receiving data: {e}")
        return None
    
#------

# Main function
def main(timeout):
    x = 0
    setup_socket()
    send_delay(timeout)
    while True:
        updated_data = update_data()
        if updated_data:
            processed_data = process_data(updated_data)
            if processed_data:
                send_to_firebase(processed_data)
        x += 1        
        time.sleep(0.5)


def inialize():
    global mode, delay, ip_socket, port_socket, url
    mode, delay, ip_socket, port_socket, url = json_config()
    if mode == "main":
        print(f"[Started] Main with {delay} minutes delay")
        main(delay * 60)
    elif mode == "test":
        print("[Started] Test")
        test_firebase()
    elif mode == "get":
        receive_from_firebase(input("ID: "))

def test_firebase():
    print("[TEST] Testing Firebase connection...")
    data = receive_from_firebase("atual")
    if data:
        print("[TEST] Data received from Firebase:", data)
    else:
        print("[TEST] No data received from Firebase.")
        print("[TEST] Probably the database is empty or the ID is incorrect.")
        print("[TEST] Trying to send data to Firebase ")
        test_data = {
            "Temperature": 25.0,
            "Pressure": 101325.0,
            "Datetime": update_datatime()
        }
        send_to_firebase(test_data)
        print("[TEST] Test data sent to Firebase.")       
    print("[TEST] Firebase connection test completed.")
    inialize()

if __name__ == "__main__":
    inialize()
else:
    print("[ERROR] This script is not meant to be imported as a module.")
    print("[ERROR] Please run it directly.")