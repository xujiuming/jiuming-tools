# 默认配置路径
import copy
import os
import pathlib
import shutil

import click
import pexpect
import yaml

from src.config.global_config import config_default_file, private_key_default_file

# 默认配置file
server_config_default_file = config_default_file + '/server_config.yaml'


def server_add(name, host, port, username, password, path):
    """
    添加服务配置
    :param name: 服务器名称
    :param host: 服务器地址
    :param port: 服务器ssh端口
    :param username: 服务器用户名
    :param password: 服务器用户密码
    :param path: 文件地址
    :return:
    """
    secretKeyPath = None
    if path is not None:
        if os.path.exists(path) and os.path.isfile(path):
            # 计算密钥地址
            secretKeyPath = private_key_default_file + '/{}_{}_{}.id_rsa'.format(name, username, host)
            # 复制密钥到配置目录命名规则 服务器名_用户名_host地址
            shutil.copyfile(path, secretKeyPath)
        else:
            raise click.FileError('保存密钥异常！未找到密钥或者无权限')
    # 追加模式
    y_file = open(server_config_default_file, 'a+')
    sc = ServerConfig(name=name, host=host, port=port, username=username, password=password,
                      secretKeyPath=secretKeyPath)
    yaml.safe_dump([sc.__dict__], y_file)
    click.echo('\n录入的服务器信息:\n名称:{}\n地址:{}\nssh端口:{}'.format(name, host, port))


def server_edit():
    os.system('vi {}'.format(server_config_default_file))


def server_remove(name):
    """
    删除服务器配置信息
    获取所有配置  删除其中name符合的数据
    :param name: 服务器名称
    :return:
    """
    y_read_file = open(server_config_default_file, 'r')
    config_list = yaml.safe_load(y_read_file)
    if config_list is None:
        click.echo("暂无服务器配置信息!")
        return
    # 深拷贝 配置列表 进行操作列表
    new_config_list = copy.deepcopy(config_list)
    for c in config_list:
        sc = ServerConfig.to_obj(c)
        if sc.name == name:
            new_config_list.remove(c)
            click.echo("删除{}服务器".format(sc.name))
    # 重新打开链接
    if len(new_config_list) != 0:
        yaml.safe_dump(new_config_list, open(server_config_default_file, 'w+'))
    else:
        # 清空配置
        open(server_config_default_file, 'w+').truncate()
        click.echo("服务器配置已清空!")


def server_list():
    config_file = pathlib.Path(server_config_default_file)
    if not config_file.exists():
        click.echo("暂无服务器配置信息！")
        return
    if not config_file.is_file():
        click.echo("{}不是配置文件".format(server_config_default_file))
        return
    y_read_file = open(server_config_default_file, 'r')
    config_list = yaml.safe_load(y_read_file)
    if config_list is None:
        click.echo("暂无服务器配置信息!")
        return
    config_str = '服务器配置信息:\n'
    for index, c in enumerate(config_list):
        sc = ServerConfig.to_obj(c)
        config_str += '第{}台服务器名称:{},地址:{},端口:{}'.format(index + 1, sc.name, sc.host, str(sc.port) + '\n')
    config_str += "\n共{}台服务器\n".format(len(config_list))
    click.echo(config_str)


def server_connect(name):
    click.echo("连接{}服务器...".format(name))
    config_list = yaml.safe_load(open(server_config_default_file, 'r'))
    if config_list is None:
        click.echo("暂无{}服务器配置信息!".format(name))
        return
    connect_sc = None
    for c in config_list:
        sc = ServerConfig.to_obj(c)
        if sc.name == name:
            connect_sc = sc
            break
    if connect_sc is None:
        click.echo("不存在{}服务器配置！".format(name))
        return
    open_ssh_tty(connect_sc.host, connect_sc.port, connect_sc.username, connect_sc.password)


def open_ssh_tty(host, port, username, password):
    cmd = 'ssh -o StrictHostKeyChecking=no  -p {} {}@{}'.format(port, username, host)
    p_ssh = pexpect.spawn(command=cmd)
    # 输入密码
    p_ssh.expect("password:")
    p_ssh.sendline(password)
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_ssh.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示终端
    p_ssh.interact()


def server_sftp(name, cwd_path):
    click.echo("连接{}服务器sftp服务...".format(name))
    config_list = yaml.safe_load(open(server_config_default_file, 'r'))
    if config_list is None:
        click.echo("暂无{}服务器配置信息!".format(name))
        return
    connect_sc = None
    for c in config_list:
        sc = ServerConfig.to_obj(c)
        if sc.name == name:
            connect_sc = sc
            break
    if connect_sc is None:
        click.echo("不存在{}服务器配置！".format(name))
        return
    # 执行sftp命令
    cmd = 'sftp -P {} {}@{}'.format(connect_sc.port, connect_sc.username, connect_sc.host)
    p_sftp = pexpect.spawn(command=cmd, cwd=cwd_path)
    # 输入密码
    p_sftp.expect("password:")
    p_sftp.sendline(connect_sc.password)
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_sftp.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示sftp终端
    p_sftp.interact()


class ServerConfig(object):
    """
    服务器配置模板class
    """
    # 名字
    name: str
    # 地址
    host: str
    # ssh端口
    port: int
    # 服务器用户名
    username: str
    # 密码
    password: str
    # 密钥位置
    secretKeyPath: str

    def __init__(self, name, host, port, username, password, secretKeyPath):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.secretKeyPath = secretKeyPath

    @staticmethod
    def to_obj(d: dict):
        """
        将读取的dict 转换为 serverConfig
        :param d:  dict
        :return: ServerConfig
        """
        return ServerConfig(name=d['name'], host=d['host'], port=d['port'], username=d['username'],
                            password=d['password'], secretKeyPath=d['secretKeyPath'])
