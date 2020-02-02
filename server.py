#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

import socket
import os
import sys
import optparse

parser = optparse.OptionParser()
parser.add_option("-f", "--file", dest='filename')
parser.add_option("-p", "--pass", dest='password')
(options, args) = parser.parse_args()

HOST = ''
PORT = 10010
NCON = 5
BUFF = 10
FILE = 'default.txt' if options.filename is None else options.filename
PASS = '12345678'    if options.password is None else options.password

if not os.path.exists(FILE):
	print("File: {} does not exist.".format(FILE))
	sys.exit()

def connect():
	print("Server Running, waiting for connections")
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	serversocket.bind((HOST, PORT))
	serversocket.listen(NCON)

	try:
		while True:
			clientsocket, address = serversocket.accept()
			print("Connection from {} has been established!".format(address[0]))
			password = clientsocket.recv(BUFF)

			if password.decode('utf-8') == PASS:
				clientsocket.send('True')
				with open(FILE, 'rb') as f:
					l = f.read(BUFF)
					while l:
						clientsocket.send(l)
						l = f.read(BUFF)
				print("File: {} successfully sent".format(FILE))
				clientsocket.close()
			else:
				clientsocket.send('False')
	except KeyboardInterrupt:
		print("Server closed")

	clientsocket.close()
	serversocket.close()
	sys.exit()

if __name__ == "__main__":
	connect()
