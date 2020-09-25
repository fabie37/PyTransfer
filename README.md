# PyTransfer
A simple TCP server and client written in python

This was a 2-man team project that I had done with a friend in the first half of second year.
It was a breeze working with him and in the end we were pretty proud of the code.
It was stable to transfer larger files over the network and ultimately was pretty satisfying to come up with.

The code works as long as you have a connection port open and a static ip address for the server.

# Client:

 Function: </br>
	-Connect to a server with a host-name and port</br>
	-Send out a command</br>
		~ put</br>
			(Send a file to server)</br>
		~ get</br>
			(Download a file from server)</br>
		~ list</br>
			(Get a list of the server's dir)</br>


# Server:</br>

 Function: </br>
  -Listen for connections</br>
	-Receive commands</br>
		~ put </br>
			(Expect a file to store)</br>
		~ get</br>
			(Send a file out a file)</br>
		~ list</br>
			(List the files on the server)</br>
