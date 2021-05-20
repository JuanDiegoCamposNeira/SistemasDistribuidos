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
#                 TO DO 
#------------------------------------------------
# Tolerancia a fallas, qué pasa si el gestor de carga, se cae en algún momento 

#------------------------------------------------
#                Variables 
#------------------------------------------------
REQUEST_TIMEOUT = 3000 
REQUEST_RETRIES = 3
SERVER_ENDPOINT = ''

#------------------------------------------------
#                 Configurations
#------------------------------------------------
context = zmq.Context()            # Define context
socket = context.socket(zmq.REQ)   # Define socket and it's action, in this case is REQUEST 
current_socket_connection = ''     # Socket connection
is_socket_connected = False        # 

#------------------------------------------------
#               Functions 
#------------------------------------------------
# Function to print warning
def print_warning(message: str):
    print('\n* WARNING : ')
    print('* %s' % message)
    print('* ... Por favor intentelo de nuevo ... ')


# Handle the client request (return a book, renew a book loan, request a book loan)
def handle_client_request(option: str, book: str):
    request_type = option
    # Send reques to server
    request = f'{ request_type },{ book }'
    socket.send( request.encode('utf-8') )
    # Wait for server response
    print('Esperando respuesta de la sede ...')
    server_response = socket.recv().decode('utf-8')
    print('Respuesta recibida.')
    print(f'Server response ... { server_response }')


#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__': 
    # Message to discover how many branches are, and their IPv4 adress

    # Ask user for action he wants to perform 
    option = True
    while option: 
        # ------------------  Branch to make request  ------------------
        print('-----------------------------------------------------')
        print('\t Bienvenido al sistema de biblioteca ')
        print('-----------------------------------------------------')
        print('Por favor ingrese la sede a la que desea realizar la solicitud: ')
        print('0. Salir del sistema')
        print('1. Sede # 1')
        print('2. Sede # 2')
        branch = int(input('$ '))

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
            current_socket_connection = 'tcp://localhost:5551'
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
            current_socket_connection = 'tcp://localhost:5552'
            # Connect socket
            socket.connect(current_socket_connection)
        else: 
            print_warning('Sede inválida, opciones válidas: 0, 1 o 2')
            continue

        # ---------------------     Book option     ---------------------
        book = ''
        print('-------------------------------------------')
        print('¿Cómo desea ingresar el libro, Id o nombre?')
        print('-------------------------------------------')
        print('0. Salir del sistema')
        print('1. Id')
        print('2. Nombre')
        book_option = int(input('$ '))

        if book_option == 0: 
            option = False
            continue 
        elif book_option == 1: 
            book = input('Digite el id del libro : ')
            # Validate Id
            pattern = r'^[0-9]{3}$'
            is_id_valid = re.fullmatch(pattern, book)
            if is_id_valid == None: 
                print('Id no valido, Id Libro consiste de 3 dígitos')
                continue
        elif book_option == 2: 
            book = input('Ingrese el nombre del libro : ')
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
        option = int(input('$ '))

        # Validate user's input action
        if not option or option == 0: 
            option = False
            print('Ha salido del sistema correctamente')
            continue
    
        if option == 1:
            handle_client_request('PrestamoLibro', book)
        elif option == 2: 
            handle_client_request('RenovarLibro', book)
        elif option == 3:
            handle_client_request('DevolverLibro', book)
        else: 
            print_warning('Opción no valida, las únicas opciones válidas son 0, 1, 2 o 3')
            continue

    # Eow

    # Say goodbye to user
    print('Ha salido con éxito del sistema')

    # Close sockets and destroy context
    socket.close()

# Eom