from socket import *
import sys
import os

# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys
import commands

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
    while user_in != "QUIT":
        user_in = raw_input("ftp> ")

        user_in = user_in.upper()

        if user_in == "QUIT":
            connSock.send("QUIT")
        elif user_in == "GET":
            connSock.send("GET")
        elif user_in == "PUT":
            # Tell server we want to upload
            connSock.send("PUT")

            # Receive socket to connect to from server
            new_port = int(connSock.recv(1024))

            # Create a socket to transmit on
            eph_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the socket
            eph_sock.connect((serverAddr, new_port))

            # Open the file we are sending
            f = open("file.txt", "r")

            # Begin reading
            i = f.read(1024)

            # While there is still stuff in the file, keep sending it
            while i:
                eph_sock.send(i)
                i = f.read(1024)

            # Close the file when we're done
            f.close()

            # Close the socket
            eph_sock.close()

        elif user_in == "LS":
            connSock.send("LS")
        elif user_in == "LLS":
            # Run ls command, get output, and print it
            for line in commands.getstatusoutput('ls -l'):
                print line
        else:
            print "Invalid input"

    print "Closing connection"
    connSock.close()
else:
    print "Fail"
