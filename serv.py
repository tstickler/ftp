import socket
import sys
import commands
import os

if len(sys.argv) < 2:
    print "USAGE python " + sys.argv[0] + "<PORT NUMBER>"

# The port on which to listen
listen_port = 1234 #int(sys.argv[1])

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

                # While there is still stuff in the file, keep sending it
                while i:
                    client_socket.send(i)
                    i = f.read(1024)

                # Close the file when we're done
                f.close()
            except IOError:
                client_socket.sendall("error")

            # Close the socket
            client_socket.close()
            welcomeSocket.close()

        elif action == "PUT":
            # Parses user input so we can assign the correct filename
            path, arg = os.path.split(clientSock.recv(1024))

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
            new_file = open(arg, "w")

            # Begin receiving
            i = client_socket.recv(1024)

            # Keep receiving until there is nothing left
            while i:
                new_file.write(i)
                i = client_socket.recv(1024)

            # Close the file
            new_file.close()

            # Close the socket
            client_socket.close()
            welcomeSocket.close()

        elif action == "LS":
            print "ls"

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
