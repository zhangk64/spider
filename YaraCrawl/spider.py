#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# 爬 https://feed.watcherlab.com/ 中的yara规则数据

import re
import requests
import os
import sys
# python在安装时，默认的编码是ascii，当程序中出现非ascii编码时，python的处理常常会报这样的错，
# python没办法处理非ascii编码的，此时需要自己设置将python的默认编码，一般设置为utf8的编码格式。
# 添加如下内容，设置编码为utf8
reload(sys)
sys.setdefaultencoding('utf8')

class crawl:
    def __init__(self, base_url):
        self.base_url = base_url
        self.urlsList = [base_url]

    # 下载函数
    def download(self, url):
        try:
            r = requests.get(url)
            r.encoding = "utf-8"
            content = r.text
            # print content  #获取文件内容

            # 当前目录下创建对应的目录
            path = url[len(self.base_url):]  #下载路径
            p_list = path.split("/")
            dir = ""
            for i,p in enumerate(p_list):
                if p and i < len(p_list) -1:
                    dir = p + "/"
            if not os.path.exists(dir):
                os.makedirs(dir)

            # 在对应目录下写入文件内容
            with open(path, "wb") as f:
                f.write(content)
            f.close()
        except:
            print "文件下载错误"

    # 读取页面链接
    def spider(self, base_url):
        links = []
        try:
            header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
            }
            r = requests.get(base_url, headers=header)
            r.encoding = "utf-8"
            content = r.text
            links = re.findall(r'(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')', content)  # 匹配页面 href= 的链接
            # print links
        except:
            print "url连接错误"
        return links

    def getUrls(self, url):
        # 合成完整url链接
        list_urls = []
        links = self.spider(url)
        for l in links:
            if l == "../":
                continue
            purl = url + l
            if purl not in list_urls:
                list_urls.append(purl)
        # print list_urls

        # 递归爬取yar文件
        for u in list_urls:
            # 如果是.yar文件则下载
            if re.findall(r".*\.yar", u):
                print u
                self.download(u)
            else:  # 如果是目录则往下递归
                print u
                self.getUrls(u)

if __name__ == '__main__':
    # 初始下载链接
    base_url = "https://feed.watcherlab.com/rules/yara/webshell/"
    c = crawl(base_url)
    c.getUrls(base_url)