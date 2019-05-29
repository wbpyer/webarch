
from wsgiref.simple_server import make_server
from teststart.webarch import App
if __name__ == '__main__':

    ip = '127.0.0.1'
    port = 9999
    server = make_server(ip,port,App())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()