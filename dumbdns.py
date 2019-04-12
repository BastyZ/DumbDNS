import argparse
import json
import socket as libsock
import struct
import datetime
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
        self.hostname = ""
        self.ip = ""

        # Actual code
        host = localhost
        socket = libsock.socket(libsock.AF_INET, libsock.SOCK_DGRAM)  # IPv4, UDP
        socket.bind((host, port))
        print("server listening on {}:{}".format(host, port))
        # Main Loop
        while True:
            # Reset values
            self.hostname = ""
            self.ip = ""

            request, address = socket.recvfrom(1024)
            print("Received:\n", request)
            self.analise_header(request)
            self.analise_qsection(request[12:])  # req without header
            # Ask to DNS server
            response = self.dns_query(request)
            # send response
            socket.sendto(response, address)

    def dns_query(self, request):
        print("gonna ask to DNS")
        dns_socket = libsock.socket(libsock.AF_INET, libsock.SOCK_DGRAM)
        dns_socket.connect((self.resolver, 53))
        dns_socket.sendto(request, (self.resolver, 53))
        response, resolver = dns_socket.recvfrom(4096)
        print("Received from {} \n {}".format(self.resolver, response))
        return response

    def analise_header(self, request):
        hid, things, qdc, anc, nsc, arc, question_mark = \
            struct.unpack("!6H?", request[:13])  # Hago unpack de la info recibida
        response = "{} @ {} @ {} @ {} @ {} @ {} @ {}".format(
            hid, binary_str(things, 16),
            binary_str(qdc, 16), anc, nsc, arc, int(question_mark))  # la formateo como texto
        print("Enviaré esta respuesta: " + response)  # esta es la cadena formateada como sale en el enunciado

    def analise_qsection(self, request):
        qname, carriage = qname_str(request)
        self.hostname = qname
        qtype, qtype_str = qtype_int(request[carriage:])
        print("qname is", qname)
        print("qtype is", qtype, qtype_str)


def log(hostname, ip):
    return datetime.datetime.utcnow().isoformat()+":: hostname "+hostname+" | ip "+ip+"\n"


def qname_str(request):
    i = 0
    ans = ""
    while True:
        length = struct.unpack("!B", request[i:i+1])
        length = int.from_bytes(length, byteorder='big')
        if length == 0:
            break

        i = i+1
        text = ""
        for j in range(i, i + length):
            c = struct.unpack("!B", request[j:j+1])
            text = text + str(chr(c[0]))

        if len(ans) > 0:
            ans = ans + "." + text
        else:
            ans = text

        i = i + length

    return ans, i + 1


def qtype_int(request):
    qtype = struct.unpack("!H", request[:2])
    qtype = int.from_bytes(qtype, byteorder='big')

    qtype_str = ""
    if qtype == 1:
        qtype_str = "A"
    elif qtype == 28:
        qtype_str = "AAAA"
    elif qtype == 15:
        qtype_str = "MX"

    return qtype, qtype_str


def binary_str(r, l):
    if type(r) != int:
        r = int.from_bytes(r, byteorder='big')
    ans = ""
    for i in range(l):
        ans = str(r % 2) + ans
        r = r // 2
    return ans


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
