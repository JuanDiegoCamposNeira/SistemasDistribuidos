#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq


def actualizar_bd(peticion : str, libro : str): 
    # Open file
    books = open("Libros.txt", "r")
    books_temp = []

    # Traverse books 
    for book in books: 
        book_splitted = book.split(",")
        #print(peticion,libro)
        # Check if the current book is the book searched 
        if book_splitted[0] == libro: 
            available = int(book_splitted[3]) 
            borrowed = int(book_splitted[4])
            # If the request is to give back the book 
            if peticion == "Devolucion": 
                borrowed -= 1
                available += 1
            # Eoi     
            # Set the new state of the book
            book_splitted[3] = str(available)
            book_splitted[4] = str(borrowed)
        # Eoi
        print(book_splitted)
        # Save the state of the book
        book_state = ""
        for i in book_splitted: 
            book_state += i + ","
        # Eof 
        # Remove the last ','
        book_state = book_state[:len(book_state) - 1]
        # Append book to the list 
        books_temp.append(book_state)
    # Eof      
    # Close file
    books.close()

    # Open file to write books 
    books = open("Libros.txt", "w")
    for book in books_temp: 
        books.write(book + "\n") 
    # Close the file 
    books.close()
# Eof

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://25.114.38.38:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")
    message = str(message)
    message = message[2:len(message)-3]
    peticion = message.split(" ",1)
    libro = peticion[1]
    print(peticion[0],libro)
    actualizar_bd(peticion[0],libro)

    #  Send reply back to client
    socket.send(b"Peticion procesada por mi chulo sin h")