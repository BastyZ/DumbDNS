import argparse
import socket as libsock
import random
import struct
import time

class Server:
    def __init__(self, port=1025, timeout=3600):
        # TODO things

if __name__ == "__main__":
    description = "a fucking damn dns"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-P', '--port',
                        help='Port used for the request.',
                        required=True)
    parser.add_argument('-C', '--cache',
                        help='Cache Timeout in [s], default value is 3600.',
                        type=int)

    args = parser.parse_args()

    port = args.port

    if args.cache_timeout:
        cache = args.cache_timeout
