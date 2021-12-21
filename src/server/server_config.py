# 默认配置路径
import copy
import os
import pathlib
import shutil
import socket
import time

import click
import pexpect
import psutil
import yaml

from src.config.global_config import config_default_file, private_key_default_file, compile_ip, compile_host_mame, \
    compile_tun_value

# 默认配置file
server_config_default_file = config_default_file + '/server_config.yaml'


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
                            password=d['password'], secretKeyPath=d.get('secretKeyPath', None))


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
    name = name.strip()
    secretKeyPath = None
    if path is not None:
        abs_path = path
        # 处理用户目录
        if str(path).startswith('~'):
            abs_path = str(path).replace('~', os.path.expanduser('~'))
        click.echo(abs_path)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            # 计算密钥地址
            secretKeyPath = private_key_default_file + '/{}_{}.id_rsa'.format(name, username)
            click.echo(abs_path + '00' + secretKeyPath)
            # 复制密钥到配置目录命名规则 服务器名_用户名_host地址
            shutil.copyfile(abs_path, secretKeyPath)
        else:
            raise click.FileError('保存密钥异常！未找到密钥或者无权限')
    # 追加模式
    y_file = open(server_config_default_file, 'a+')
    sc = ServerConfig(name=name, host=host, port=port, username=username, password=password,
                      secretKeyPath=secretKeyPath)
    yaml.safe_dump([sc.__dict__], y_file)
    echo_str = '\n录入的服务器信息:\n名称:{}\n地址:{}\nssh端口:{}'.format(name, host, port)
    if secretKeyPath is not None:
        echo_str += '\n密钥地址:{}'.format(secretKeyPath)
    click.echo(echo_str)


def server_edit():
    os.system('vi {}'.format(server_config_default_file))


def server_remove(name):
    """
    删除服务器配置信息
    获取所有配置  删除其中name符合的数据
    :param name: 服务器名称
    :return:
    """
    name = name.strip()
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
            if sc.secretKeyPath is not None:
                os.remove(sc.secretKeyPath)
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
        config_str += '第{}台服务器名称:{},地址:{},端口:{}'.format(index + 1, sc.name, sc.host, str(sc.port))
        if sc.secretKeyPath is not None:
            config_str = config_str + ',密钥地址:{}'.format(sc.secretKeyPath)
        config_str = config_str + '\n'
    config_str += "\n共{}台服务器\n".format(len(config_list))
    click.echo(config_str)


def server_connect(name):
    name = name.strip()
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
    # 如果存在密钥 优先使用密钥登录服务器
    if connect_sc.secretKeyPath is not None:
        open_ssh_secret_key_tty(connect_sc.host, connect_sc.port, connect_sc.username, connect_sc.secretKeyPath)
    else:
        open_ssh_password_tty(connect_sc.host, connect_sc.port, connect_sc.username, connect_sc.password)


def open_ssh_secret_key_tty(host, port, username, secretKeyPath):
    cmd = 'ssh -o StrictHostKeyChecking=no -i {}  -p {} {}@{}'.format(secretKeyPath, port, username, host)
    # 授权600
    os.chmod(secretKeyPath, 0o600)
    p_ssh = pexpect.spawn(command=cmd)
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_ssh.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示终端
    p_ssh.interact()


def open_ssh_password_tty(host, port, username, password):
    cmd = 'ssh -o StrictHostKeyChecking=no  -p {} {}@{}'.format(port, username, host)
    p_ssh = pexpect.spawn(command=cmd)
    # 输入密码
    try:
        p_ssh.expect("password:", timeout=3)
        p_ssh.sendline(password)
    except pexpect.exceptions.TIMEOUT:
        click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_ssh.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示终端
    p_ssh.interact()


def server_sftp(name, cwd_path):
    name = name.strip()
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
    if connect_sc.secretKeyPath is not None:
        open_sftp_secret_key_tty(connect_sc.host, connect_sc.port, connect_sc.username, connect_sc.secretKeyPath,
                                 cwd_path)
    else:
        open_sftp_password_tty(connect_sc.host, connect_sc.port, connect_sc.username, connect_sc.password, cwd_path)


def open_sftp_password_tty(host, port, username, password, cwd_path):
    # 执行sftp命令
    cmd = 'sftp -o StrictHostKeyChecking=no -P {} {}@{}'.format(port, username, host)
    p_sftp = pexpect.spawn(command=cmd, cwd=cwd_path)
    # 输入密码
    # 输入密码
    try:
        p_sftp.expect("password:", timeout=3)
        p_sftp.sendline(password)
    except pexpect.exceptions.TIMEOUT:
        click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_sftp.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示sftp终端
    p_sftp.interact()


def open_sftp_secret_key_tty(host, port, username, secret_key_path, cwd_path):
    # 执行sftp命令
    cmd = 'sftp -o StrictHostKeyChecking=no -i {} -P {} {}@{}'.format(secret_key_path, port, username, host)
    p_sftp = pexpect.spawn(command=cmd, cwd=cwd_path)
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_sftp.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示sftp终端
    p_sftp.interact()


def ping_ssh_server(name_arr):
    """
     检查 列表中的 server是否存活
    """
    config_list = yaml.safe_load(open(server_config_default_file, 'r'))
    if config_list is None:
        click.echo("暂无服务器配置信息!")
        return
    for c in config_list:
        sc = ServerConfig.to_obj(c)
        if name_arr is None:
            if sc is not None:
                # 执行探测操作
                start_time = time.perf_counter_ns()
                r = open_socket_ssh_server(sc.host, sc.port)
                end_time = time.perf_counter_ns()
                result = "{},探测结果:{},耗时:{}ms".format(sc.host + ":" + str(sc.port), r,
                                                     str(round((int(round((end_time - start_time) / 1000000))), 2)))
                click.echo(result)
        else:
            sc = ServerConfig.to_obj(c)
            if sc is not None:
                # 如用户传入 name_arr 只测试传入的列表
                if list(name_arr).__contains__(sc.name):
                    # 执行探测操作
                    start_time = time.perf_counter_ns()
                    r = open_socket_ssh_server(sc.host, sc.port)
                    end_time = time.perf_counter_ns()
                    result = "{},探测结果:{},耗时:{}ms".format(sc.host + ":" + str(sc.port), r,
                                                         str(round((int(round((end_time - start_time) / 1000000))), 2)))
                    click.echo(result)


def open_socket_ssh_server(host, port):
    try:
        remote_ip = host
        if compile_host_mame.match(host):
            remote_ip = socket.gethostbyname(host)
        elif compile_ip.match(host):
            remote_ip = socket.gethostbyaddr(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((remote_ip, port))
        sock.close()
        return True
    except socket.error as e:
        click.echo("{}的{}端口连接失败,原因:{}".format(host, port, e))
        return False


def server_tun(left, right, reverse, name):
    config_list = yaml.safe_load(open(server_config_default_file, 'r'))
    if config_list is None:
        click.echo("暂无服务器配置信息!")
        return
    sc = None
    for c in config_list:
        sc = ServerConfig.to_obj(c)
        if sc.name == name:
            break

    if reverse:
        cmd_str = 'ssh -CqTnN -R {} -p {} {}'.format('{}:{}'.format(get_server_config_tun_info(sc, right), left),
                                                     str(sc.port),
                                                     '{}@{}'.format(sc.username, sc.host))
        click.echo(cmd_str)
        auto_open_tun(cmd_str, sc.password)
    else:
        cmd_str = 'ssh -CqTnN -L {} -p {} {}'.format('{}:{}'.format(left, get_server_config_tun_info(sc, right)),
                                                     str(sc.port),
                                                     '{}@{}'.format(sc.username, sc.host))
        click.echo(cmd_str)
        auto_open_tun(cmd_str, sc.password)


def auto_open_tun(cmd_str, password):
    """
    自动打开 tun通道   当断开之后重连
    """
    p_tun = pexpect.spawn(command=cmd_str, cwd=".")
    # 输入密码
    try:
        p_tun.expect("password:", timeout=3)
        p_tun.sendline(password)
    except pexpect.exceptions.TIMEOUT:
        click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
    pid = p_tun.pid
    click.echo(pid)
    while True:
        if not psutil.pid_exists(pid):
            p_tun = pexpect.spawn(command=cmd_str, cwd=".")
            # 输入密码
            try:
                p_tun.expect("password:", timeout=3)
                p_tun.sendline(password)
            except pexpect.exceptions.TIMEOUT:
                click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
            pid = p_tun.pid
            click.echo("重连tun通道,PID:{}", pid)
        # 休眠200ms
        time.sleep(0.2)


def get_server_config_tun_info(sc: ServerConfig, tun_str):
    if compile_tun_value.match(tun_str):
        return tun_str
    else:
        return '{}:{}'.format(sc.host, sc.port)


def server_select_connect():
    # 获取服务器列表 增加编号
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
    config_str = '服务器信息:\n'
    index_name_map = {}
    for index, c in enumerate(config_list):
        sc = ServerConfig.to_obj(c)
        index_name_map[str(index + 1)] = sc.name
        config_str += '{})台服务器名称:{},地址:{},端口:{}\n'.format(index + 1, sc.name, sc.host, str(sc.port))

    click.echo(config_str)

    # 等待用户输入服务器编号
    r = click.prompt(
        "选择服务器编号:",
        type=click.Choice(index_name_map.keys()),
        show_default=False,
    )
    server_connect(index_name_map[r])
