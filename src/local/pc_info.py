import asyncio
import json
import os
import re
import subprocess

import click
import psutil
from prettytable import PrettyTable

from src.utils.convertUtils import byte_length_format


async def async_get_screenfetch():
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
    virtual_type_split_arr = str.split(
        subprocess.getoutput("lscpu | grep -E  '超管理器厂商|Hypervisor vendor'").strip(''))
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
    cpu_load_str = '''cpu当前负载信息:
{}    
'''.format(subprocess.getoutput('mpstat -P ALL'))
    click.echo(cpu_load_str)

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

    inode_str = '''inode使用信息:
{}    
'''.format(subprocess.getoutput('df -ih'))
    click.echo(inode_str)

    ss_str = '''socket使用摘要统计信息:
{}    
'''.format(subprocess.getoutput('ss -s '))
    click.echo(ss_str)

    # 异步执行 screenfetch
    loop = asyncio.get_event_loop()
    screenfetch_future = asyncio.ensure_future(async_get_screenfetch(), loop=loop)
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


def pid_info(pid, details):
    """
    使用psutil 探测指定pid的综合信息 方便判断问题节点
    https://psutil.readthedocs.io/en/latest/#process-class
    获取对应id的进程综合信息
    cpu、内存、磁盘、文件描述符等等信息
    :return:
    """
    p = psutil.Process(pid)
    file_mem_map_info_str = ""
    for m in p.memory_maps():
        file_mem_map_info_str = file_mem_map_info_str + "\r\n" + m[0] + "使用rss:{},size:{}".format(
            byte_length_format(m[1]),
            byte_length_format(m[2]))

    mem_full_info = p.memory_full_info()
    mem_full_info_str = "使用总内存大小{},swap大小{}".format(byte_length_format(mem_full_info[8]),
                                                             byte_length_format(mem_full_info[9]))

    base_str = """
PID:{}
name:{}    
执行用户:{}
进程可执行文件路径:{}
进程使用的内存大小信息:{}
内存引用文件占用内存信息:{}
此进程当前打开的文件描述符数:{}
此进程当前使用的线程数:{}
此进程和总物理内存比例:{}
进程打开的套接字连接:{}
""".format(p.pid,
           p.name(),
           p.username(),
           p.exe(),
           mem_full_info_str,
           file_mem_map_info_str,
           p.num_fds(),
           p.num_threads(),
           p.memory_percent(),
           p.connections()
           )
    click.echo(base_str)
    if details:
        click.echo("详细信息:\r\n" + json.dumps(p.as_dict(), indent=1, separators=(', ', ': '), ensure_ascii=False))


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
    detect_mem()


def detect_cpu():
    cpu_load_arr = psutil.cpu_percent(3, True)
    click.echo("cpu负载信息:")
    for i, c in enumerate(cpu_load_arr):
        click.echo("第{}个cpu负载:{}".format(i, c))
    click.echo("总负载:{}".format(sum(cpu_load_arr)))


def detect_mem():
    v_mem = psutil.virtual_memory()
    s_mem = psutil.swap_memory()
    mem_info = """
    物理内存:{}/{},{}
    虚拟内存:{}/{},{}
    """.format(byte_length_format(v_mem.used()), byte_length_format(v_mem.total()), 0, byte_length_format(s_mem.used),
               byte_length_format(s_mem.total), 0)
    click.echo(mem_info)


def detect_inode():
    pass


def detect_net():
    pass


def detect_file_desc():
    pass


def detect_io():
    pass


def mem_info(top, pid, details):
    p_arr = []
    if pid is not None:
        p_arr.append(psutil.Process(pid))
    else:
        for p in psutil.process_iter():
            p_arr.append(p)

    mem_info_arr = []
    for p in p_arr:
        for m in p.memory_maps():
            mem_info_arr.append(m)

    # 过滤 anon  heap  stack 数据
    mem_info_arr = [t for t in mem_info_arr if not (t[0] == '[anon]' or t[0] == '[heap]' or t[0] == '[stack]')]
    mem_info_arr.sort(key=lambda t: t[2], reverse=True)
    mem_info_arr = mem_info_arr[:top]

    # 创建表格
    t_table = PrettyTable(['file', 'rss', 'size'])
    for i, m in enumerate(mem_info_arr):
        t_table.add_row([m[0], byte_length_format(m[1]), byte_length_format(m[2])])
        if details:
            click.echo("详细信息:\r\n" + json.dumps(m, indent=1, separators=(', ', ': '), ensure_ascii=False))
    # 设置对齐方式
    t_table.align = "l"
    # 设置表格最长列
    t_table.max_width = 80
    click.echo(t_table)


def net_info(details):
    all_net_io_counter = psutil.net_io_counters()
    all_net_io_info_str = """
综合数据:     
发送数据大小: {}
接受数据大小: {}
发送的数据包数量: {}
接受的数据包数量: {}
接受的错误总数: {}
发送的错误总数: {}
丢弃的传入数据包总数: {}
丢弃的传出数据包总数: {}
    """.format(byte_length_format(all_net_io_counter.bytes_sent),
               byte_length_format(all_net_io_counter.bytes_recv),
               all_net_io_counter.packets_sent,
               all_net_io_counter.packets_recv,
               all_net_io_counter.errin,
               all_net_io_counter.errout,
               all_net_io_counter.dropin,
               all_net_io_counter.dropout
               )
    print(all_net_io_info_str)

    net_io_counters = psutil.net_io_counters(pernic=True)

    net_io_table = PrettyTable(
        ['发送数据大小', '接受数据大小', '发送的数据包数量', '接受的数据包数量', '接受的错误总数', '发送的错误总数',
         '丢弃的传入数据包总数',
         '丢弃的传出数据包总数'])
    for key in net_io_counters.keys():
        t = net_io_counters[key]
        net_io_table.add_row([key,
                              byte_length_format(t.bytes_sent),
                              byte_length_format(t.bytes_recv),
                              t.packets_sent,
                              t.packets_recv,
                              t.errin,
                              t.errout,
                              t.dropin,
                              t.dropout
                              ])

    net_io_table.align = "l"
    # 设置表格最长列
    net_io_table.max_width = 80
    click.echo(net_io_table)
    pass


def disk_info():
    disk_partitions = psutil.disk_partitions()
    d_p_table = PrettyTable(['设备驱动号', '挂载名称', '文件系统类型', '挂载选项', '使用量'])
    for d in disk_partitions:
        t_l = [d.device, d.mountpoint, d.fstype, d.opts]
        t_d_u = psutil.disk_usage(d.mountpoint)
        t_l.append("total:{},used:{},free:{},percent:{}%".format(byte_length_format(t_d_u.total),
                                                                 byte_length_format(t_d_u.used),
                                                                 byte_length_format(t_d_u.free),
                                                                 t_d_u.percent
                                                                 ))
        d_p_table.add_row(t_l)
    # 设置对齐方式
    d_p_table.align = "l"
    # 设置表格最长列
    d_p_table.max_width = 80
    click.echo(d_p_table)

    # 输出当前磁盘的详细io信息
    try:
        disk_stat_dict = psutil.disk_io_counters(perdisk=True)
        d_s_table = PrettyTable(
            ['设备名', '读取次数', '写入次数', '读取大小', '写入大小', '读取耗时(ms)', '写入耗时(ms)',
             '实际io耗费时间(ms)', '合并读取次数', '合并写入次数'])
        for key in disk_stat_dict.keys():
            t = disk_stat_dict[key]
            d_s_table.add_row([key,
                               t.read_count,
                               t.write_count,
                               byte_length_format(t.read_bytes),
                               byte_length_format(t.write_bytes),
                               t.read_time,
                               t.write_time,
                               t.busy_time,
                               t.read_merged_count,
                               t.write_merged_count
                               ])

        d_s_table.align = "l"
        # 设置表格最长列
        d_s_table.max_width = 80
        click.echo(d_s_table)
    except Exception as e:
        click.echo(click.style("获取磁盘io统计计数信息异常!" + e, fg='red'))
