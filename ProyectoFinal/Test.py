import zmq 

context = zmq.Context()

# Sub 
sub_socket = context.socket( zmq.SUB )
sub_socket.connect('tcp://localhost:5000')

# Req 
req_socket = context.socket( zmq.REQ )
req_socket.connect('tcp://localhost:9999')

# Rep
# rep_socket = context.socket( zmq.REP )
# rep_socket.bind('tcp://*:4000')

# Pub 
pub_socket = context.socket( zmq.PUB )
pub_socket.bind('tcp://*:9953')

while True: 
    # ----- REQ -----
    r = input('$ ').encode('utf-8')
    req_socket.send(r)
    response = req_socket.recv().decode('utf-8')
    print('Response ', response)

    # ----- PUB -----
    # r = input('$ ').encode('utf-8')
    # pub_socket.send(r)
