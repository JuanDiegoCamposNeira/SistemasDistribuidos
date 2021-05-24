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
if len(sys.argv) != 3: 
    print('Parámetros de ejecución inválidos, ejecución válida : ')
    print('python3 BaseDeDatos.py < NÚMERO_SEDE > < DIRECCIÓN_PUB_RÉPLICA_PRIMARIA >') 
    exit()

#------------------------------------------------
#                Variables 
#------------------------------------------------
branch = sys.argv[1]
pub_primary_replica_address = sys.argv[2]

library = []
ejemplares_disponibles = dict()

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
    # Save book
    library.append( Libro(id_libro, id_ejemplar, nombre, autor, estado, loan_date, return_date, sede_prestamo) )

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
        for current_book in library: 
            if (current_book.nombre == book or current_book.id_libro) and current_book.estado == 'prestado': 
                print(current_book)
                # Modify current book 
                current_book.estado = 'disponible'
                current_book.fecha_prestamo = '_'
                current_book.fecha_devolucion = '_'
                current_book.sede = '_'
                print(current_book)
                # Add one to available books
                ejemplares_disponibles[current_book.id] += 1  
                break
                
    # If is a renew operation 
    elif operation == 'renovacion':
        # Search book 
        for current_book in library: 
            if (current_book.nombre == book or current_book.id_libro) and current_book.estado == 'prestado': 
                print(current_book)
                # Modify current book 
                fecha_devolucion = current_book.fecha_devolucion
                fecha_devolucion = datetime.datetime.strptime(fecha_devolucion, '%y/%m/%d') + datetime.timedelta(days=7)
                current_book.fecha_devolucion = fecha_devolucion
                print(current_book)
                break

    # If is a request operation 
    elif operation == 'solicitud':
        # Search book 
        for current_book in library: 
            if current_book.nombre == book or current_book.id_libro:
                # Validate available books
                if ejemplares_disponibles[current_book.id] >= 1: 
                    ejemplares_disponibles[current_book] -= 1
                    current_book.estado = 'prestado'
                    current_book.fecha_prestamo = datetime.datetime.today().strftime('%y%m%d')
                    current_book.fecha_devolucion = datetime.datetime.strptime(current_book.fecha_prestamo, '%y/%m/%d') + datetime.timedelta(days=7) 
                    current_book.sede = branch
                else: 
                    return 'No hay ejemplares disponibles para realizar el prestamo'


    # Override file with new data 
    data_base = open('BaseDeDatos.txt', 'w')
    data_base.write('# Id, Nombre_Libro, Autor, Ejemplares_Disponibles \n')
    for single_book_info in library: 
        id_libro = single_book_info.id_libro
        id_ejemplar = single_book_info.id_ejemplar
        nombre = single_book_info.nombre 
        autor = single_book_info.autor
        estado = single_book_info.estado
        fecha_prestamo = single_book_info.fecha_prestamo 
        fecha_devolucion = single_book_info.fecha_prestamo  
        sede_prestamo = single_book_info.sede_prestamo  
        
        # Write book
        new_book = id_libro + ',' + id_ejemplar + ',' + nombre + ',' + autor + ',' + estado + ',' + str(fecha_prestamo) + ',' + str(fecha_devolucion) + ',' + sede_prestamo
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
        operation, book, branch = primary_replica_message.split(',')
        # Handle operation
        print('Modificando base de datos ...')
        message = handle_database_modification( operation, book, branch ) 
        print('Base de datos modificada.')

        # ----- Publish message to primary replica -----
        print('Enviando respuesta a la réplica primaria ...')
        # print(pub_primary_replica_address)
        time.sleep( 1 )
        pub_primary_replica_socket.send(message.encode('utf-8'))

    # Eow
# Eom