from enum import IntEnum

from peewee import *

# 创建sqlite
from src.config.global_config import db_dir

db = SqliteDatabase(db_dir + '/tools.db')


# 定义peewee 元数据
class BaseModel(Model):
    class Meta:
        database = db


class MyTask(BaseModel):
    name = CharField()
    content = TextField()
    level = IntegerField()
    over = BooleanField()
    over_time = TimestampField()
    create_time = TimestampField()
    update_time = TimestampField()


class ServerConfig(BaseModel):
    """
    服务器配置表
    """
    # 名字
    name = CharField()
    # 地址
    host = CharField()
    # ssh端口
    port = IntegerField()
    # 服务器用户名
    username = CharField()
    # 认证方式 @link this#AuthType
    auth_type = IntegerField()
    # 密码
    password = CharField(null=True)
    # 密钥二进制内容
    secret_key_blob = BlobField(null=True)

    class AuthType(IntEnum):
        """
        服务器信息认证类型
        """
        # 密码方式
        PWD = 1
        # 秘钥模式
        SECRET = 2


# 链接数据库  和创建对应的表格
db.connect()
db.create_tables([ServerConfig])
