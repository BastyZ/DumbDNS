# Dumb DNS

The project contains a basic DNS proxy, with caching, blocking and filtering capabilities, made on the context of
CC4303 Course "Redes" at the University of Chile. We are based on examples given on the course and on 
[RFC 1035](https://www.ietf.org/rfc/rfc1035.txt) from IETF.

## Basic usage
```
dumbdns.py [-h] [-P PORT] [-R RESOLVER] [-C CACHE] [-F FORWARD]
                  [-B BLOCKED]
```
a fucking damn dns that receives the following parameters:
```
optional arguments:
  -h, --help            show this help message and exit
  -P PORT, --port PORT  Port used for the request. Default port is 1025
  -R RESOLVER, --resolver RESOLVER
                        Resolver to get an actual answer
  -C CACHE, --cache CACHE
                        Cache Timeout in [s], default value is 3600.
  -F FORWARD, --forward FORWARD
                        JSON containing names/domains used to be forwarded to
                        another IP with format {"page": "ip"}
  -B BLOCKED, --blocked BLOCKED
                        JSON containing names/domains that will not receive a
                        response with format {"names": [page1, page2, ...]}
```

all this are optionals, but by default comes with `-P 1025 -R 1.1.1.1 -C 3600`, forward and blocked JSONs are not
requiered to run this proxy.

## Explanation and assumptions (from spanish subtitles)

En la tarea el servidor atiende todas las consultas en el mismo thread, y atiende preguntas en nombre de un resolver
a elección seteado al momento de correr el servidor. Al recibir una consulta se realiza un parseo de esta, extrayendo
información relevante de esta, con 
