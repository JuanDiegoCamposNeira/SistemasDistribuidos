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
# Validate addresses passed as parameters
if len(sys.argv) != 4: 
    print('Parámetros de ejecución inválidos, ejecución válida : ')
    print('python3 BaseDeDatos.py < NÚMERO_SEDE > < DIRECCIÓN_REP_FRONTEND > < DIRECCIÓN_PUB_REPLICAS_RESPALDO >') 
    exit()

#------------------------------------------------
#                Variables 
#------------------------------------------------
branch = sys.argv[1]
rep_frontend_address = sys.argv[2]
pub_replicas_address = sys.argv[3]

library = []
ejemplares_disponibles = dict()

backup_replicas = 0

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Context
context = zmq.Context()

# Socket to receive requests from Front End
rep_frontend_socket = context.socket( zmq.REP )
rep_frontend_socket.bind( f'tcp://*:9999' )

# Socket to publish to backup replicas 
pub_replicas_socket = context.socket( zmq.PUB )
pub_replicas_socket.bind( 'tcp://*:9950' )

# Socket to subscribe to backup replicas
sub_replicas_socket = context.socket( zmq.SUB )

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )


# Read the initial state of the DataBase
data_base = open('BaseDeDatos.txt', 'r')
for single_book_info in data_base: 
    # Get book parameters 
    id_libro, id_ejemplar, nombre, autor, estado, fecha_prestamo, fecha_devolucion, sede_prestamo = single_book_info.split(',')
    # Save book
    library.append( Libro(id_libro, id_ejemplar, nombre, autor, estado, fecha_prestamo, fecha_devolucion, sede_prestamo) )

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
def handle_database_modification(operation: str, book: str, branch: str): 
    # If is a return operation
    if operation == 'devolucion':
        # Search book 
        book_found = False
        for current_book in library: 
            if (current_book.nombre == book or current_book.id_libro == book) and current_book.estado == 'prestado': 
                # Modify current book 
                current_book.estado = 'disponible'
                current_book.fecha_prestamo = '_'
                current_book.fecha_devolucion = '_'
                current_book.sede_prestamo = '_\n'
                print(current_book)
                # Add one to available books
                ejemplares_disponibles[current_book.id_libro] += 1  
                book_found = True
                break
        if not book_found: 
            print('Solicitud de devolución, libro no encontrado')
            return 'Solicitud de devolución, libro no encontrado' 
                
    # If is a renew operation 
    elif operation == 'renovacion':
        # Search book 
        book_found = False 
        for current_book in library: 
            if (current_book.nombre == book or current_book.id_libro == book) and current_book.estado == 'prestado': 
                # Modify current book 
                year, month, day = current_book.fecha_devolucion.split('-')
                fecha_devolucion = datetime.date( int(year), int(month), int(day) ).strftime('%y-%m-%d')
                fecha_devolucion = datetime.datetime.strptime(fecha_devolucion, '%y-%m-%d') + datetime.timedelta(days=7)
                current_book.fecha_devolucion = fecha_devolucion.strftime('%y-%m-%d')
                book_found = True
                break
        if not book_found: 
            print('Renovación de préstamo, libro no encontrado')
            return 'Renovación de préstamo, libro no encontrado' 

    # If is a request operation 
    elif operation == 'solicitud':
        # Search book 
        book_found = False 
        for current_book in library: 
            
            if (current_book.nombre == book or current_book.id_libro == book) and current_book.estado == 'disponible':
                print('Ejemplares : ', ejemplares_disponibles[current_book.id_libro])
                # Validate available books
                if ejemplares_disponibles[current_book.id_libro] >= 1: 
                    ejemplares_disponibles[current_book.id_libro] -= 1
                    current_book.estado = 'prestado'
                    current_book.fecha_prestamo = datetime.datetime.today().strftime('%y-%m-%d')
                    return_date = datetime.datetime.strptime(datetime.datetime.today().strftime('%y-%m-%d'), '%y-%m-%d') + datetime.timedelta(days=7)
                    current_book.fecha_devolucion = return_date.strftime('%y-%m-%d')
                    current_book.sede_prestamo = branch + '\n'
                    book_found = True
                    break
                else: 
                    print('No hay ejemplares disponibles')
                    return 'No hay ejemplares disponibles para realizar el prestamo'

        if not book_found: 
            print('Solicitud de préstamo, libro no encontrado')
            return 'Solicitud de préstamo, libro no encontrado'  


    # Override file with new data 
    data_base = open('BaseDeDatos.txt', 'w')
    # data_base.write('# Id, Nombre_Libro, Autor, Ejemplares_Disponibles \n')
    for single_book_info in library: 
        id_libro = single_book_info.id_libro
        id_ejemplar = single_book_info.id_ejemplar
        nombre = single_book_info.nombre 
        autor = single_book_info.autor
        estado = single_book_info.estado
        fecha_prestamo = single_book_info.fecha_prestamo 
        fecha_devolucion = single_book_info.fecha_devolucion  
        sede_prestamo = single_book_info.sede_prestamo  
        # Write book
        new_book = id_libro + ',' + id_ejemplar + ',' + nombre + ',' + autor + ',' + estado + ',' + str(fecha_prestamo) + ',' + str(fecha_devolucion) + ',' + sede_prestamo
        data_base.write( new_book ) 
    # Close Data Base
    data_base.close()

    # Publish message to modify DB to backup replicas   
    message = operation + ',' + book + ',' + branch
    pub_replicas_socket.send( message.encode('utf-8') )

    # Wait for all backup replicas response 
    quantity_backup_replicas = backup_replicas
    print('Esperando respuesta de [ %d ] réplicas de respaldo' % quantity_backup_replicas)
    while quantity_backup_replicas > 0: 
        message = sub_replicas_socket.recv().decode('utf-8')
        print('Replica de respaldo dice [%s]' % message)
        quantity_backup_replicas -= 1
    
    # Succesfull message
    return 'Modificación de la base de datos exitosa'


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
        operation, book, branch = frontend_req.split(',')
        # Handle operation
        message = handle_database_modification( operation, book, branch ) 

        # ---------- Reply to Front End -----------
        rep_frontend_socket.send( message.encode('utf-8') )

    # Eow

# Eom