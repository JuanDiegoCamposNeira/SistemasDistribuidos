"""
    Autores: 
        - Simón Dávila Saravia
        - Jose Mario Árias Acevedo 
        - Juan Diego Campos Neira
"""

"""-----------------------------------------------
-------------    Gestor de carga    -------------- 
-----------------------------------------------"""

import time
import zmq

# Library configurations 
context = zmq.Context() # Get the context
socket = context.socket(zmq.REP) # Set the socket to be a REPLY socket  
socket.bind("tcp://25.114.38.38:5555") # Bind the socket with an IPv4 adress


# Function to update the state of a book in the Data Base
# TO DO : This function should send a message to other Load Manager (GC) 
#         in order to update the other DB (replica) 
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
    # Eof
    # Close the file 
    books.close()
# Eof

# Main 
if __name__ == "__main__":
    # Initialize server
    while True:
        # Wait for next request from client
        message = socket.recv()
        # Print the message recived
        print(f"Received request: {message}")

        # Make the substring of the message
        message = str(message)
        message = message[2 : len(message) - 3]
        peticion = message.split(" ", 1)
        libro = peticion[1]

        # Process the client request and update the state of the book in the DB
        actualizar_bd(peticion[0],libro)

        # Send reply back to client
        server_response = "Petición de " + str(peticion[0]) + " procesada con éxito"
        socket.send(bytes(server_response, 'utf-8'))
    # Eow
# Eom 