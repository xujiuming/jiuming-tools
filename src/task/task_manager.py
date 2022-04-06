import time

import click

from src.config.peewee_config import MyTask


def create(name, content, level):
    t = MyTask(name=name, content=content, level=level, over=False, create_time=time.time(),
               update_time=time.time())
    t.save()
    click.echo("创建{}任务成功!".format(t.name))


def list():
    t_list = MyTask.select()
    for i, t in enumerate(t_list):
        click.echo("{}:[{}任务:{},是否完成:{}]".format(i, t.name, t.content, t.over))
