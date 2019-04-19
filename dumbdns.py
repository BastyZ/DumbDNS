import argparse
import json
import socket as libsock
import struct
import datetime
import errno
import sys
from ast import literal_eval

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
        self.qtype = ""
        self.response = ""
        self.cache = {}
        self.addr = ""

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
            self.qtype = ""
            request, address = socket.recvfrom(1024)
            self.address = address
            self.addr = address[0]+":"+str(address[1])
            print("Received:\n", request)

            # Parse Request
            self.analise_header(request)
            offset = self.analise_qsection(request[12:])  # req without header

            # Lookup on Cache
            try:
                self.get_cache()
            except FileNotFoundError:
                self.write_cache()

            if self.cache and self.cache[self.hostname] and self.cache[self.hostname][self.qtype]    \
                    and self.cache[self.hostname][self.qtype]["time"] + self.timeout > datetime.datetime.utcnow():
                print("Cache used with", self.hostname)
                cache = self.cache[self.hostname][self.qtype]
                self.ip = cache["ip"]
                self.log(cached=True)
                socket.sendto(request[:2] + self.cache[self.hostname][self.qtype]["response"][2:], address)
                continue

            # Block like Terry Crews
            if blocked and self.hostname in blocked["names"]:
                self.log(blocked=True)
                continue

            # Ask to DNS server
            self.response = self.dns_query(request)
            # Parse Response
            self.analise_rsection(self.response[12 + offset:])

            # Check FWD
            if forward and self.hostname in forward:
                self.forward_dns(forward[self.hostname], offset)
                self.log(filtered=True)
                # Add to cache
                if not self.cache or not self.cache[self.hostname]:
                    self.cache[self.hostname] = dict()
                self.cache[self.hostname][self.qtype] = dict(response="".join(map(chr, self.response)),
                                                             time=str(datetime.datetime.utcnow()), ip=forward[self.hostname])
                self.write_cache()
                socket.sendto(self.response, self.address)
                continue

            # Make log in file
            self.log()

            # Write to Cache
            if not self.cache or not self.cache[self.hostname]:
                self.cache[self.hostname] = dict()
            self.cache[self.hostname][self.qtype] = dict(response=str("".join(map(chr, self.response))),
                                                         time=str(datetime.datetime.utcnow()), ip=self.ip)
            self.write_cache()
            # send response
            socket.sendto(self.response, address)

    def forward_dns(self, new_ip, offset):
        print("Forwarding")
        if self.qtype != "MX":
            pointer = struct.unpack("!H", self.response[12 + offset:14 + offset])
            advance = 12 if binary_str(pointer[0], 16)[:2] == "11" else qname_str(self.response[12 + offset:])[1] + 10
            self.response = self.response[:12 + offset + advance] + ip_to_bytes(new_ip) \
                            + self.response[12 + offset + advance + (4 if self.qtype == "A" else 6):]

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
        qtype, qtype_str = qtype_int(request[carriage:])
        self.hostname = qname
        self.qtype = qtype_str
        print("qname is", qname)
        print("qtype is", qtype, qtype_str)
        return carriage + 4  # +4 por qtype y qclass

    def analise_rsection(self, r_section):
        pointer = struct.unpack("!H", r_section[:2])
        if binary_str(pointer[0], 16)[:2] == "11":
            # Hay un puntero y morimos conchetumadre
            offset = binary_str(pointer[0], 16)[2:]
            print("el offset es", offset)
            offset = int_f_binary_str(offset)
            print("el offset ahora es", offset)
            qname, useless = qname_str(self.response[offset:])
            print("el sitio es:", qname)
            advance = 2
        else:
            # lo mismo que en el qsection
            qname, carriage = qname_str(r_section)
            advance = carriage
        rtype, rclass, ttl, rdlength = struct.unpack("!2HLH", r_section[advance:advance + 10])
        ip1, ip2, ip3, ip4 = struct.unpack("!4B", r_section[advance + 10:advance + 10 + rdlength])
        print(ip1, ip2, ip3, ip4)
        self.ip = str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)

    def log(self, cached=False, blocked=False, filtered=False):
        with open("log.txt", "a", encoding="utf-8") as file:
            try:
                file.write(log(self.addr, self.hostname, self.ip, self.qtype, cached, blocked, filtered))
            except Exception as e:
                print("ERROR: cannot write on log.txt", e)
            finally:
                file.close()

    def write_cache(self):
        with open("cache.json", "w", encoding="utf-8") as file:
            try:
                json.dump(self.cache, file)
            except Exception as e:
                print("ERROR: problem while writing cache.json", e)
            finally:
                file.close()

    def get_cache(self):
        with open("cache.json", "r", encoding="utf-8") as file:
            try:
                self.cache = json.load(file)
                for hostname in self.cache:
                    for qtype in self.cache[hostname]:
                        self.cache[hostname][qtype]["time"] = datetime.datetime.strptime(self.cache[hostname][qtype]["time"],
                                                                                         "%Y-%m-%d %H:%M:%S.%fZ")
                        self.cache[hostname][qtype]["response"] = bytes(self.cache[hostname][qtype]["response"], 'utf-8')
            except ValueError as e:
                print("No cache or invalid JSON:", e)
                self.cache = {}
            finally:
                file.close()


def log(address, hostname, ip, qtype, cached=False, blocked=False, filtered=False):
    return datetime.datetime.utcnow().isoformat() + " :: client " + address + " hostname " + hostname + " | " + qtype \
           + " | ip " + ip + (" :: cached answer" if cached else "") + (" :: blocked answer" if blocked else "") \
           + (" :: filtered answer" if filtered else "") + "\n"


def ip_to_bytes(ip):
    print(" gonna write ", ip)
    arr = ip.split('.')
    ans = list()
    for num in arr:
        ans.append(int(num))
    return bytearray(ans)


def qname_str(request):
    i = 0
    ans = ""
    while True:
        length = struct.unpack("!B", request[i:i + 1])
        length = int.from_bytes(length, byteorder='big')
        if length == 0:
            break

        i = i + 1
        text = ""
        for j in range(i, i + length):
            c = struct.unpack("!B", request[j:j + 1])
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


def int_f_binary_str(b):
    ans = 0
    carry = 1
    for i in range(len(b) - 1, -1, -1):
        ans = ans + (carry if b[i] == '1' else 0)
        carry = carry * 2
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
    Server(port, resolver, datetime.timedelta(seconds=cache_timeout), forward, blocked)


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
                        help='JSON containing names/domains used to be forwarded to another IP \n'
                             + ' with format {"page": "ip"} ')
    parser.add_argument('-B', '--blocked',
                        help='JSON containing names/domains that will not receive a response\n'
                            + 'with format {"names": [page1, page2, ...]}')

    main(parser.parse_args())
