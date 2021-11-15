import tornado.ioloop
import tornado.web
import sys
import os, socket

from consul import Consul, Check

hostname = os.getenv('HOSTNAME') or socket.gethostname()
tags = os.getenv('TAGS', '').split(',')
consul_host = os.getenv('CONSUL_HOST', 'consul')
consul_port = int(os.getenv('CONSUL_PORT', 8500))
service_name = os.getenv('SERVICE_NAME', 'web')
service_ip = os.getenv('SERVICE_IP', socket.gethostbyname(hostname))
service_port = int(os.getenv('SERVICE_PORT', 8080))
service_id = os.getenv('SERVICE_ID') or "%s-%s-%s" % (service_name, hostname, service_port)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Container', hostname)
        self.finish("Hello, Service: " + hostname + "\n")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

def register():
    consul = Consul(host=consul_host, port=consul_port)
    check_url = 'http://%s:%s' % (hostname, service_port)
    checker = Check.http(check_url, "10s", deregister="10s")
    consul.agent.service.register(
        service_name, # service name. i.e: client-endpoint
        service_id=service_id, # instance name, one service could include multi instance
        address=service_ip, # instance address, make sure use ip address.
        port=int(service_port), # instance port
        check=checker, # health check
        tags=tags, #
    )

if __name__ == "__main__":
    register()

    app = make_app()
    app.listen(service_port)
    tornado.ioloop.IOLoop.current().start()
