import network
import socket
import time
from machine import I2C, Pin
from bmp280 import BMP280
import json 

#Json
def json_config():
    with open("config.json", "rb") as f:
        json_str = f.read().decode("utf-8")
        json_file = json.loads(json_str)
        return json_file["mode"], json_file["ip_socket"], json_file["port_socket"], json_file["ssid"], json_file["password"]

#WIFI
def wifi_con():
    print(f"[WIFI] Trying connection on {ssid} with pass {password}")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)
    while not wifi.isconnected():
        pass
    print(f"[WIFI] Sucessful connection on {ssid} \n[WIFI] Your IP is: {wifi.ifconfig()}")
#----------

#SOCKET
def socket_connection():
    global s        
    print(f"[SOCKET] Connecting on {HOST}:{PORT}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except socket.gaierror:
        print("[SOCKET] Host not found")         
        return False
    except Exception as e:
        print(f"[SOCKET] Error on socket \n[SOCKET] Error: {e}")
        return False
    finally:
        print(f"[SOCKET] Connected on {HOST}:{PORT}")
        return True
    
def get_delay():
    delay = s.recv(1024)
    if not delay:
        print("[SOCKET] Delay not recived, trying again")
        time.sleep(1)
        get_delay()
    delay = delay.decode()
    delay = int(delay)
    print(f"[SOCKET] Delay {delay} recived")
    try:
        eco_delay = str(delay)
        s.sendall(eco_delay.encode())
    except Exception as e:
        print(f"[SOCKET] Error {e} on get_delay")
    finally:
        return delay


def socket_send_data(data=''):
    try: 
        s.sendall(data.encode())
        print(f"[SOCKET] Sended {data} and encoded to {data.encode()}")
    except Exception as e:
        print(f"[SOCKET] Error sending data\n[SOCKET] Error: {e}")
        print("[SOCKET] Trying to connect again")
        socket_connection()
        return None
    
def socket_test():
    print(f"[SOCKET-TEST] Running")
    wifi_con()
    socket_connection()
    try:
        socket_send_data("TEST".encode)
        time.sleep(2)
        data = s.recv(1024)
        print(f"[SOCKET-TEST] Recived: {data.decode()}")
    except Exception as e:
        print(f"[SOCKET-TEST] Something wrong happend\n[SOCKET-TEST] Error: {e}")

#----------

#bmp280 funcs
def setup_sensor():
    global bmp
    i2c = I2C(scl=Pin(22), sda=Pin(21))
    bmp = BMP280(i2c)
    bmp.oversample(3)
    bmp.use_case(1)
    print(f"[SENSOR] Sensor setup finished")

def get_sensor_values():
    temp = bmp.temperature
    pressure = bmp.pressure / 100
    temp_pressure = "{:.2f}/{:.2f}".format(temp, pressure)
    print(f"[SENSOR] Values: {temp_pressure}")
    return temp_pressure

def sensor_test():
    print(f"[SENSOR-TEST] Running")
    setup_sensor()
    try:
        for x in range(0, 16):
            print(f"[SENSOR-TEST] Turn {x}")
            get_sensor_values()
            time.sleep(1)
    except Exception as e:
        print(f"[SENSOR-TEST] Error: {e}")

#----------

#Main

def main():
    setup_sensor()
    wifi_con()
    sock_bool = socket_connection()
    print("[SETUP] Waiting for the delay")
    delay = get_delay()
    print("[SETUP] Everything succeful, starting code")
    if sock_bool:
        while True:
            try:
                values = get_sensor_values()
                socket_send_data(values)
                time.sleep(delay)
            except Exception as e:
                print(f"[MAIN] Error on main\n[MAIN] Error: {e}")

def inialize():
    global HOST, PORT, ssid, password
    mode, HOST, PORT, ssid, password = json_config()
    if mode == "main":
        main()
    elif mode == "sensor-test":
        sensor_test()
    elif mode == "socket-test":
        socket_test()

if __name__ == "__main__":
    inialize()
else:
    print("[ERROR] This script is not meant to be imported as a module.")
    print("[ERROR] Please run it directly.")
