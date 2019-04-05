import argparse
import json
import socket as libsock
import struct
import time
import errno
import sys

localhost = "127.0.0.1"


class Server:
    def __init__(self, port, resolver, timeout, forward, blocked):
        # Variables
        self.port = port
        self.resolver = resolver
        self.timeout = timeout
        self.forward = forward
        self.blocked = blocked

        # Actual code
        host = localhost
        socket = libsock.socket(libsock.AF_INET, libsock.SOCK_DGRAM)  # IPv4, UDP
        socket.bind((host, port))
        print("server listening on {}:{}".format(host, port))
        # Main Loop
        while True:
            request, address = socket.recvfrom(1024)
            print("Received:\n", request)
            # Ask to DNS server
            response = self.dns_query(request)
            # response is the same query (worst)
            # FIXME delet this
            socket.sendto(response, address)

    def dns_query(self, request):
        print("gonna ask to DNS")
        dns_socket = libsock.socket(libsock.AF_INET, libsock.SOCK_DGRAM)
        dns_socket.connect((self.resolver, 53))
        dns_socket.sendto(request, (self.resolver, 53))
        response, resolver = dns_socket.recvfrom(4096)
        print("Received from {} \n {}".format(self.resolver, response))
        return response


def main(args):
    port = args.port
    resolver = args.resolver
    cache_timeout = args.cache
    forward = {}
    blocked = {}

    if port <= 1024:
        print("Port value should be greater than 1024")
        return sys.exit(errno.EINVAL)

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
    Server(port, resolver, cache_timeout, forward, blocked)


if __name__ == "__main__":
    description = "a fucking damn dns"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-P', '--port',
                        help='Port used for the request. Default port is 1025',
                        default=1025,
                        type=int)
    parser.add_argument('-R', '--resolver',
                        help='Resolver to get an actual answer',
                        default='1.1.1.1')
    parser.add_argument('-C', '--cache',
                        help='Cache Timeout in [s], default value is 3600.',
                        default=3600,
                        type=int)
    parser.add_argument('-F', '--forward',
                        help='JSON containing names/domains used to be forwarded to another IP')
    parser.add_argument('-B', '--blocked',
                        help='JSON containing names/domains that will not receive a response')

    main(parser.parse_args())
