import time

import click

from src.config.peewee_config import MyTask


def create(name, content, level):
    t = MyTask(name=name, content=content, level=level, over=False, create_time=time.time(),
               update_time=time.time())
    t.save()
    click.echo("创建{}任务成功!".format(t.name))


def list(model, date, search):
    print(model, date, search)
    expressions = None
    if str(model).upper() == 'FALSE':
        expressions = (MyTask.over == False)
    elif str(model).upper() == 'TRUE':
        expressions = (MyTask.over == True)

    if date is not None:
        expressions = expressions & MyTask.create_time >= date

    if search is not None:
        search = '%{}%'.format(search)
        expressions = expressions & (MyTask.name ** search | MyTask.content ** search)

    t_list = MyTask.select().where(expressions)
    for t in t_list:
        s = """
id:{}
名称:{}
内容:{}
等级:{}        
        """.format(t.id, t.name, t.content, t.level)
        click.echo(s)


def over(id):
    MyTask.update({MyTask.over: True}).where(MyTask.id == id).execute()
    click.echo("{}任务已完成!".format(id))


def remove(id):
    MyTask.delete_by_id(id)
    click.echo("{}任务已删除!".format(id))
