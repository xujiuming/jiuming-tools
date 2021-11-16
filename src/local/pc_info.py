import asyncio
import os
import re
import subprocess

import click
import psutil


async def asyncGetScreenfetch():
    # 尝试执行 screenfetch
    try:
        res = await asyncio.create_subprocess_shell("screenfetch", stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        sout, serr = await res.communicate()
        # res.returncode, sout, serr, res.pid
        if res.returncode == 0:
            return sout.decode('utf-8')
    except OSError:
        return '安装screenfetch可以获得screenfetch图！'


def echo_pc_info():
    """
    输出 设备产品信息
    :return:
    """
    os_info = os.uname()
    # 获取当前系统虚拟化方式
    virtual_type_split_arr = str.split(subprocess.getoutput("lscpu | grep -E  '超管理器厂商|Hypervisor vendor'").strip(''))
    virtual_type_str = '无'
    if len(virtual_type_split_arr) == 2:
        virtual_type_str = virtual_type_split_arr[1]
    system_str = '''
操作系统:
  用户名:     {}
  主机名:     {}
  发行版本:   {}
  内核版本:   {}
  硬件架构:   {}
  虚拟化方式:  {}    
'''.format(
        os.getenv("USER"),
        os_info.nodename,
        subprocess.getoutput('cat /etc/issue').strip('\n'),
        os_info.release,
        os_info.machine,
        virtual_type_str if virtual_type_str is not None else "无"
    )
    click.echo(system_str)

    cpu_str = '''cpu信息:
  cpu型号:    {}
  cpu物理核心: {}
  cpu逻辑核心: {}
'''.format(
        cpu_info().modelName,
        psutil.cpu_count(logical=False),
        psutil.cpu_count()
    )
    click.echo(cpu_str)

    memory_str = '''内存信息:
{}
'''.format(subprocess.getoutput('free -h'))
    click.echo(memory_str)

    net_str = '''网卡信息:
{}    
'''.format(subprocess.getoutput('ip addr'))
    click.echo(net_str)

    disk_str = '''磁盘信息:
{}
'''.format(subprocess.getoutput('df -h'))
    click.echo(disk_str)

    # 异步执行 screenfetch
    loop = asyncio.get_event_loop()
    screenfetch_future = asyncio.ensure_future(asyncGetScreenfetch(), loop=loop)
    loop.run_until_complete(screenfetch_future)
    screenfetch_result = screenfetch_future.result()
    if screenfetch_future is not None:
        screenfetch_str = '''screenfetch:
        \r\n
        {}
        '''.format(str(screenfetch_result))
        click.echo(screenfetch_str)


def cpu_info():
    """
    从 /proc/cpuinfo 中读取cpu 模型名称
    :return:
    """
    f_cpu_info = open('/proc/cpuinfo', 'r')
    c = f_cpu_info.readlines()
    for i in c:
        tmp_str_list = i.split(':')
        if re.match(".*model.*name.*", tmp_str_list[0]):
            return cpuInfo(tmp_str_list[1].strip('\n').strip('\t'))


class cpuInfo(object):
    def __init__(self, modelName):
        self.modelName = modelName


def byteToGb(byteNumber):
    # b   kb     mb      gb
    return str(format(byteNumber / 1024 / 1024 / 1024, '.3'))



def detect():
    """
    探测服务器各项资源  
    all:所有资源
    cpu:cpu资源
    mem:内存资源
    inode:inode资源
    net:网络带宽、和端口、当前网络连接资源  
    file_desc:文件描述符资源  
    io:io资源  
    
    """
    detect_cpu()

def detect_cpu():
    click.echo(psutil.cpu_stats())
    pass
def detect_mem():
    v_mem =  psutil.virtual_memory()
    s_mem= psutil.swap_memory()
    mem_info ="""
    物理内存:{}/{},{}
    虚拟内存:{}/{},{}
    """.format(byteToGb(v_mem.total()),byteToGb(v_mem.used()),)
    click.echo(mem_info)
    pass
def detect_inode():
    pass
def detect_net():
    pass
def detect_file_desc():
    pass
def detect_io():
    pass


