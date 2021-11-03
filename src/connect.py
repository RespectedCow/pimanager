import socket, pickle
import threading
from gpiozero import CPUTemperature
import psutil

# Get address and port
address = input("What is the ip address of the manager(LAN)? ")
port = input("What is the port? ")

# Start connection
mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysocket.connect((address, int(port)))

# Handle protocols
password = input("What is the passcode for the manager? ")
mysocket.send(pickle.dumps(password))

name = input("What name do you want this pi to have? Make sure it is unique or it will overwrite other pi's data: ")
mysocket.send(pickle.dumps(name))

while True:
    try:
        data = pickle.loads(mysocket.recv(2046))   
    except:
        pass
    else:
        print(data)
        
        cpu = CPUTemperature()
        
        data_to_send = {}
        
        # Temperature
        data_to_send['temp'] = str(cpu.temperature()) + "'C"
        
        # CPU usage
        data_to_send['cpu_usage'] = str(psutil.cpu_percent(1)) + "%"

        # Ram usage
        data_to_send['ram_usage'] = str(psutil.virtual_memory()[2]) + "%"
        
        if data == "Client status.":
            mysocket.send(pickle.dumps(data_to_send))
        if data == "Permission denied.":
            break