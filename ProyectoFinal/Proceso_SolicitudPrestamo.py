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
#                 TO DO 
#------------------------------------------------
# Tolerancia a fallas, qué pasa si el gestor de carga, se cae en algún momento 


#------------------------------------------------
#                Validations 
#------------------------------------------------
# Validate addresses passed as parameters
# if len(sys.argv) != 4: 
#     print('Parámetros de ejecución inválidos, ejecución válida : ')
#     print('python3 Proceso_Devolucion.py < DIRECCIÓN_PUB_GESTOR > < DIRECCÓN_PUB_COORDINADOR > < NÚMERO_SEDE >') 
#     exit()

#------------------------------------------------
#                 Variables
#------------------------------------------------
pub_load_manager_address = sys.argv[1]
pub_coordinator_address = sys.argv[2]
branch = sys.argv[3] 

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Ports
PUB_LOAD_MANAGER_PORT = pub_load_manager_address.split(':')[1]   # Port to publish to Load Manager
PUB_COORDINATOR_PORT = pub_coordinator_address.split(':')[1]     # Port to publish to coordinator

# CONTEXT
context = zmq.Context()                                             # Define context  

# Socket to publish to coordinator
coordinator_pub_socket = context.socket( zmq.PUB ) 
coordinator_pub_socket.bind( f'tcp://*:{ PUB_COORDINATOR_PORT }' )

# Socket to publish to load manager
pub_load_manager_socket = context.socket( zmq.PUB )
pub_load_manager_socket.bind( f'tcp://*:{ PUB_LOAD_MANAGER_PORT }' )

# Socket to request to primary replica manager
primary_replica_address = '25.0.228.65:9999'
req_primary_replica_socket = context.socket( zmq.REQ )
req_primary_replica_socket.connect( f'tcp://{ primary_replica_address }' ) 

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )

#------------------------------------------------
#                 Functions
#------------------------------------------------

#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__': 

    # Register process
    register_message = 'registro,solicitud,' + branch + ',' + pub_load_manager_address + ',' + pub_coordinator_address
    response = ''
    while response != 'ok': 
        register_socket.send( register_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8')
        # If response isn't ok
        if response != 'ok': 
            time.sleep( 2 )

    # Request nedded addresses
    request_message = 'peticion,solicitud,' + branch + ',' + 'coordinador:rep_processes_address,' + 'gestor_carga:pub_processes_address'
    register_socket.send( request_message.encode('utf-8') )
    response = register_socket.recv().decode('utf-8').split(',')

    # Socket to request to coordinator
    coordinator_address = response[0].split(' ')[1]
    req_coordinator_socket = context.socket( zmq.REQ ) 
    req_coordinator_socket.connect( f'tcp://{ coordinator_address}' )

    # Socket to subscribe to load manager
    sub_load_manager_socket = context.socket( zmq.SUB )
    # Subscribe to primary Load manager
    load_manager_address = response[1].split(' ')[1]
    sub_load_manager_socket.connect( f'tcp://{ load_manager_address }' )
    # Subscribe to backup load manager
    backup_load_manager_address = '25.0.228.65:2999'
    sub_load_manager_socket.connect( f'tcp://{ backup_load_manager_address }' )
    # Filter messages 
    topic_filter = 'PrestamoLibro'.encode('utf-8')
    sub_load_manager_socket.subscribe( topic_filter )


    print('--------------------')
    print('|     Solicitud     |')
    print('--------------------')

    while True: 
        #---------------  Wait for request from 'GestorDeCarga'  ---------------
        print('Esperado solicitud ... ')
        request = sub_load_manager_socket.recv().decode('utf-8')
        _, book = request.split(',')
        print('Solicitud recibida')

        #---------------  Handle request  ---------------
        print('Solicitando acceso a la Base de Datos ...')
        # Request access to DB until access granted
        coordinator_response = ''
        while coordinator_response != 'Access granted':
            req_coordinator_socket.send('Prestamo'.encode('utf-8'))
            coordinator_response = req_coordinator_socket.recv().decode('utf-8')
            print('Cordinador dice [%s]' % coordinator_response)
            # Sleep if DB is occupied and try again in 2 seconds
            if coordinator_response != 'Access granted':
                time.sleep( 2 )

        # Modify DataBase
        print('Enviando solicitud a réplica primaria ...')
        # modifyDatabaseDistributed(book)
        # book = '12'
        message = 'solicitud,' + book
        req_primary_replica_socket.send( message.encode('utf-8') )
        print('Envidada.')
        print('Esperando respuesta de réplica primaria ...')
        response = req_primary_replica_socket.recv().decode('utf-8')
        print('Respuesta recibida [%s]' % response)

        # Send message to coordinator to free DB resource
        print('Enviando mensaje para liberar BD ... ')
        coordinator_pub_socket.send('Free resource'.encode('utf-8'))
        print('Enviado')

        #---------------  Reply to 'GestorDeCarga'  ---------------
        print('Enviando respuesta a Gestor de carga ...')
        pub_load_manager_socket.send('Process finished'.encode('utf-8'))
        print('Respuesta enviada.')
        
    # Eow

    # Destroy sockets and context
    coordinator_pub_socket.close()

# Eom