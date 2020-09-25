# PyTransfer
A simple TCP server and client written in python

This was a 2-man team project that I had done with a friend in the first half of second year.
It was a breeze working with him and in the end we were pretty proud of the code.
It was stable to transfer larger files over the network and ultimately was pretty satisfying to come up with.

The code works as long as you have a connection port open and a static ip address for the server.

# Client:

 Function:
	-Connect to a server with a host-name and port
	-Send out a command
		~ put
			(Send a file to server)
		~ get
			(Download a file from server)
		~ list
			(Get a list of the server's dir)


# Server:

 Function: 
  -Listen for connections
	-Receive commands
		~ put 
			(Expect a file to store)
		~ get
			(Send a file out a file)
		~ list
			(List the files on the server)
