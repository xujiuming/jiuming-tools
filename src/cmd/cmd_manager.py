import click
import requests
from lxml import etree


def search(name):
    response = requests.get("http://linux.51yip.com/search/{}".format(name))
    response.encoding = 'utf-8'
    if response.status_code != 200:
        click.echo(response.text)  # 以文本形式打印网页源码
        if response.status_code == 404:
            click.echo("未找到{}命令!".format(name))
        if response.status_code >= 500:
            click.echo("51yip服务器异常!")
        return
    # 利用etree.HTML，将字符串解析为HTML文档
    html = etree.HTML(response.text, etree.HTMLParser())
    click.echo(html.xpath('string(//*[@id="post-1"]/h1)'))
    click.echo(html.xpath('string(//*[@id="post-1"]/div[1])'))
    content_arr = html.xpath('//*[@id="post-1"]/div[2]/pre')
    for i, content in enumerate(content_arr):
        if i == 0:
            help_arr = content.xpath('text()')
            for h in help_arr:
                click.echo(h)
        else:
            click.echo(content.xpath('string(.)'))
