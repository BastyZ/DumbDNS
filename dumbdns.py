import argparse
import socket as libsock
import random
import struct
import time
import errno

class Server:
    def __init__(self, port, timeout):
        # TODO things

if __name__ == "__main__":
    description = "a fucking damn dns"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-P', '--port',
                        help='Port used for the request. Default port is 1025',
                        default=1025)
    parser.add_argument('-C', '--cache',
                        help='Cache Timeout in [s], default value is 3600.',
                        default=3600,
                        type=int)
    parser.add_argument('-F', '--forward',
    					help='JSON containing names/domains used to be forwarded to another IP')
    parser.add_argument('-B', '--blocked',
    					help='JSON containing names/domains that will not receive a response')
    
    args = parser.parse_args()

    port = args.port
    cache_timeout = args.cache_timeout
    forward = {}
    blocked = {}

    if  port <= 1024:
    	print("Port value should be greater than 1024")
    	return errno.EINVAL

    if args.forward:
    	with open(args.forward, 'r', encoding='utf-8') as file:
    		try:
    			forward = json.load(file)

    		finally:
    			file.close()

    if args.blocked:
    	with open(args.blocked, 'r', encoding='utf-8') as file:
    		try:
    			blocked = json.load(file)

    		finally:
    			file.close()
