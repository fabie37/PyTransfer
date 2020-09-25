# ~ Client Side Script ~
# Fabrizio Catinella
# Mark Glasgow
#
# Function:
#	-Connect to a server with a host-name and port
#	-Send out a command
#		~ put
#			(Send a file to server)
#		~ get
#			(Download a file from server)
#		~ list
#			(Get a list of the server's dir)

# Import dependancies
from socket import *
import os
import sys
import re
from pathlib import Path
import pyT2 as pyT


# Socket setup
def cliSockSet(ip, port, cmd, File):
    
    # Mapped launch list
    launch = {"put":uploadFile,"list":getDir,"get":getFile}

    try:
        # s is the socket connection
        s = socket(AF_INET, SOCK_STREAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
        s.settimeout(3)
        s.connect((ip,port))
        s.settimeout(None)
    except:
        print("Connection to server timed-out. Is it online?")
        return None

    # Execute command
    launch[cmd](s,File)
    
    # Connection end
    s.close()
        

## ~ Functions for cmds ~
# 1) Upload / Put
def uploadFile(conn, File):

    header = pyT.packHeader('put',File)

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
    sizeDir  = ntohl(sizeDir)
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
    
# 3) Get / Download
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
    elif (check == "PROTEC"):
        print("This is a protected file.")
        return None

    # Get header from server
    resp_header = pyT.getHeader(conn)

    # Download file 
    pyT.recvFile(conn, resp_header)
 

# Main execution
def main():	

    try:
        # Get user input via cmd line

        # RE match for xxx.xxx.xxx.xxx
        #assert(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', sys.argv[1])), "Enter a proper IPv4 address. Ensure you're also using the correct format. Format: client.py ip port cmd [file] "
        ip   = sys.argv[1]

        # RE match for decimal numbers
        assert(re.match(r'^\d+$', sys.argv[2])), "Enter a proper port number. Format: client.py ip port cmd [file]"
        assert(int(sys.argv[2])>1 and int(sys.argv[2])<65535), "Enter a port number between 1 & 65535. \nEnsure you're also using the correct format. \nFormat: client.py ip port cmd [file] "

        port = int(sys.argv[2])

        # RE match for 'put' 'get & 'list'
        assert(re.match(r'^put$|^get$|^list$',sys.argv[3])), "Enter a selected command [put/get/list]. \nEnsure you're also using the correct format. \nFormat: client.py ip port cmd [file] "
        cmd  = sys.argv[3] 
        

        if cmd == "put":
            # RE match to ensure filename is unicode. 
            assert(not re.match(r'^\w+$',sys.argv[4])), "Your filename contains non-unicode characters. Ensure you're also using the correct format. Format: client.py ip port cmd [file] "	
            assert(not re.match(r'^/+', sys.argv[4])), 'Filename contains illegal character [slash]'
            File = sys.argv[4]
            # Assert for file existance
            assert(File in os.listdir(pyT.getFilePath())), "File %s does not exist." % File
            # Assert for max and min size
            assert(pyT.getFileSize() > 0), "Selected file is 0 bytes"
            assert(pyT.getFileSize() < 1073741824), "Selected file is too large at %s bytes. Max upload size 1GB" % pyT.getFileSize()
            # Ensure file name isn't above 255 characters
            assert(len(File) < 255), "Filename must be below 255 characters"
            
        elif cmd == "get":
            # RE match to ensure filename is unicode. 
            assert(not re.match(r'^\w+$',sys.argv[4])), "Your filename contains non-unicode characters. Ensure you're also using the correct format. Format: client.py ip port cmd [file] "	
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
