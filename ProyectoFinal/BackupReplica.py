"""
    Authors: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""

#------------------------------------------------
#                 Libraries
#------------------------------------------------
import sys
import time
import zmq

#------------------------------------------------
#                 Classes
#------------------------------------------------
class Libro:
    def __init__(self, _id = 0, name = '', authors = '', avaiable_quantity = 0):
        self.id = _id
        self.name = name
        self.authors = authors
        self.available_quantity = avaiable_quantity

#------------------------------------------------
#                Validations 
#------------------------------------------------
# # Validate addresses passed as parameters
# if len(sys.argv) != 3: 
#     print('Parámetros de ejecución inválidos, ejecución válida : ')
#     print('python3 BaseDeDatos.py < NÚMERO_SEDE > < DIRECCIÓN_PUB_RÉPLICA_PRIMARIA >') 
#     exit()

#------------------------------------------------
#                Variables 
#------------------------------------------------
branch = sys.argv[1]
pub_primary_replica_address = sys.argv[2]
library_database = []

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Ports
PUB_PRIMARY_REPLICA_PORT = pub_primary_replica_address.split(':')[1]

# Context
context = zmq.Context()

# Socket to subscribe to primary replica
sub_primary_replica_socket = context.socket( zmq.SUB )

# Socket to publish to primary replica
pub_primary_replica_socket = context.socket( zmq.PUB ) 
pub_primary_replica_socket.bind( f'tcp://*:{ PUB_PRIMARY_REPLICA_PORT }' )

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )

# Read the initial state of the DataBase
# Inser dummy book
library_database.append( Libro() )
# Open file
data_base = open('BaseDeDatos.txt', 'r')
# Read file 
line = 1 # This is used as an index too 
for single_book_info in data_base: 
    # Don't read the first line
    if line == 1: 
        line += 1
        continue
    else: 
        line += 1
    # Save book  
    book_id, book_name, authors, available_quantity = single_book_info.split(',')
    library_database.append( Libro(book_id, book_name, authors, available_quantity) )
# Eof

#------------------------------------------------
#                 Functions
#------------------------------------------------
def handle_database_modification(operation: str, book: str): 

        # Check if book is id or name
    id_search = False
    if len(book) == 3: 
        id_search = True 

    if operation == 'devolucion':
        if id_search: 
            book_id = int( book )
            library_database[ book_id ].available_quantity = int(library_database[ book_id ].available_quantity) + 1
            library_database[ book_id ].available_quantity = str(library_database[ book_id ].available_quantity) + '\n'
            print(library_database[ book_id ].name)
        else: 
            for i in range(0, len(library_database)): 
                if library_database[ i ].name == book:
                    library_database[ i ].available_quantity = int(library_database[ i ].available_quantity) + 1
                    library_database[ i ].available_quantity += '\n'

    elif operation == 'renovacion':
        if id_search: 
            pass
        else: 
            pass

    elif operation == 'solicitud':
        if id_search: 
            book_id = int( book ) 
            if int(library_database[ book_id ].available_quantity) >= 1: 
                library_database[ book_id ].available_quantity = int(library_database[ book_id ].available_quantity) - 1
                library_database[ book_id ].available_quantity = str(library_database[ book_id ].available_quantity) + '\n'
            else: 
                print('Cantidad de ejemplares insuficientes.')
        else: 
            for i in range(0, len(library_database)): 
                if library_database[ i ].name == book:
                    if library_database[ i ].available_quantity >= 1: 
                        library_database[ book_id ].available_quantity = int(library_database[ book_id ].available_quantity) - 1
                        library_database[ book_id ].available_quantity = str(library_database[ book_id ].available_quantity) + '\n'
                    else: 
                        print('Cantidad de ejemplares insuficientes.')

    # Override file with new data 
    data_base = open('BaseDeDatos.txt', 'w')
    data_base.write('# Id, Nombre_Libro, Autor, Ejemplares_Disponibles \n')
    for single_book_info in library_database: 
        book_name = single_book_info.name
        book_id = single_book_info.id
        authors = single_book_info.authors
        available_quantity = single_book_info.available_quantity
        # Don't write first book 
        if book_id == 0: 
            continue
        # Otherwise, write book
        new_book = str(book_id) + ',' + book_name + ',' + authors + ',' + str(available_quantity)
        data_base.write( new_book ) 
    # Close Data Base
    data_base.close()


#------------------------------------------------
#                   Main 
#------------------------------------------------
if __name__ == '__main__':

    # Register process 
    register_message = 'registro,replica_respaldo,' + branch + ',' + pub_primary_replica_address
    response = ''
    while response != 'ok': 
        register_socket.send( register_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8')
        # If response isn't ok
        if response != 'ok': 
            time.sleep( 2 )

    # Request nedded addresses
    request_message = 'peticion,replica_respaldo,' + branch + ',' + 'replica_primaria:pub_replicas_address'
    register_socket.send( request_message.encode('utf-8') )
    response = register_socket.recv().decode('utf-8').split(',')
    print('Response :', response)

    # Connect socket to subscribe to primary replica
    address = response[0].split(' ')[1]
    sub_primary_replica_socket.connect( f'tcp://{ address }' )
    sub_primary_replica_socket.subscribe(''.encode('utf-8'))

    print('---------------------')
    print('|  Réplica respaldo |')
    print('---------------------')

    while True: 
        # ----- Wait for an update from Primary replica -------
        print('Esperando actualización del manejador principal ...')
        primary_replica_message = sub_primary_replica_socket.recv().decode('utf-8')
        print(primary_replica_message)

        # Get request parameters
        operation, book = primary_replica_message.split(',')
        # Handle operation
        print('Modificando base de datos ...')
        # time.sleep(5)
        handle_database_modification( operation, book ) 
        print('Base de datos modificada.')

        # ----- Publish message to primary replica -----
        print('Enviando respuesta a la réplica primaria ...')
        print(pub_primary_replica_address)
        time.sleep( 1 )
        pub_primary_replica_socket.send('ok'.encode('utf-8'))

    # Eow
# Eom