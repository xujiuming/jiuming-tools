import click
from local import pc_info


def print_version(ctx, param, value):
    """
    输出工具版本
    :param ctx:   click上下文
    :param param: 参数
    :param value:  值
    :return:
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo('mint-tools Version 1.0')
    ctx.exit()


@click.group()
@click.option('--version', '-v', help='工具版本', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
def cli():
    pass


# ---------------------- server tools ----------------------------------------------------------------------------------

@cli.group(help='远程服务器管理')
def server():
    pass


@server.command("list", help='显示所有服务器配置')
def server_list():
    click.echo('server_list')


@server.command("add", help='添加服务器配置')
def server_add():
    click.echo("server_add")


@server.command("remove", help='删除服务器配置')
def server_remove():
    click.echo("server_remove")


@server.command('edit', help='编辑服务器配置')
def server_edit():
    click.echo("server_edit")


# ----------------------------------- local tools ----------------------------------------------------------------------

@cli.group(help='本机使用的工具')
def local():
    pass


@local.command('pc-info', help='电脑配置')
def local_pc_info():
    pc_info.echo_pc_info()


@local.command('http', help='根据指定文件夹开启临时http服务器')
@click.option('--d', '-d', type=click.Path(exists=True), default='.', nargs=1, help='指定静态文件目录,默认为.')
@click.option('--t', '-t', default='http', type=click.Choice(['http', 'ftp', 'smb']), nargs=1, help='指定共享类型,默认为http')
def local_tmp_http(d, t):
    click.echo('http:::' + d + 'asdfas:::' + t)


# main 函数
if __name__ == '__main__':
    cli()
