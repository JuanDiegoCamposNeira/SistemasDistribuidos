"""
    Authors: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""
"""
    Coordinator: 

        This is the coordinator that guarantees mutex (Mutual Exclution).
        All 3 processes (ReturnBook, RenewLoan, RequestLoan) will request 
        the access to the DataBase. 
        If a process request the DB and no other process is in the DB, the
        access will be granted, but in the case that a process request the
        access to the DB and there is already a process in the DB, the 
        request will be queued and the requested process will block until 
        the response from the coordinator arrives.

        Protocol used to request acces to DB : REQ - REP
        Protocol used to free the DB : PUB - SUB
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
# if len(sys.argv) != 2: 
#     print('Parámetros de ejecución inválidos, ejecución válida : ')
#     print('\t Python3 Coordinador.py')
#     exit()

#------------------------------------------------
#                  Variables 
#------------------------------------------------
is_db_occupied = False

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Ports
REP_PROCESSES_PORT = '4000' 

# Address
rep_processes_address = f'25.0.228.65:{ REP_PROCESSES_PORT }'

# Context
context = zmq.Context()                    

# Socket to receive processes requests (Return, RenewLoan, RequestLoan) 
rep_processes_socket = context.socket( zmq.REP )  
rep_processes_socket.bind( f'tcp://*:{ REP_PROCESSES_PORT }' )   

# Socket to register process
register_socket = context.socket( zmq.REQ )
register_socket.connect( 'tcp://25.0.228.65:6000' )

#------------------------------------------------
#                   Main 
#------------------------------------------------
if __name__ == '__main__': 

    # Register process ... registro,coordinador,<dummy_branch>,<rep_process_address>
    register_message = 'registro,coordinador,' + '122' + ',' +  rep_processes_address
    response = ''
    while response != 'ok': 
        register_socket.send( register_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8')
        # If response isn't ok
        if response != 'ok': 
            time.sleep( 2 )
    
    # Socket to subscribe to all processes (return, renew, request)
    sub_processes_socket = context.socket( zmq.SUB )
    for branch in range(1, 3):
        request_message = 'peticion,coordinador,' + str(branch) + ',' + 'devolucion:pub_coordinator_address,' + 'renovacion:pub_coordinator_address,' + 'solicitud:pub_coordinator_address'
        register_socket.send( request_message.encode('utf-8') )
        response = register_socket.recv().decode('utf-8').split(',')
        print(branch)
        # Subscribe to addresses
        for process in response: 
            address = process.split(' ')[1]
            sub_processes_socket.connect( f'tcp://{ address }')
            print(address)
        # Eof
    # Eof
    sub_processes_socket.subscribe( ''.encode('utf-8') )

    # Poller configuration 
    poller = zmq.Poller()
    poller.register( rep_processes_socket, zmq.POLLIN )
    poller.register( sub_processes_socket, zmq.POLLIN ) 


    print('---------------------')
    print('|    Coordinador    |')
    print('---------------------')

    while True: 
        events = dict( poller.poll() )
        if rep_processes_socket in events and events[rep_processes_socket] == zmq.POLLIN: 
            message = rep_processes_socket.recv().decode('utf-8')
            print('REP_PROCESSES_SOCKET [%s]' % message)
            if is_db_occupied == True: 
                print('DB occupied')
                rep_processes_socket.send('Access denied'.encode('utf-8'))
            else: 
                print('DB free to access ...')
                is_db_occupied = True
                rep_processes_socket.send('Access granted'.encode('utf-8'))

        if sub_processes_socket in events and events[sub_processes_socket] == zmq.POLLIN: 
            message = sub_processes_socket.recv().decode('utf-8')
            print('SUB_PROCESSES_SOCKET [%s]' % message)
            if message == 'Free resource': 
                is_db_occupied = False
                print('DB is free now.')
    # Eow                

    # Close socket(s)
    rep_processes_socket.close()

    # Inform the user, succsefull exit 
    print('Programa teminado correctamente')