import re
from webob import Request,Response
from webob.dec import wsgify
from webob.exc import HTTPError
class Attrdict:
    def __init__(self,d:dict):

        self.__dict__.update(d if isinstance(d,dict) else {})  # 这个方法太损了，直接躲避过了下面的两个方法，但其实不好，不要这样

    def __setattr__(self, key, value):
        raise NotImplementedError

    def __repr__(self):
        return '<AttrDict {}>'.format(self.__dict__)

    def __len__(self):
        return len(self.__dict__)
class Router:

    _regex  = re.compile('/{([^{}:]+):?([^{}:]*)}')

    TYPEPATTERNS = {
        'str': r'[^/]+',
        'word': r'\w+',
        'int': r'[+-]?\d+',
        'float': r'[+-]?\d+\.\d+',
        'any': r'.+'
    }

    TYPECAST = {
        'str': str,
        'word': str,
        'int': int,
        'float': float,
        'any': str}

    def __parse(self,src:str):
        start = 0
        repl = ''
        types = {}


        matchers = self._regex.finditer(src)
        for i ,matcher in enumerate(matchers):
            name = matcher.group(1)
            t = matcher.group(2)

            types[name] = self.TYPECAST.get(matcher.group(2),str)

            repl += src[start:matcher.start()]
            tmp  = '/(?P<{}>{})'.format(
                matcher.group(1),
                self.TYPEPATTERNS.get(matcher.group(2),self.TYPEPATTERNS['str'])
            )

            repl += tmp

            start  = matcher.end()
        else:
            repl +=src[start:]

        return repl,types

    def __init__(self,prefix:str = ''):
        self._prefix = prefix.rstrip('/\\')
        self._routetable = [] # 这个路由表就不是类了，而是实例自己的

        self.pre_interceptor = []  #拦截分全局和独立的，这个明显是每个router实例自己的拦截器，你看位置就知道了，放到了实例下面。
        self.post_interceptor = []

        # 拦截器注册函数

    def register_preinterceptor(self, fn):
        self.pre_interceptor.append(fn)
        return fn

    def register_postinterceptor(self, fn):
        self.post_interceptor.append(fn)
        return fn

    def route(self,rule,*methods):
        def wrapper(handler):
            pattern,trans = self.__parse(rule)
            self._routetable.append(
                (tuple(map(lambda x:x.upper(),methods)),
                 re.compile(pattern),trans,handler)
            )
            return handler
        return wrapper

    def get(self,pattern):
        return self.route(pattern,'GET')

    def post(self,pattern):
        return self.route(pattern, 'POST')

    def head(self,pattern):
        return self.route(pattern, 'HEAD')

    def match(self,request:Request):
        if not request.path.startswith(self._prefix):
            return None  # 如果请求的前缀不匹配，那就直接return,后面就不会再执行了。


            # 是此Router的请求，开始拦截，处理request
        for fn in self.pre_interceptor:
            request = fn(request)
            if not request:
                return None  # 请求为None将不再向后传递，截止


        for methods, pattern,trans,handler in self._routetable:
            if not methods or request.method.upper() in methods:
                matcher = pattern.match(request.path.replace(self._prefix, '', 1))
                if matcher:
                    newdict = {}
                    for k,v in matcher.groupdict().items():
                        newdict[k] = trans[k](v)

                    request.vars = Attrdict(newdict)
                    response= handler(request)


                    for fn in self.post_interceptor:
                        response = fn(request, response)
                    return response

class App:
    _ROUTERS= []
    PRE_INTERCEPTOR = []  #这是全局拦截器。
    POST_INTERCEPTOR = []


    #全局拦截器注册函数。明显可以看出是定义在类上的，所以明显是全局的。
    @classmethod
    def register_preinterceptor(cls, fn):
        cls.PRE_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def register_postinterceptor(cls, fn):
        cls.POST_INTERCEPTOR.append(fn)
        return fn


    @classmethod
    def register(cls,*routers:Router):
        for router in routers:
            cls._ROUTERS.append(router)

    @wsgify
    def __call__(self, request):

        for fn in self.PRE_INTERCEPTOR:
            request = fn(request)


        for router in self._ROUTERS:
            response = router.match(request)

            for fn in self.POST_INTERCEPTOR:
                response = fn(request, response)

            if response:
                return response
        raise HTTPError('<h1>wrong not page</h1>')



