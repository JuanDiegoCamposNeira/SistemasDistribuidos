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
import re

#------------------------------------------------
#                Variables 
#------------------------------------------------
REQUEST_TIMEOUT = 10000 
REQUEST_RETRIES = 3
# Branches IP address
branches = [ '-1', '25.0.228.65', '25.114.38.38' ]
# Addressed from load managers
load_managers_addresses = [ '-1', [], [] ]
# Load managers, branch 1
load_managers_addresses[1].append( branches[1] + ':5551' ) # Primary load manager
load_managers_addresses[1].append( branches[1] + ':5550' ) # Backup load manager
# Load managers, branch 2
load_managers_addresses[2].append( branches[2] + ':5551' ) # Primary load manager
load_managers_addresses[2].append( branches[2] + ':5550' ) # Backup load manager

current_socket_connection = ''     # Socket connection
is_socket_connected = False        # 

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Context
context = zmq.Context()            # Define context

# Socket to communicate with branches (load managers)
socket = context.socket( zmq.REQ )   # Define socket and it's action, in this case is REQUEST 
socket.RCVTIMEO = REQUEST_TIMEOUT     # Set max limit to wait for a response 

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )

#------------------------------------------------
#               Functions 
#------------------------------------------------
# Function to print warning
def print_warning(message: str):
    print('\n* WARNING : ')
    print('* %s' % message)
    print('* ... Por favor intentelo de nuevo ... ')

# Handle the client request (return a book, renew a book loan, request a book loan)
def handle_client_request(option: str, book: str, branch: int, current_socket_connection: str):
    # Construct request 
    request_type = option
    request = f'{ request_type },{ book }'
    # Try send request to every load manager
    server_response = ''
    global socket
    try: 
        # Send request to server
        socket.send( request.encode('utf-8') )
        print('Esperando respuesta de la sede ...')
        # Wait for server response
        server_response = socket.recv().decode('utf-8')
    except zmq.ZMQError as e: 
        print('ERROR: ', e)
        print('Error enviando al Gestor de carga, intentando con otro ... ')
        # Disconnect to current connection 
        # socket.disconnect( current_socket_connection )
        socket.close()
        # Create new socket
        socket = context.socket( zmq.REQ )
        # Connect to the new load manager
        current_socket_connection = f'tcp://{ load_managers_addresses[branch][1] }'
        socket.connect( current_socket_connection )
        # Send request to new load manager
        socket.send( request.encode('utf-8') )
        # # Wait for new load manager reponse
        server_response = socket.recv().decode('utf-8')

    print('Respuesta recibida.')
    print(f'Server response ... { server_response }')
    return current_socket_connection

#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__': 
    #------  Discover how many branches are  -------
    # message = 'peticion,cliente,' + '1' + 'sedes:all'
    # register_socket.send( message.encode('utf-8') )
    # response = register_socket.recv().decode('utf-8')
    # print('BRANCHES : ', response)

    # Read client input
    client_input = open('peticiones_cliente.txt', 'r')

    # Ask user for action he wants to perform 
    option = True
    for input in client_input:  
    # while option:
        branch, book_option, book, option = input.split(',')
        branch = int(branch)
        book_option = int(book_option)
        option = int(option) 
        # ------------------  Branch to make request  ------------------
        print('-----------------------------------------------------')
        print('\t Bienvenido al sistema de biblioteca ')
        print('-----------------------------------------------------')
        print('Por favor ingrese la sede a la que desea realizar la solicitud: ')
        print('0. Salir del sistema')
        print('1. Sede # 1')
        print('2. Sede # 2')
        # branch = int(input('$ '))
        # branch = client_input.read()

        # Connect the socket to the corresponding IPv4 branch 
        if branch == 0: 
            option = False
            continue
        elif branch == 1: 
            # Connect socket to branch # 1
            # If socket is already connected, disconnect it 
            if is_socket_connected: 
                socket.disconnect(current_socket_connection) 
            else: 
                is_socket_connected = True 
            # Save connection
            current_socket_connection = f'tcp://{ load_managers_addresses[1][0] }'
            # Connect socket 
            socket.connect(current_socket_connection)
        elif branch == 2: 
            # Connect socket to branch # 2
            # If socket is already connected, disconnect it 
            if is_socket_connected: 
                socket.disconnect(current_socket_connection) 
            else: 
                is_socket_connected = True 
            # Save connection
            current_socket_connection = f'tcp://{ load_managers_addresses[2][0] }'
            # Connect socket
            socket.connect(current_socket_connection)
        else: 
            print_warning('Sede inválida, opciones válidas: 0, 1 o 2')
            continue

        # ---------------------     Book option     ---------------------
        # book = ''
        print('-------------------------------------------')
        print('¿Cómo desea ingresar el libro, Id o nombre?')
        print('-------------------------------------------')
        print('0. Salir del sistema')
        print('1. Id')
        print('2. Nombre')
        # book_option = int(input('$ '))
        # book_option = client_input.read()

        if book_option == 0: 
            option = False
            continue 
        elif book_option == 1: 
            # book = input('Digite el id del libro : ')
            # Validate Id
            # pattern = r'^[0-9]{3}$'
            # is_id_valid = re.fullmatch(pattern, book)
            # if is_id_valid == None: 
            #     print('Id no valido, Id Libro consiste de 3 dígitos')
            #     continue
            pass
        elif book_option == 2: 
            # book = input('Ingrese el nombre del libro : ')
            pass
        else: 
            print_warning('Opción no valida, las únicas posibles opciones son 0, 1 o 2')
            continue

        # ---------------------     User option     ---------------------
        print('------------------------')
        print('¿Qué desea realizar hoy?')
        print('------------------------')
        print('0. Salir del sistema')
        print('1. Solicitar el prestamo de un libro')
        print('2. Renovar el prestamo de un libro')
        print('3. Devolver un libro')
        # option = int(input('$ '))
        # option = client_input.read()

        # Validate user's input action
        if not option or option == 0: 
            option = False
            print('Ha salido del sistema correctamente')
            continue
    
        book = str(book)
        branch = int(branch)
        print('LIBRO [ %s ] BRANCH [ %d ] ' % ( book, branch ))
        if option == 1: 
            current_socket_connection = handle_client_request('PrestamoLibro', book, branch, current_socket_connection)
        elif option == 2: 
            current_socket_connection = handle_client_request('RenovarLibro', book, branch, current_socket_connection)
        elif option == 3:
            current_socket_connection = handle_client_request('DevolverLibro', book, branch, current_socket_connection)
        else: 
            print_warning('Opción no valida, las únicas opciones válidas son 0, 1, 2 o 3')
            continue

    # Eow

    # Say goodbye to user
    print('Ha salido con éxito del sistema')

    # Close sockets and destroy context
    socket.close()

# Eom