
# ~ Simple File Protocal ~
# Fabrizio Catinella
# Mark Glasgow

# Method List:
#	sendFile(conn,f)
#	recvFile(conn,header)
#	packHeader(cmd, File)
#	getFilePath(f="")
#	getHeader(conn)
#	fileExist(conn, header)

# Dependacies
import socket
import os
import sys
import re
from pathlib import Path

# Send file with b encoding
def sendFile(conn,f):

        filePath = getFilePath(f)

        try:
                with open(filePath, "rb") as data:
                        chunk = data.read(1024)
                        conn.sendall(chunk)
                        while chunk != b"":
                                chunk = data.read(1024)
                                conn.sendall(chunk)
                print("Finished reading file")
                return True
        except:
                print("Error reading File!")
                return False

# Receive file with b encoding
def recvFile(conn, header):

        # Deconstruct the header 
        fileSize = int(header[1])
        fileName = header[2]
        filePath =getFilePath(fileName)

        try:

                # Start writing to the file
                with open(filePath, "wb") as new_f:
                        chunkData = conn.recv(1024)
                        dataRecv   = len(chunkData)
                        new_f.write(chunkData)
                        while dataRecv < fileSize:
                                chunkData = conn.recv(1024)
                                dataRecv += len(chunkData)
                                new_f.write(chunkData)

                                # 0-100% visual counter
                                sys.stdout.write(str(int((dataRecv/fileSize)*100))+'%\r')
                                sys.stdout.flush()

                print("File Downloaded")

        except:
                print("Error downloading client file!")


# Takes the command of the user and file info and packs it into header format:
#       ~> command:fileSize:fileName
def packHeader(cmd, File):

	filePath = getFilePath(File)

        # Pack Header
	fileName = File if File !='N/A' else 'N/A'

	if (File != 'N/A') and (File in os.listdir(getFilePath())):
		fileSize = str(os.path.getsize(filePath))
	else:
		fileSize = str(0)
        
	command  = cmd
	header   = command + ':' + fileSize + ':' + fileName
	header   = bytes(header,'utf-8')

	return header

# Get file path of file
def getFilePath(f=""):

        return Path(os.path.dirname(os.path.realpath(__file__))) / f

# Get a header from a socket
def getHeader(conn):
        header = conn.recv(5124)
        header = header.decode('utf-8')
        header = header.split(':')
        header[1] = int(header[1])
        conn.send(b'ack')
        return header

# Check if file exists on current machine and sends to socket if it does exist
def fileExist(conn, header):

        #Deconstuct header for filename
        fileName = header[2]

        # Check if file is already in server
        if fileName in os.listdir(getFilePath()):
                print("File recieved already in server.")
                conn.sendall("EXISTS".encode('utf-8'))
                return True
        else:
                conn.sendall("NOT_EX".encode('utf-8'))
                return False

