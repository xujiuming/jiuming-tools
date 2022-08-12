from peewee import *

# 创建sqllite
db = SqliteDatabase('my_database.db')


# 定义peewee 元数据
class BaseModel(Model):
    class Meta:
        database = db


class Staff(BaseModel):
    username = CharField(unique=True)


if __name__ == '__main__':
    db.connect()
    db.table_exists(Staff)
    db.create_tables([Staff])
    print( db.get_tables())
    print( db.get_columns('staff'))
    # t = Staff(username='ming')
    # t.save()
    l = Staff.select()
    for i in l:
        print(i.username)
