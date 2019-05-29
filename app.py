
from wsgiref.simple_server import make_server
from teststart.webarch import App
#这是一个入口函数，一切都是从这里开启，一定要先开启一个WEB 服务器，然后才有接下来的事情。
if __name__ == '__main__':

    ip = '127.0.0.1'
    port = 9999
    server = make_server(ip,port,App())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
#这只是学习版本，不能用来商用。
#有任何问题请联系坐着邮箱。
