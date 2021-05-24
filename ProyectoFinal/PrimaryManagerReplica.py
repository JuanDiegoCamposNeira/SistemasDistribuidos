"""
    Authors: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""
"""
    DataBase: 
        
        This process will be in charge of management of the Database and it's replicas.
        
        Algorithm used to manage replicas : Passive replication, where the FRONT END will be 
        Return_Book, Renew_Loan and Request_Loan processes and there will be a PRIMARY REPLICA MANAGER
        and also it's backups.

            * Front End : Return_Book, Renew_Loan and Request_Loan
            * Primary Replica Manager : 1 
            * Backups : 3 

        Protocol used to communicate between Primary Replica and Backups : REQ - REP
        Protocol used to communicate between Front End and Primary Replica : REQ - REP  
"""
#------------------------------------------------
#                 Libraries
#------------------------------------------------
import sys
import time
import zmq
import datetime

#------------------------------------------------
#                 Classes
#------------------------------------------------
class Libro:
    def __init__(self, id_libro, id_ejemplar, nombre, autor, estado, fecha_prestamo, fecha_devolucion, sede_prestamo):
        self.id_libro = id_libro
        self.id_ejemplar = id_ejemplar
        self.nombre = nombre
        self.autor = autor
        self.estado = estado 
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = fecha_devolucion
        self.sede_prestamo = sede_prestamo 

#------------------------------------------------
#                Validations 
#------------------------------------------------
# # # Validate addresses passed as parameters
# if len(sys.argv) != 4: 
#     print('Parámetros de ejecución inválidos, ejecución válida : ')
#     print('python3 BaseDeDatos.py < NÚMERO_SEDE > < DIRECCIÓN_REP_FRONTEND > < DIRECCIÓN_PUB_REPLICAS_RESPALDO >') 
#     exit()

# #------------------------------------------------
# #                Variables 
# #------------------------------------------------
# branch = sys.argv[1]
# rep_frontend_address = sys.argv[2]
# pub_replicas_address = sys.argv[3]

database_book_id = dict()
database_book_name = dict()
ejemplares_disponibles = dict()

backup_replicas = 0

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# # Context
# context = zmq.Context()

# # Socket to receive requests from Front End
# rep_frontend_socket = context.socket( zmq.REP )
# rep_frontend_socket.bind( f'tcp://*:9999' )

# # Socket to publish to backup replicas 
# pub_replicas_socket = context.socket( zmq.PUB )
# pub_replicas_socket.bind( 'tcp://*:9950' )

# # Socket to subscribe to backup replicas
# sub_replicas_socket = context.socket( zmq.SUB )

# # Socket to register process
# register_socket = context.socket( zmq.REQ )
# register_socket.connect( 'tcp://25.0.228.65:6000' )


# Read the initial state of the DataBase
# Open file
data_base = open('BaseDeDatos.txt', 'r')
# Read file 
line = 1
for single_book_info in data_base: 
    # Don't read the first line
    if line == 1: 
        line += 1
        continue
    else: 
        line += 1

    # Get book parameters 
    id_libro, id_ejemplar, nombre, autor, estado, fecha_prestamo, fecha_devolucion, sede_prestamo = single_book_info.split(',')
    # Create dates if book available
    loan_date = fecha_prestamo 
    return_date = fecha_devolucion
    if estado == 'prestado': 
        fecha_prestamo = fecha_prestamo.split('-')
        loan_date = datetime.datetime(int(fecha_prestamo[0]), int(fecha_prestamo[1]), int(fecha_prestamo[2]))
        fecha_devolucion = fecha_devolucion.split('-')
        return_date = datetime.datetime(int(fecha_devolucion[0]), int(fecha_devolucion[1]), int(fecha_devolucion[2]))
    # Save book by id
    database_book_id[id_libro] = Libro(id_libro, id_ejemplar, nombre, autor, estado, loan_date, return_date, sede_prestamo)
    # Save book by name 
    database_book_name[nombre] = Libro(id_libro, id_ejemplar, nombre, autor, estado, loan_date, return_date, sede_prestamo) 

    # If book isn't available, continue
    if estado == 'prestado': 
        continue

    # Otherwise, save the 'ejemplar'
    if not id_libro in ejemplares_disponibles:
        ejemplares_disponibles[id_libro] = 1
    else: 
        ejemplares_disponibles[id_libro] += 1

# Eof

#------------------------------------------------
#                 Functions
#------------------------------------------------
def handle_database_modification(operation: str, book: str): 
    # Search book 
    name = False
    id = False
    if book in database_book_name: 
        name = True
    else: 
        id = True

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
                    library_database[ i ].available_quantity = str(library_database[ i ].available_quantity) + '\n'

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
                    if int(library_database[ i ].available_quantity) >= 1: 
                        library_database[ i ].available_quantity = int(library_database[ i ].available_quantity) - 1
                        library_database[ i ].available_quantity = str(library_database[ i ].available_quantity) + '\n'
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

    # Publish message to modify DB to backup replicas   
    message = operation + ',' + book
    pub_replicas_socket.send( message.encode('utf-8') )

    # Wait for all backup replicas response 
    quantity_backup_replicas = backup_replicas
    print('Esperando respuesta de [ %d ] réplicas de respaldo' % quantity_backup_replicas)
    while quantity_backup_replicas > 0: 
        message = sub_replicas_socket.recv().decode('utf-8')
        print('Replica de respaldo dice [%s]' % message)
        quantity_backup_replicas -= 1


def request_needed_addresses(): 
    # Request nedded addresses
    request_message = 'peticion,replica_primaria,' + branch + ',' + 'replica_respaldo:pub_primary_replica_address'
    register_socket.send( request_message.encode('utf-8') )
    response = register_socket.recv().decode('utf-8').split(',')
    print('Response :', response)

    # Connect socket to request to backup replicas
    print(response)
    number_of_backups = 0 
    for process in response: 
        address = process.split(' ')[1] 
        # If no address, continue
        if address == '': 
            continue
        print('PROCESS : ', process)
        # Otherwise, connect to subs socket
        sub_replicas_socket.connect( f'tcp://{ address }')
        sub_replicas_socket.subscribe( ''.encode('utf-8') )
        # Add to backup replicas 
        number_of_backups += 1

    global backup_replicas 
    backup_replicas = number_of_backups
    print(backup_replicas)

#------------------------------------------------
#                   Main 
#------------------------------------------------
if __name__ == '__main__':

    # Register process 
    register_message = 'registro,replica_primaria,' + branch + ',' + rep_frontend_address + ',' + pub_replicas_address
    response = ''
    while response != 'ok': 
        register_socket.send( register_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8')
        # If response isn't ok
        if response != 'ok': 
            time.sleep( 2 )


    print('---------------------')
    print('|  Réplica primaria |')
    print('---------------------')

    while True: 

        print('Esperando solicitud de Front End ...') 
        # -------- Wait for Front End request ----------
        # Request examples : 
        #       - renovacion,< id_libro / nombre_libro > 
        #       - devolucion,< id_libro / nombre_libro >
        #       - solicitud,<  id_libro / nombre_libro >  

        frontend_req = rep_frontend_socket.recv().decode('utf-8')
        print( 'Solicitud recibida [%s]' % frontend_req )
        # Request needed addresses
        print('Solicitando, direcciones necesarias...')
        request_needed_addresses()
        print('Terminado.')
        # Get request parameters
        operation, book = frontend_req.split(',')
        # Handle operation
        handle_database_modification( operation, book ) 

        # ---------- Reply to Front End -----------
        rep_frontend_socket.send('ok'.encode('utf-8'))

    # Eow

# Eom