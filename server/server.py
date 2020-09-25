

# ~ Server Side Script ~
# Fabrizio Catinella
# Mark Glasgow
# 
# Function: 
#	-Listen for connections
#	-Receive commands
#		~ upload 
#			(Expect a file to store)
#		~ get
#			(Send a file out a file)
#		~ list
#			(List the files on the server)

# Import dependancies
import socket
import os
import sys
import re
import pyTransfer as pyT
from pathlib import Path

# Socket setup
def servSockSet(port):

	# Get ip of server to bind to all available addresses
	ip = "0.0.0.0"

	# s is the socket connection
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((ip,port))
		s.listen(1)

		# conn is the connection between server and client
		conn, addr = s.accept()
		print("Socket Setup: ",addr)
	except Exception as error:
		print("Error setting up server.")
		print(error)
		return None
	
	# Get header from client
	header = pyT.getHeader(conn)

	# Get command
	command = header[0]

	# Mapped launch list
	launch = {"upload":downloadFile, "list":listDir, "get":giveFile}
	
	# Execute assositated method
	launch[command](conn,header)
	
	
	# Close connection
	conn.close()

# 1) Upload 
def downloadFile(conn,header):
	
	#Check if file already exists
	if pyT.fileExist(conn,header):
		return None
	
	#Download file
	pyT.recvFile(conn,header)
	
# 2) List
def listDir(conn, header):
	
	filePath = pyT.getFilePath()

	# Get File directory of server
	servDir = os.listdir(filePath)
	servDir = ':'.join(servDir)
	
	# Send directory filename size
	sizeDir = len(servDir)
	sizeDir = socket.htonl(sizeDir)
	sizeDir = sizeDir.to_bytes((sizeDir.bit_length() + 7) // 8, 'big') or b'\0'
	conn.sendall(sizeDir)
	conn.recv(3)

	# Send server directory
	while servDir[:10] != "":
		conn.sendall(bytes(servDir[:10],'utf-8'))
		servDir = servDir[10:]

	print("Directory list sent.")

# 3) Get
def giveFile(conn, header):
	
	# Check if requested file exists on server
	if not pyT.fileExist(conn,header):
		print("Client's requested file does not exist.")
		return None

	# Pack header to get ready to send to client
	fileName = header[2]
	resp_header = pyT.packHeader('give',fileName)
	
	# Send Header
	conn.sendall(resp_header)
	conn.recv(100)

	# Send file
	pyT.sendFile(conn,fileName)

	print("File sent to client.")	
 

# Main Execution
def main():

	# Get user input via cmd line
	port = int(sys.argv[1])
	
	# Set up server
	servSockSet(port)


# Run main
if __name__ == "__main__":
	main()
