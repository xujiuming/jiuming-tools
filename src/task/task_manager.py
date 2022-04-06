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
    for t in t_list:
        click.echo("{}:[{}任务:{},是否完成:{}]".format(t.id, t.name, t.content, t.over))


def over(id):
    MyTask.update({MyTask.over: True}).where(MyTask.id == id).execute()
    click.echo("{}任务已完成!".format(id))


def remove(id):
    MyTask.delete_by_id(id)
    click.echo("{}任务已删除!".format(id))
