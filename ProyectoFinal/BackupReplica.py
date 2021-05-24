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
            if (current_book.nombre == book or current_book.id_libro) and current_book.estado == 'prestado': 
                print(current_book)
                # Modify current book 
                current_book.estado = 'disponible'
                current_book.fecha_prestamo = '_'
                current_book.fecha_devolucion = '_'
                current_book.sede_prestamo = '_\n'
                print(current_book)
                # Add one to available books
                ejemplares_disponibles[current_book.id] += 1  
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
            if (current_book.nombre == book or current_book.id_libro) and current_book.estado == 'prestado': 
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
        for i in range(0, len(library)): 
            if (library[ i ].nombre == book or library[ i ].id_libro == book) and library[ i ].estado == 'disponible':
                print('Libro encontrado', library[i].nombre, library[i].id_ejemplar)
                print('Ejemplares : ', ejemplares_disponibles[library[i].id_libro])
                # Validate available books
                if ejemplares_disponibles[library[ i ].id_libro] >= 1: 
                    ejemplares_disponibles[library[ i ].id_libro] -= 1
                    library[ i ].estado = 'prestado'
                    library[ i ].fecha_prestamo = datetime.datetime.today().strftime('%y-%m-%d')
                    return_date = datetime.datetime.strptime(datetime.datetime.today().strftime('%y-%m-%d'), '%y-%m-%d') + datetime.timedelta(days=7)
                    library[ i ].fecha_devolucion = return_date.strftime('%y-%m-%d')
                    library[ i ].sede_prestamo = branch + '\n'
                    book_found = True
                    break
                else: 
                    print('No hay ejemplares disponibles')
                    book_found = True
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