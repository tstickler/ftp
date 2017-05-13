import socket
import sys
import commands
import os

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
            # Gets user specified file path
            arg = clientSock.recv(1024)

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

            # Attempt to open the file given by the user
            try:
                # Open the file we are sending
                f = open(arg, "r")

                # Begin reading
                i = f.read(1024)

                file_size = len(i)

                # While there is still stuff in the file, keep sending it
                while i:
                    client_socket.sendall(i)
                    i = f.read(1024)
                    file_size += len(i)

                # Tell the client how big the file should have been
                file_size = str(file_size)
                clientSock.sendall(file_size)

                # Report in server
                print "To:", addr, "\n", "Sent:", arg, "\n", "Size:", file_size

                # Close the file when we're done
                f.close()
            except IOError:
                client_socket.sendall("error")

            # Close the socket
            client_socket.close()
            welcomeSocket.close()

        elif action == "PUT":
            # Sets filename to use
            f_name = clientSock.recv(1024)

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
            new_file = open(f_name, "w")

            # Begin receiving
            i = client_socket.recv(1024)

            file_size = len(i)

            # Keep receiving until there is nothing left
            while i:
                new_file.write(i)
                i = client_socket.recv(1024)
                file_size += len(i)

            # Close the file
            new_file.close()

            client_reported_file_size = clientSock.recv(1024)
            if client_reported_file_size == str(file_size):
                # Report in server
                print "From:", addr, "\n", "Received:", f_name, "\n", \
                    "Size:", file_size
                clientSock.sendall("SUCCESS")
            else:
                print "Failure receiving file"
                clientSock.sendall("FAIL")
                os.remove(arg)

            # Close the socket
            client_socket.close()
            welcomeSocket.close()

        elif action == "LS":
            # Report command
            print "From:", addr, "\n", "ls command"

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

            # Holds the string to send to client
            ls = ""

            # Run ls command, get output, and append to the string
            for line in commands.getstatusoutput('ls -l'):
                ls += str(line) + "\n"

            # Send response to client
            client_socket.sendall(ls)

            # Close the socket
            client_socket.close()
            welcomeSocket.close()
