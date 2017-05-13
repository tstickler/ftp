import socket
import sys
import commands
import os

# Command line checks
if len(sys.argv) < 3:
    print "USAGE python " + sys.argv[0] + " <server_machine> <server_port>"

# Server address
serverAddr = sys.argv[1]

# Server port
serverPort = int(sys.argv[2])

# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
connSock.connect((serverAddr, serverPort))

# Receive connection status from server
reply = connSock.recv(1024)

if reply == "Connection Accepted":
    print reply, "\n"

    user_in = ""
    while user_in != "quit":
        user_in = raw_input("ftp> ")

        # Forces input to uppercase to evaluate
        user_in = user_in.lower()

        # Splits the input to handle filename on get/put
        tokens = user_in.split()

        # Determines which action the user would like to take
        command = tokens[0]

        if command == "quit":
            connSock.send("QUIT")
        elif command == "get":
            # Makes sure that the user entered an argument
            if len(tokens) != 2:
                print "USAGE get <filepath>"
                continue

            # Holds the file path
            arg = tokens[1]

            try:
                connSock.settimeout(3)
                # Tell the server we want to download
                connSock.send("GET")
                connSock.send(arg)

                # Receive socket to connect to from server
                new_port = int(connSock.recv(1024))
            except socket.timeout:
                print "Connection timed out"
                continue

            # Create a socket to transmit on
            eph_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the socket
            eph_sock.connect((serverAddr, new_port))

            # Begin receiving
            i = eph_sock.recv(1024)

            if i == "error":
                print "File does not exist on the server"
                eph_sock.close()
                continue

            # Open file to write
            new_file = open(arg, "w")

            file_size = len(i)

            # Keep receiving until there is nothing left
            while i:
                new_file.write(i)
                i = eph_sock.recv(1024)
                file_size += len(i)

            # Close the file
            new_file.close()

            # See how much the server sent
            server_reported_file_size = connSock.recv(1024)

            # If file sizes match, success
            if server_reported_file_size == str(file_size):
                print "SUCCESS"
                print "Received:", arg, "\n", "Size:", file_size
            else:
                print "Failure receiving file"
                os.remove(arg)

            # Close the socket
            eph_sock.close()
        elif command == "put":
            # Makes sure that the user entered an argument
            if len(tokens) != 2:
                print "USAGE put <filepath>"
                continue

            # Holds the file path
            arg = tokens[1]

            # Check to make sure file path exists
            if os.path.isfile(arg):


                # Parses user input so we can assign the correct filename
                path, f_name = os.path.split(arg)

                try:
                    connSock.settimeout(3)

                    # Tell server we want to upload
                    connSock.send("PUT")
                    connSock.send(f_name)

                    # Receive socket to connect to from server
                    new_port = int(connSock.recv(1024))
                except socket.timeout:
                    print "Connection timed out"
                    continue

                # Create a socket to transmit on
                eph_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Connect to the socket
                eph_sock.connect((serverAddr, new_port))

                try:
                    # Open the file we are sending
                    f = open(arg, "r")

                    # Begin reading
                    i = f.read(1024)

                    file_size = len(i)

                    # While there is still stuff in the file, keep sending it
                    while i:
                        eph_sock.sendall(i)
                        i = f.read(1024)
                        file_size += len(i)

                    # Close the file when we're done
                    f.close()

                    # Tell server how much we sent
                    file_size = str(file_size)
                    connSock.send(file_size)
                except IOError:
                    print "Error opening file"

                # Close the socket
                eph_sock.close()

                print "Server response: ", connSock.recv(1024), "\n", \
                    "Sent:", f_name, "\n", "Size:", file_size

            else:
                print "File does not exist"
        elif command == "ls":
            # Tell the socket we want ls
            connSock.send("LS")

            # Receive socket to connect to from server
            new_port = int(connSock.recv(1024))

            # Create a socket to transmit on
            eph_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the socket
            eph_sock.connect((serverAddr, new_port))

            # Holds response from server
            ls = eph_sock.recv(1024)

            # Print results from ls command
            print ls

            # Close the socket
            eph_sock.close()
        elif command == "lls":
            # Run ls command, get output, and print it
            for line in commands.getstatusoutput('ls -l'):
                print line
        else:
            print "Invalid input"

    print "Closing connection"
    connSock.close()
else:
    print "Fail"
