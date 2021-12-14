import datetime

import click


class TodoConfig(object):
    """
    todo任务配置对象
    """
    # 名字
    name: str
    # 地址
    content: str
    # 完结时间
    over_time: datetime
    # 创建时间
    create_time: datetime

    def __init__(self, name, content, over_time, create_time):
        self.name = name
        self.content = content
        self.over_time = over_time
        self.create_time = create_time

    @staticmethod
    def to_obj(d: dict):
        """
        将读取的dict 转换为 serverConfig
        :param d:  dict
        :return: ServerConfig
        """
        return TodoConfig(name=d['name'], content=d['content'], over_time=d.get("over_time", None),
                          create_time=d['create_time'])


def create(name, content):
    tc = TodoConfig(name=name, content=content, over_time=None, create_time=datetime.datetime)
    click.echo(tc)
