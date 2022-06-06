class DbConfig(object):
    """
    数据库配置对象
    """
    # 名字
    name: str
    # 地址
    host: str
    # 端口
    port: int
    # 服务器用户名
    username: str
    # 密码
    password: str
    # 密钥位置
    secret_key_path: str
    # 数据库类型
    db_type: str

    def __init__(self, name, host, port, username, password, secret_key_path):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.secret_key_path = secret_key_path

    @staticmethod
    def to_obj(d: dict):
        """
        将读取的dict 转换为 serverConfig
        :param d:  dict
        :return: ServerConfig
        """
        return ServerConfig(name=d['name'], host=d['host'], port=d['port'], username=d['username'],
                            password=d['password'], secret_key_path=d.get('secret_key_path', None))
