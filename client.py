#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

import socket
import struct
import os
import sys
import multiprocessing.dummy
import multiprocessing
import subprocess
import platform
import getpass
import optparse
try:
	import fcntl
except Exception:
	pass

parser = optparse.OptionParser()
parser.add_option("-s", "--range_start", dest='start')
parser.add_option("-e", "--range_end", dest='end')
(options, args) = parser.parse_args()

PORT  = 10010
BUFF  = 10
START = 1   if options.start is None else int(options.start)
END   = 254 if options.end   is None else int(options.end)

def get_ip_address(ifname):
	try:
		server    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		packed_ip = fcntl.ioctl(server.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24]
		return socket.inet_ntoa(packed_ip)
	except Exception, e:
		print(e)
		sys.exit(0)

def get_network():
	network = ''
	if platform.system().lower()=='windows':
		network    = ".".join(socket.gethostbyname(socket.gethostname()).split('.')[:3] + [''])
	else:
		interfaces = os.listdir('/sys/class/net/')
		interfaces  = [[key, interface] for key, interface in enumerate(interfaces)]
		print("List of interfaces: {}".format(interfaces))
		interface = interfaces[int(input("Select interface: "))][1]
		print("Interface selected: {}".format(interface))
		ip_address = get_ip_address(interface)
		network    = ".".join([unit for key, unit in enumerate(ip_address.split('.')) if key != 3] + [''])
	
	print("Network: {}0".format(network))
	return network

def clear():
    if platform.system().lower()=='windows':
        os.system("cls")
    else:
        os.system("clear")

def ping(ip):
    global ips

    try:
        subprocess.check_output("ping -n 1 -w 200 {}".format(ip) if platform.system().lower()=="windows" else "ping -c 1 -i 0.2 {}".format(ip), shell=True)
    except Exception, e:
        return False

    ips.append(ip)
    return True

def ping_range(network, start=1, end=254):
	print("Looking for servers, this process may take a while..")
	num_threads = 3 * multiprocessing.cpu_count()
	p = multiprocessing.dummy.Pool(num_threads)
	p.map(ping, ["{}{}".format(network, x) for x in range(start,end)])


def request_server(ips):
	clientsocket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	for ip in ips:
		try:
			clientsocket.connect((ip, PORT))
			print("Connection established on: {}".format(ip))
			password = getpass.getpass("Password: ")
			clientsocket.send(password.encode('utf-8'))
			data = clientsocket.recv(BUFF)
			if data.decode('utf-8') == 'True':
				with open('received_file.txt', 'wb') as f:
					while True:
						print("Receiving data..")
						data = clientsocket.recv(BUFF)
						while data:
							f.write(data)
							data = clientsocket.recv(BUFF)
						if not data:
							break
				print("File received successfully")
				clientsocket.close()
			else:
				print("Wrong password")
			break
			clientsocket.close()
		except Exception as e:
			print("Connection refused on {}".format(ip))


if __name__ == "__main__":
	ips     = []
	network = get_network()
	ping_range(network, START, END)
	request_server(ips)
	
