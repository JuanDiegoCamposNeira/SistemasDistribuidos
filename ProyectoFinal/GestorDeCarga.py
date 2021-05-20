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


#------------------------------------------------
#                Validations 
#------------------------------------------------
# Validate port passed as parameter
if len(sys.argv) != 4: 
    print('Parámetros de ejecución inválidos, ejecución válida : ')
    print('Python3 GestorDeCarga.py < DIRECCIÓN_PUB_PROCESOS > < DIRECCIÓN_CLIENTE > < NÚMERO_SEDE >')
    exit()

#------------------------------------------------
#                 Variables
#------------------------------------------------
pub_processes_address = sys.argv[1]               # Address to publish to the processes
client_address = sys.argv[2]                      # Address to communicate with the client
branch = sys.argv[3]                              # Branch number

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Ports
PUB_PROCESSES_PORT = pub_processes_address.split(':')[1]      # Port to publish to processes
CLIENT_PORT = client_address.split(':')[1]                    # Port to communicate with the client

# Context
context = zmq.Context() 

# Socket to serve the client (REQ-REP)
client_socket = context.socket( zmq.REP )          
client_socket.bind(f'tcp://*:{ CLIENT_PORT }') 
                                          
# Socket to communicate with processes (Pub-Sub)
pub_processes_socket = context.socket( zmq.PUB )          
pub_processes_socket.bind( f'tcp://*:{ PUB_PROCESSES_PORT }' )               

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )

#------------------------------------------------
#               Functions 
#------------------------------------------------
def handle_request(request_type: str, book: str) -> bool:
    # Define topic
    topic = request_type
    # Define message
    message_data = book
    # Create information string
    information = '%s,%s' % (topic, message_data)
    # Publish message
    print('Publicando mensaje ...')
    pub_processes_socket.send( information.encode('utf-8') )
    print('Publicado.')
    # Block until process response
    print('Esperando respuesta del proceso ...')
    process_response = sub_processes_socket.recv().decode('utf-8')
    print('Respuesta proceso [%s]' % process_response)
    # Return on success
    return True

#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__': 

    # Register process
    register_message = 'registro,gestor_carga,' + branch + ',' +  pub_processes_address + ',' + client_address
    response = ''
    while response != 'ok': 
        register_socket.send( register_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8')
        # If response isn't ok
        if response != 'ok': 
            time.sleep( 2 )

    # Request nedded addresses
    request_message = 'peticion,gestor_carga,' + branch + ',' + 'devolucion:pub_manager_address,' + 'renovacion:pub_manager_address,' + 'solicitud:pub_manager_address'
    register_socket.send( request_message.encode('utf-8') )
    response = register_socket.recv().decode('utf-8').split(',')

    # Configure socket that subscribes to return, request and renew processes
    sub_processes_socket = context.socket( zmq.SUB ) 
    print(response)
    for process in response: 
        address = process.split(' ')[1]
        sub_processes_socket.connect( f'tcp://{ address }')
    # Eof
    sub_processes_socket.subscribe( ''.encode('utf-8') )

    print('---------------------------------------------')
    print(f'|                Sede #{ branch }                    |')
    print('---------------------------------------------')

    # pub_processes_socket.send('DevolverLibro,algo'.encode('utf-8'))

    while True: 
        #----------   Wait for the next request   ----------
        print('Esperando solicitud de cliente ... ') 
        request = client_socket.recv().decode('utf-8') # recv() will block the process until it receives a request
        print('Recibida.')

        #-----------   Handle request   ------------
        success = False
        request_type, book = request.split(',')
        # Handle request
        success = handle_request(request_type, book) 

        #------------   Reply to client   -----------
        if not success: 
            response = 'Algo salio mal en el lado del servidor'.encode('utf-8')
        else: 
            response = 'Procedimiento terminado'.encode('utf-8')
        # Send information in socket
        print('Enviando respuesta al cliente ... ')
        client_socket.send( response )
        print('Enviada.')
    # Eow

    # Close I/O sockets
    client_socket.close()
    pub_processes_socket.close()

    # Show the user, successfull termination
    print(f'Sede { branch } finalizada correctamene.')