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
if len(sys.argv) != 4: 
    print('Parámetros de ejecución inválidos, ejecución válida : ')
    print('python3 Proceso_Devolucion.py < DIRECCIÓN_PUB_GESTOR > < DIRECCÓN_PUB_COORDINADOR > < NÚMERO_SEDE >') 
    exit()

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

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )

#------------------------------------------------
#                 Functions
#------------------------------------------------
# This function will handle the process of returning a book 
def modifyDatabaseDistributed(book: str):
    # Open file
    data_base = open('BaseDeDatos.txt', 'r')
    # Read file 
    library = []
    line = 1
    for single_book_info in data_base: 
        # Don't read the first line
        if line == 1: 
            line += 1
            continue
        else: 
            line += 1

        # Check if current book is the one to make a return 
        book_name, book_id, authors, available_quantity = single_book_info.split(',')
        # Search by name and by id
        if book_name == book or book_id == book: 
            # Modify book data
            available_quantity = str( int(available_quantity) + 1 )
            single_book_info = book_name + ',' + book_id + ',' + authors + ',' + available_quantity + '\n'

        # Add Book to array 
        library.append(single_book_info)
    # Eof

    # Close file 
    data_base.close()



    # Override file with new data 
    data_base = open('BaseDeDatos.txt', 'w')
    data_base.write('# Nombre_libro, Id, Autor, Ejemplares_Disponibles \n')
    for single_book_info in library: 
        data_base.write(single_book_info) 
    # Close Data Base
    data_base.close()

#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__': 

    # Register process
    register_message = 'registro,devolucion,' + branch + ',' + pub_load_manager_address + ',' + pub_coordinator_address
    response = ''
    while response != 'ok': 
        register_socket.send( register_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8')
        # If response isn't ok
        if response != 'ok': 
            time.sleep( 2 )

    # Request nedded addresses
    request_message = 'peticion,devolucion,' + branch + ',' + 'coordinador:rep_processes_address,' + 'gestor_carga:pub_processes_address'
    register_socket.send( request_message.encode('utf-8') )
    response = register_socket.recv().decode('utf-8').split(',')
    print('Response :', response)

    # Socket to request to coordinator
    coordinator_address = response[0].split(' ')[1]
    req_coordinator_socket = context.socket( zmq.REQ ) 
    req_coordinator_socket.connect( f'tcp://{ coordinator_address}' )

    # Socket to subscribe to load manager
    load_manager_address = response[1].split(' ')[1]
    sub_load_manager_socket = context.socket( zmq.SUB )
    sub_load_manager_socket.connect( f'tcp://{ load_manager_address }' )
    topic_filter = 'DevolverLibro'.encode('utf-8')
    sub_load_manager_socket.subscribe( topic_filter )
    print('Load manager address : ', load_manager_address)


    print('--------------------')
    print('|    Devolución    |')
    print('--------------------')
    
    while True: 
        #----------  Wait request from 'GestorDeCarga'  ----------
        print('Esperado solicitud ... ')
        request = sub_load_manager_socket.recv().decode('utf-8')
        _, book = request.split(',')
        print('Solicitud recibida')

        #----------  Handle request  ----------- 
        print('Solicitando acceso a la Base de Datos ...')
        # Request access to DB until access granted
        coordinator_response = ''
        while coordinator_response != 'Access granted':
            req_coordinator_socket.send('Devolucion'.encode('utf-8'))
            coordinator_response = req_coordinator_socket.recv().decode('utf-8')
            print('Coordinador dice [%s]' % coordinator_response)
            # Sleep if DB is occupied and try again in 2 seconds
            if coordinator_response != 'Access granted':
                time.sleep( 2 )

        # Modify DataBase
        print('Modificando Base de Datos', end=' ... ')
        modifyDatabaseDistributed(book)
        print('Base de datos modificada')

        # Send message to coordinator to free DB resource
        print('Enviando mensaje para liberar BD ... ')
        time.sleep( 4 )
        coordinator_pub_socket.send('Free resource'.encode('utf-8'))
        print('Enviado')
        
        #----------  Reply to 'GestorDeCarga'  ----------
        print('Enviando respuesta a Gestor de carga ...')
        
        pub_load_manager_socket.send('Process finished'.encode('utf-8'))
        print('Respuesta enviada.')

    # Eow

# Eom