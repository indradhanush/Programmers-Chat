Programmers-Chat
================

A chat application built with Twisted that also supports file transfer from client to client

To run the program : 
Server side : python server.py

Client side : python client.py 193.168.10.12
              where 193.168.10.12 is the IP of the server.




Currently it supports two commands from within the program : 

/online :  Gives the list of currently online clients
/send destination filename : Sends a file to the destination. Currently it successsfully sends a file to the server. Will complete the implementation of client to client file transfer. 'destination' is server so it is inconsequential and can be ignored for now.
