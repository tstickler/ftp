# *****************************************************
# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import os
import sys
import commands

if len(sys.argv) < 2:
    print "USAGE python " + sys.argv[0] + "<PORT NUMBER>"

# The port on which to listen
listen_port = int(sys.argv[1])

# Create a welcome socket.
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listen_port))

# Start listening on the socket
welcomeSock.listen(1)

# Accept connections forever
while True:
    print "Waiting for connections..."

    # Accept connections
    clientSock, addr = welcomeSock.accept()

    print "Accepted connection from client: ", addr
    print "\n"

    clientSock.sendall("Connection Accepted")

    # Keep client connection to allow multiple actions
    while True:
        # Receive user action
        action = clientSock.recv(1024)

        if action == "QUIT":
            print "Client terminated connection"
            clientSock.close()
            break
        elif action == "GET":
            print "get"
        elif action == "PUT":
            print "put"

            # Create a socket
            welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to port 0
            welcomeSocket.bind(('', 0))

            # Grab socket number as string
            new_sock = str(welcomeSocket.getsockname()[1])

            # Tell client to connect on this socket
            clientSock.sendall(new_sock)

            # Listen for client connection
            welcomeSocket.listen(5)

            # Accept client connection
            client_socket, addr = welcomeSocket.accept()

            # Open file to write
            new_file = open("new_file.txt", "w")

            # Begin receiving
            i = client_socket.recv(1024)

            # Keep receiving until there is nothing left
            while i:
                new_file.write(i)
                i = client_socket.recv(1024)

            # Close the file
            new_file.close()

            # Close the socket
            welcomeSocket.close()

        elif action == "LS":
            print "ls"
