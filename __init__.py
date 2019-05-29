from webob import Response,Request
from .web import Router,App

idx  = Router()
py = Router('/python')
user = Router('/user')

App.register(idx,py)
App.register(user)


# ip拦截
def ip(request: Request):
    print(request.remote_addr, '~~~~~~~~~~~~~~~')
    print(type(request.remote_addr))
    if request.remote_addr.startswith('192.'):
        return request
    else:
        return None  # 返回None将截断请求
py.register_preinterceptor(ip)

@idx.get(r'^/$')
@idx.route(r'^/{id:int}$')
def indexhandler(request): #indexhandler = wrapper(handler)
    # print(request.groups)
    # print(request.groupdict)
    id = ''
    if request.vars:
        id = request.vars.id
        print(type(id))
    return '<h1>indexwang{}</h1>'.format(id)


@py.get('^/{id}$')
def pythonhandler(request):
    if request.vars:
        print(type(request.vars.id))


    return '<h1>fuckpython!!!!!!</h1>'


@user.get(r'^/?$')
def userhandler(request):
    userlist = [ (3,'tom',20),
    (7,'jerry',27)]

    d = {'userlist':userlist,'usercount':len(userlist)}
    res = Response(json=d)   #可以返回一个json 格式的序列。
    return res
    # return render('index.html',d)