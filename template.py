

from jinja2 import Environment,PackageLoader,FileSystemLoader
#env = Environment(loader=PackageLoader('webarch', 'templates')) # 包加载器
env = Environment(loader=FileSystemLoader('webarch/templates'))
def render(name,data:dict):
    """

    :param name:
    :param data:
    :return:
    """
    template = env.get_template(name)
    return template.render(**data)