

# ~ Client Side Script ~
# Fabrizio Catinella
# Mark Glasgow
#
# Function:
#	-Connect to a server with a host-name and port
#	-Send out a command
#		~ upload
#			(Send a file to server)
#		~ get
#			(Download a file from server)
#		~ list
#			(Get a list of the server's dir)

# Import dependancies
import socket
import os
import sys
import re
import pyTransfer as pyT
from pathlib import Path

# Socket setup
def cliSockSet(ip, port, cmd, File):
	
	# Mapped launch list
	launch = {"upload":uploadFile,"list":getDir,"get":getFile}

	try:
		# s is the socket connection
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip,port))
	except:
		print("Error connecting to server. Is it online?")
		return None

	# Execute command
	launch[cmd](s,File)
	
	# Connection end
	s.close()
		
# ~ Functions for cmds ~

# 1) Upload
def uploadFile(conn, File):

	header = pyT.packHeader('upload',File)

	# Send header
	conn.sendall(header)
	conn.recv(100)

	# Get confirmation
	check = conn.recv(6)
	check = check.decode('utf-8')
	
	if (check == "EXISTS"):
		print("File already exists on server.")
		return None
	elif (check == "NOT_EX"):
		print("Server is ready for file.")
	
	# Send file
	sent = pyT.sendFile(conn,File)

	if (sent):
		print("File uploaded to server")
	else:
		print("File not sent to server")


# 2) List
def getDir(conn, File):

	#Define Directory
	servDir = ""

	# Pack Header
	header = pyT.packHeader('list',File)

	# Send header
	conn.sendall(header)
	conn.recv(100)

	# Recv server directory file size
	sizeDir  = conn.recv(4)
	sizeDir  = int.from_bytes(sizeDir, 'big')
	sizeDir  = socket.ntohl(sizeDir)
	conn.sendall(b'ack')

	# Recv server directory
	dirChunk = conn.recv(10)
	dataRecv = len(dirChunk.decode('utf-8'))
	servDir += dirChunk.decode('utf-8')
	while dataRecv < sizeDir:
		dirChunk  = conn.recv(10)
		dataRecv += len(dirChunk.decode('utf-8'))
		servDir  += dirChunk.decode('utf-8')

	#Output server Directory
	servDir = servDir.split(':')
	servDir.sort()
	print("~ Server Directory ~ \n")
	for f in servDir:
		print("$~: " + f)
	
# 3) Get

def getFile(conn, File):
	
	# Pack header
	header = pyT.packHeader('get', File)
	
	# Send header
	conn.sendall(header)
	conn.recv(100)

	# Get confirmation
	check = conn.recv(6)
	check = check.decode('utf-8')
	
	if (check == "NOT_EX"):
		print("File does not exist on server.")
		return None
	elif (check == "EXISTS"):
		print("Server has requested file.")

	# Get header from server
	resp_header = pyT.getHeader(conn)

	# Download file 
	pyT.recvFile(conn, resp_header)
 

# Main execution
def main():	

	try:
		# Get user input via cmd line

		# RE match for xxx.xxx.xxx.xxx
		assert(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', sys.argv[1])), "Enter a proper IPv4 address."
		ip   = sys.argv[1]

		# RE match for decimal numbers
		assert(re.match(r'^\d+$', sys.argv[2])), "Enter a proper port number."
		assert(int(sys.argv[2])>1024 and int(sys.argv[2])<65535), "Enter a port number between 1024 & 65535"
		port = int(sys.argv[2])

		# RE match for 'upload' 'get & 'list'
		assert(re.match(r'^upload$|^get$|^list$',sys.argv[3])), "Enter a selected command [upload,get,list]"
		cmd  = sys.argv[3] 
		

		if cmd == "upload":
			# RE match for example.txt or example.xy.yz
			assert(re.match(r'^.+\.[a-zA-z0-9]+(\.[a-zA-z0-9]+)*$',sys.argv[4])), "Enter a proper file name with ext."	
			File = sys.argv[4]
			# Assert for file existance
			assert(File in os.listdir(pyT.getFilePath())), "File %s does not exist." % File
		elif cmd == "get":
			# RE match for example.txt or example.xy.yz	
			assert(re.match(r'^.+\.[a-zA-z0-9]+(\.[a-zA-z0-9]+)*$',sys.argv[4])), "Enter a proper file name with ext."      
			File = sys.argv[4]
		else:
			File = 'N/A'

	except AssertionError as error:
		print(error)
		return None
	
	except:
		print("Not enough arguments given.")
		print("Format: ip port cmd [file]")
		return None	
	
	# Setup Socket
	cliSockSet(ip,port,cmd,File)

# Run main
if __name__ == "__main__":
	main()
