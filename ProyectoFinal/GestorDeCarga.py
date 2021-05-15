"""
    Authors: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""
#------------------------------------------------
#                 Libraries
#------------------------------------------------
import time
import zmq
import sys

from zmq.sugar.constants import PUB

#------------------------------------------------
#                Validations 
#------------------------------------------------
# Validate port passed as parameter
if len(sys.argv) != 4: 
    print('Parámetros de ejecución inválidos, ejecución válida : ')
    print('\t Python3 GestorDeCarga.py < PUERTO_CLIENTES > < PUERTO_PUB > < NÚMERO_SEDE >')
    exit()


#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Define ZMQ context
context = zmq.Context() 

# Socket to serve the client (REQ-REP)
CLIENT_PORT = sys.argv[1]                        # Get port from arguments 
client_socket = context.socket(zmq.REP)          # Define socket and it's action
client_socket.bind(f'tcp://*:{ CLIENT_PORT }')   # Bind socket to an IPv4 address to reply
                                                 #   In this case, the server will reply to all requests 
                                                 #   because of the '*' in the IPv4 adress
                                          
# Socket to communicate with processes (Pub-Sub)
PUB_PORT = sys.argv[2]                          # Get port from arguments 
pub_socket = context.socket(zmq.PUB)            # Define PUB socket
pub_socket.bind(f'tcp://*:{ PUB_PORT }')        # Bind socket to an IPv4 address to reply
                                                #   In this case, the server will reply to all requests 
                                                #   because of the '*' in the IPv4 adress 


#------------------------------------------------
#               Functions 
#------------------------------------------------
def handle_request(request_type: str, book: str) -> bool:
    # Define topic
    topic = request_type
    # Define message
    message_data = book 
    # Publish message
    pub_socket.send(topic, message_data)
    # Return on success
    return True

#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__': 
    print('---------------------------------------------')
    print(f'|                Sede #{ sys.argv[3] }                    |')
    print('---------------------------------------------')
    while True: 
        #----------   Wait for the next request   ----------
        print('Esperando solicitud de cliente ...') 
        request = client_socket.recv() # recv() will block the process until it receives a request
        print('Solicitud de cliente recibida.')

        #-----------   Handle request   ------------
        success = False
        request_type, book = request.split(',')
        # Check if message is to kill process
        if request_type == 'kill': 
            break 
        # Handle request
        success = handle_request(request_type, book)

        #------------   Reply to client   -----------
        if not success: 
            response = 'Algo salio mal en el lado del servidor'
        else: 
            response = 'Procedimiento terminado'
        # Send information in socket
        client_socket.send(bytes( response, 'utf-8'))
    # Eow

    # Close I/O sockets
    client_socket.close()
    pub_socket.close()

    # Show the user, successfull termination
    print(f'Sede { sys.argv[3] } finalizada correctamene.')