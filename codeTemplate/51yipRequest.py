#!/bin/python3
# author ming
# 调用http://linux.51yip.com 页面 获取对应命令的使用方式文档
# requests + lxml
import requests
from requests_cache import CachedSession
from lxml import etree

if __name__ == '__main__':
    session = CachedSession('http_cache', backend='filesystem', use_cache_dir=True)
    print(session.cache.cache_dir)
    response = requests.get("http://linux.51yip.com/search/ls")
    response.encoding = 'utf-8'
    print(response.text)  # 以文本形式打印网页源码
    # 利用etree.HTML，将字符串解析为HTML文档
    html = etree.HTML(response.text, etree.HTMLParser())
    print("---------------------------------------")
    print(html.xpath('string(//*[@id="post-1"]/h1)'))
    print(html.xpath('string(//*[@id="post-1"]/div[1])'))
    content_arr = html.xpath('//*[@id="post-1"]/div[2]/pre')
    for i, content in enumerate(content_arr):
        if i == 0:
            help_arr = content.xpath('text()')
            for h in help_arr:
                print(h)
        else:
            print(content.xpath('string(.)'))
