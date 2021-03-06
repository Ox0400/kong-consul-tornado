### Start test

#### ports
##### consul
- 8502 for Admin UI page
- 8600 for DNS resolver (like :53)
##### web app
- 8080 target web app http port
##### kong
- 8000 endpoint for forward request to target web app
- 8001 endpoint for admin manage services & routes
- 8002 for admin UI page


#### set envs

```
# for dns resolver
# LAN IP address
export HOST_MACHINE_IP=172.31.36.146
export HOST_NET_IP=`curl ip.sb` # could reuse HOST_MACHINE_IP
# service name
# export SERVICE_NAME=web
```

#### start services

```
# start pgsql & consul
docker-compose up -d consul pgsql

# start setup for kong & web apps (two instance)
docker-compose up -d setup web1 web2

# config consul dns resolver address
# access consul use container ip. https://github.com/moby/moby/issues/11998
# suggest deploy consul with host network_mode if want start kong with consul's lan ip.
export CONSUL_LAN_IP=`docker-compose exec consul hostname -i | tr -d '\r'`
# dig @172.31.36.146  -p 8600 web.service.dc1.consul. SRV
# dig @192.168.240.1  -p 8600 web.service.dc1.consul. A
docker-compose up -d kong # start kong

```

### test forward to web server(consul dns resolver)

#### registry test web app, forward request to multi servers
> `web.service.consul` is consul service name (DNS CNAME). format: `$ServiceName.service.consul`

```bash
curl "http://$HOST_MACHINE_IP:8001/default/services" \
  -H 'Content-Type: application/json;charset=UTF-8' \
  --data-raw '{"name":"web1-srv","host":"web1.service.dc1.consul.", "port": 8080}'

```bash

#### set route for web app
```bash
curl "http://$HOST_MACHINE_IP:8001/default/services/web1-srv/routes" \
  -H 'Content-Type: application/json;charset=UTF-8' \
  --data-raw '{"name":"web1-srv-route","protocols":["http","https"],"paths":["/srv/web1.app"]}'

```

#### test call web app
```bash
curl http://$HOST_MACHINE_IP:8000/srv/web1.app
# Hello, Service: 9dbf4260e86c
# Hello, Service: 4d3e162d7f9a

# HTTP/1.1 200 OK
# Content-Type: text/html; charset=UTF-8
# Content-Length: 29
# Connection: keep-alive
# Server: TornadoServer/6.1
# Date: Mon, 15 Nov 2021 17:10:49 GMT
# Container: 4d3e162d7f9a
# Etag: "be5efb9df8e6ddc4491a52c52417aa9acc0c8615"
# X-Kong-Upstream-Latency: 1
# X-Kong-Proxy-Latency: 2
# Via: kong/2.6.0.0-enterprise-edition
```


### test forward to a exists http service
#### registry a google app, forward request to google.com
> Suppose is frontend

```
curl "http://$HOST_MACHINE_IP:8001/default/services" \
  -H 'Content-Type: application/json;charset=UTF-8' \
  --data-raw '{"name":"google-srv","url":"https://www.google.com"}'
```

#### set route for google app
```
curl "http://$HOST_MACHINE_IP:8001/default/services/google-srv/routes" \
  -H 'Content-Type: application/json;charset=UTF-8' \
  --data-raw '{"name":"google-srv-route","protocols":["http","https"],"paths":["/srv/google.app"]}'
```

```
curl -i -X GET   --url http://$HOST_MACHINE_IP:8000/srv/google.app
```
