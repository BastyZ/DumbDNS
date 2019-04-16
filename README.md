# Dumb DNS

## Basic usage
```
dumbdns.py [-h] [-P PORT] [-R RESOLVER] [-C CACHE] [-F FORWARD]
                  [-B BLOCKED]
```
a fucking damn dns
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

## Explanation (from subtitles)

En la tarea
