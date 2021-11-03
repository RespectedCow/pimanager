'''
This is the server-side code for the users to view their raspberry pis.

Allowing them to check their pi's code and stuff.
'''

# Import libraries
import socket # python networking
from threading import Thread 
from src import filter
import pickle
from _thread import start_new_thread

# Classes
class Server:
    
    def __init__(self, address, port, password, serverroom):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while True:
            try:
                sock.bind((address, port))
                break
            except:
                port += 1
        serverroom.print_msg(f'hosting cave on {address}:{port}')
        
        # Define values
        self.filter = None
        self.run = False
        self.room = serverroom
        self.sock = sock
        self.ThreadCount = 0
        self.clients = set()
        self.client_data = {}
        self.password = password
        
        # Listen to port
        self.sock.listen(5)
        
    def start(self):
        self.run = True
        self.room.print_msg("Server started")
        self.room.print_msg("Cluster cave started, Looking for connections.")
        
        while self.run:
            try:
                if self.run == True:
                    Client, address = self.sock.accept()
                    
                    self.room.print_msg('Connected from: ' + address[0] + ':' + str(address[1]))
                    
                    # Check if client passcode is valid
                    passcode = pickle.loads(Client.recv(2048))
                    if passcode == self.password:
                        self.ThreadCount += 1
                        self.clients.add(Client)
                        self.room.print_msg("Client successfully logged in.")
                        self.room.print_msg('Number of connected pis: ' + str(self.ThreadCount))
                        start_new_thread(self.threaded_client, (Client, )) 
                    else:
                        self.room.print_msg("Client unsuccessfully logged in.")
                        Client.send(pickle.dumps("Permission denied."))
                        self.room.print_msg("Client kicked.")
                        Client.close()
            except BlockingIOError:
                pass

        self.sock.close()
            
    def stop(self):
        self.room.print_msg("Server stopped")
        self.run = False
        
    def threaded_client(self, connection):
        # Get the name of the pi
        name = pickle.loads(connection.recv(2048))
        self.room.print_msg("The pi's display name is " + name)
        
        clientCount = self.ThreadCount
        connection.send(pickle.dumps("Welcome to the cave, " + name))
        
        while self.run and connection:
            connection.send(pickle.dumps("Client status."))
            
            try:
                data = pickle.loads(connection.recv(4048))
            except:
                break
            if not data and self.run == False or connection == None:
                break
            data = filter.filter(data)
            
            # Append to a array or something
            self.client_data[name] = data
        
        self.room.print_msg("Connection closed.")
        self.clients.remove(connection)
        self.ThreadCount -= 1
        self.room.print_msg("Number of connected clients: " + str(self.ThreadCount))
        connection.close()
        
    def broadcast(self, message):
        for c in self.clients:
            c.send(pickle.dumps(message))
            
    def get_data(self):
        return self.client_data


# Main
def main():
    # Create a server/listen in on a port
    server = Server('192.168.0.165', 2222)
    Thread(server.start()).start()
    
    print("hey")

if __name__ == "__main__":
    main()