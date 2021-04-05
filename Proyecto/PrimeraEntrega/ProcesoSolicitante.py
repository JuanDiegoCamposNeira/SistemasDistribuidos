"""
    Autores: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""

"""-----------------------------------------------
----------    Proceso solicitante    ------------- 
-----------------------------------------------"""

import zmq

# Library configurations
context = zmq.Context() # Get the context 
socket = context.socket(zmq.REQ) # This line sets the socket to be a REQUEST socket
socket.connect("tcp://25.114.38.38:5555") # This line tells the socket to connect to the address ... and port

def read_requests(): 
    # Open file 
    requests = open("Peticiones.txt", "r")
    # Traverse request file 
    for request in requests: 
        print(request)
        # Send the message trhu the socket 
        socket.send(bytes(request, 'utf-8'))
        # Wait for the server response 
        server_reply = socket.recv()
        # Print server reply
        print(f"Reply recived {server_reply}")
    # Eof
    # Close file 
    requests.close()

# Main 
if __name__ == "__main__":
    # Read all requests from file 
    read_requests()