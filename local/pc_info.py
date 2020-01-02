import os
import re
import subprocess

import click
import psutil


def echo_pc_info():
    """
    输出 设备产品信息
    :return:
    """
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()
    os_info = os.uname()

    memory_info_str = '''
操作系统:
  主机名:     {}
  发行版本:   {}
  内核版本:   {}
  硬件架构:   {}
  
cpu信息:
  cpu型号:    {}
  cpu物理核心: {}
  cpu逻辑核心: {}
  
内存信息:
{}

磁盘信息:
{}
        '''.format(
        os_info.nodename,
        linux_issue(),
        os_info.release,
        os_info.machine,
        cpu_info().modelName,
        psutil.cpu_count(logical=False),
        psutil.cpu_count(),
        subprocess.getoutput('free -h'),
        subprocess.getoutput('df -h')
    )
    click.echo(memory_info_str)


def linux_issue():
    return subprocess.getoutput('cat /etc/issue').strip('\t').strip('\n')


def cpu_info():
    f_cpu_info = open('/proc/cpuinfo', 'r')
    c = f_cpu_info.readlines()
    for i in c:
        tmp_str_list = i.split(':')
        if re.match(".*model name.*", tmp_str_list[0]):
            return cpuInfo(tmp_str_list[1].strip('\n').strip('\t'))


class cpuInfo(object):
    def __init__(self, modelName):
        self.modelName = modelName


def byteToGb(byteNumber):
    # b   kb     mb      gb
    return str(format(byteNumber / 1024 / 1024 / 1024, '.3'))
