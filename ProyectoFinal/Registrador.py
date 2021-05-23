"""
    Authors: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""
"""
    Register: 
    
    This process will contain all IP addresses and ports to the all other processes,
    they will register to this process and the register will assign ports to all processes.
    The other processes will have to register and then they will request information about other 
    processes

    Protocol used to request and response PORTS used : REQ - REP

"""

#------------------------------------------------
#                 Classes
#------------------------------------------------
# Represents a branch 
class PrimaryReplica: 
    def __init__(self, rep_frontend_address, pub_replicas_address):
        self.rep_frontend_address = rep_frontend_address
        self.pub_replicas_address = pub_replicas_address
# Eoc

class BackupReplica:
    def __init__(self, pub_primary_replica_address = ''): 
        self.pub_primary_replica_address = pub_primary_replica_address
# Eoc

# Represents a process (Return, RenewLoan, RequestLoan)
class Process: 
    def __init__(self, process_name, pub_manager_address, pub_coordinator_address): 
        self.process_name = process_name
        self.pub_manager_address = pub_manager_address
        self.pub_coordinator_address = pub_coordinator_address
# Eoc

# Represents the coordinator
class Coordinator: 
    def __init__(self, rep_processes_address):
        self.rep_processes_address = rep_processes_address
# Eoc

# Represents a Load Manager
class LoadManager: 
    def __init__(self, pub_processes_address, rep_client_address): 
        self.pub_process_address = pub_processes_address
        self.rep_client_address = rep_client_address
# Eoc

#------------------------------------------------
#                 Libraries
#------------------------------------------------
import time
import zmq
import sys

#------------------------------------------------
#                 Configurations
#------------------------------------------------
# Port(s)
REP_TO_PROCESSES_PORT = 6000

# ZMQ context
context = zmq.Context()

# Socket to register a process 
rep_to_processes_socket = context.socket( zmq.REP )
rep_to_processes_socket.bind( f'tcp://*:{ REP_TO_PROCESSES_PORT }' )

#------------------------------------------------
#                 Variables
#------------------------------------------------
# Branches IP address
branch = [ '-1', '25.0.228.65', '25.0.228.65' ]
# Arrays to store information of all branches
load_managers = [ [] for _ in range(0, 10) ]
return_book = [ [] for _ in range(0, 10) ] 
renew_loan = [ [] for _ in range(0, 10) ]
request_loan = [ [] for _ in range(0, 10) ] 
# Replicas
primary_replica = PrimaryReplica('', '')
backup_replica = [ BackupReplica() ] 

# Coordinator 
coordinator = Coordinator( branch[1] + ':4000' ) 

#------ Register load managers ------
# Branch 1
load_managers[1].append( LoadManager(branch[1] + ':3000', branch[1] + ':5551') ) # Primary load manager
load_managers[1].append( LoadManager(branch[1] + ':2999', branch[1] + ':5550') ) # In case, the primary load manager fails
# Branch 2 
load_managers[2].append( LoadManager(branch[2] + ':3000', branch[2] + ':5551') ) # Primary load manager
load_managers[2].append( LoadManager(branch[2] + ':2999', branch[2] + ':5550') ) # In case, the primary load manager fails

#------ Register processes ------
# Branch 1
return_book[1].append( Process('devolucion', branch[1] + ':1001', branch[1] + ':3001') ) # Return Book 
renew_loan[1].append( Process('renovacion', branch[1] + ':1002', branch[1] + ':3002') ) # Renew Loan
request_loan[1].append( Process('solicitud', branch[1] + ':1003', branch[1] + ':3003') ) # Request Loan
# Branch 2
return_book[2].append( Process('devolucion', branch[2] + ':1001', branch[2] + ':3001') ) # Return Book 
renew_loan[2].append( Process('renovacion', branch[2] + ':1002', branch[2] + ':3002') ) # Renew Loan
request_loan[2].append( Process('solicitud', branch[2] + ':1003', branch[2] + ':3003') ) # Request Loa

#------ Register replicas ------
# Primary replica
rep_frontend_address = branch[1] + ':9999'
pub_replicas_address = branch[1] + ':9950'
primary_replica = PrimaryReplica( rep_frontend_address, pub_replicas_address )
# Backup replicas 

#------------------------------------------------
#                Main 
#------------------------------------------------
if __name__ == '__main__':
    print('---------------------')
    print('|    Registrador    |')
    print('---------------------')
    while True:
        print('Esperando peticiones ...')
        # Wait for process to request to register 
        req = rep_to_processes_socket.recv().decode('utf-8')
        request = req.split(',')

        request_type = request[0]
        name = request[1]
        branch = int(request[2])

        # When a process wants to register 
        # Check what kind of process wants to register
        if request_type == 'registro':
            print('Registro.')
            # If process (Return_book, renew_loan or request_loan) wants to register
            if name == 'devolucion' or name == 'renovacion' or name == 'solicitud':
                pub_manager_port = request[3]
                pub_coordinator_port = request[4]
                # Create new process 
                new_process = Process(name, pub_manager_port, pub_coordinator_port)
                # Save new process
                if name == 'devolucion': 
                    return_book[ branch ].append( new_process )
                elif name == 'solicitud': 
                    request_loan[ branch ].append( new_process )
                elif name == 'renovacion': 
                    renew_loan[ branch ].append( new_process )
            
            # If coordinator wants to register 
            elif name == 'coordinador':
                address = request[3]
                coordinator.rep_processes_address = address
            
            # If load manager wants to register
            elif name == 'gestor_carga':
                new_load_manager = LoadManager(request[3], request[4])
                load_managers[ branch ].append( new_load_manager )

            # If primary replica wants to register
            elif name == 'replica_primaria':
                rep_frontend_address = request[3]
                pub_replicas_socket = request[4]
                new_primary_replica = PrimaryReplica( rep_frontend_address, pub_replicas_socket )
                primary_replica = new_primary_replica

            # If a bakcup replica wants to register
            elif name == 'replica_respaldo':
                pub_primary_replica_address = request[3]
                new_backup_replica = BackupReplica( pub_primary_replica_address ) 
                backup_replica.append( new_backup_replica ) 

            # Prepare response 
            response = 'ok'
        # Eoi

        elif request_type == 'peticion': 
            print('Petición')
            # Request example ...
            # peticion,< process_name >, < branch >, < process_name >:< address >, ...
            
            # Traverse request and construct string with response 
            response = ''
            requests = request[3:]

            for request in requests: 
                requested_process_name, address_requested = request.split(':')
                # If requested process is coordinator
                if requested_process_name == 'coordinador':
                    response += 'coordinator '
                    response += coordinator.rep_processes_address

                # If requested process is load manager
                elif requested_process_name == 'gestor_carga': 
                    response += 'load_manager '
                    if address_requested == 'pub_processes_address':
                        response += load_managers[ branch ][ 0 ].pub_process_address  
                    else: 
                        response += load_managers[ branch ][ 0 ].rep_client_address

                # If requested process is return, renew or request_loan
                elif requested_process_name == 'devolucion' or requested_process_name == 'renovacion' or requested_process_name == 'solicitud': 
                    # Set the type of response 
                    response += requested_process_name + ' ' 

                    # Debug 
                    print('BRANCH : [%s]' % branch)
                    print('\nreturn_books :', return_book, '\nrenew_loan : ', renew_loan, '\nrequest_loan : ', request_loan) 
            
                    # Check type of address requested and process
                    # If process is return book 
                    if address_requested == 'pub_manager_address' and requested_process_name == 'devolucion': 
                        response += return_book[ branch ][ 0 ].pub_manager_address
                    elif address_requested == 'pub_coordinator_address' and requested_process_name == 'devolucion':
                        response += return_book[ branch ][ 0 ].pub_coordinator_address

                    # If process is renew loan  
                    if address_requested == 'pub_manager_address' and requested_process_name == 'renovacion': 
                        response += renew_loan[ branch ][ 0 ].pub_manager_address
                    elif address_requested == 'pub_coordinator_address' and requested_process_name == 'renovacion':
                        response += renew_loan[ branch ][ 0 ].pub_coordinator_address

                    # If process is request loan  
                    if address_requested == 'pub_manager_address' and requested_process_name == 'solicitud': 
                        response += request_loan[ branch ][ 0 ].pub_manager_address
                    elif address_requested == 'pub_coordinator_address' and requested_process_name == 'solicitud':
                        response += request_loan[ branch ][ 0 ].pub_coordinator_address
                     
                # If requested process is primary replica
                elif requested_process_name == 'replica_primaria':
                    response += requested_process_name + ' '
                    if address_requested == 'pub_replicas_address': 
                        response += primary_replica.pub_replicas_address
                    elif address_requested == 'rep_frontend_address': 
                        response += primary_replica.rep_frontend_address

                # If requested process is backup replica
                elif requested_process_name == 'replica_respaldo':
                    for backup in backup_replica: 
                        response += requested_process_name + ' '
                        response += backup.pub_primary_replica_address + ','
                    # Eof
                    # Remove last ','
                    response = response[:len(response) - 1]

                # If request is to get the branches
                elif requested_process_name == 'sedes':
                    for b in branch:
                        response += b + ','

                print(request)
                # Add ',' to separate requests
                response += ','
            # Eof
            
            # Remove last ','
            response = response[:len(response) - 1]
        # Eoi

        # Send back response to process
        rep_to_processes_socket.send( response.encode('utf-8') )