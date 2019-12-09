#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/3 15:19
# @Author  : m02he
# @File    : CNVD_CVE.py

import re
import time
import random
import Queue
import threading
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Crawl_Cnvd():
    def __init__(self):
        self.qurl = Queue.Queue()
        self.thread_num = 50
        self.lock = threading.Lock()
        self.lock2 = threading.Lock()
        self.proxyIPList = []
        self.proxyIP = ""  # 设空为使用本地ip
        self.flag = 0
        self.cnvd_id = ""

    def get_proxyIP(self):
        for line in  open("ip.txt"):
            ip = line.strip()
            self.proxyIPList.append(ip)
        print "代理ip加载完毕............"

    def verify_ip(self):
        cnt = 0
        while True: # 如果找不到可用的代理ip，可能出现死循环
            try:
                if cnt > 3: # waf拦截2分钟左右，所以本地ip又可以用
                    self.proxyIP = ""
                    break
                randomIP = self.proxyIPList[random.randint(0, len(self.proxyIPList) - 1)]
                proxy = {
                    "http": randomIP,
                    "https": randomIP
                }
                url = "http://icanhazip.com/"
                req = requests.get(url, proxies=proxy, timeout=60)
                if req.status_code == 200:
                    self.proxyIP = randomIP
                    print "找到新的可用代理ip......", randomIP
                    break
            except Exception, e:
                print randomIP  + " 无效代理"
                pass
            cnt += 1

    def create_thread(self):
        self.read_url()
        self.get_proxyIP()
        ths = []
        for t in range(0, self.thread_num):
            th = threading.Thread(target=self.request_queue)
            # th.setDaemon(False)
            th.start()
            ths.append(th)
        for th in ths:
            th.join()

    # def request_url(self, cnnvd_id):


    def request_queue(self):
        while True:
            self.lock.acquire()
            if self.qurl.empty():
                self.lock.release()
                break
            base_url = "https://www.cnvd.org.cn/flaw/show/"
            if self.flag == 0:
                self.cnvd_id = self.qurl.get()
            elif self.flag == 1:
                self.cnvd_id = self.cnvd_id # 重新发送请求
                self.lock2.acquire()
                print "正在寻找新代理............"
                if self.proxyIP =="":
                    th = threading.Thread(target=self.verify_ip)
                    th.start()
                    th.join()
                else:
                    self.proxyIP = ""
                self.lock2.release()
                self.flag = 0
            url = base_url + self.cnvd_id
            try:
                UA_list = [
                    {'User-Agent': 'Mozilla/1.22 (compatible; MSIE 2.0d; Windows NT)'},
                    {'User-Agent': 'Mozilla/2.0 (compatible; MSIE 3.02; Update a; Windows NT)'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 4.01; Windows NT)'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0)'},
                    {'User-Agent': 'Mozilla/4.79 [en] (WinNT; U)'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:0.9.2) Gecko/20010726 Netscape6/6.1'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.19) Gecko/20081204 SeaMonkey/1.1.14'},
                    {'User-Agent': 'Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaE90-1/210.34.75 Profile/MIDP-2.0 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413'},
                    {'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_2 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5G77 Safari/525.20'},
                    {'User-Agent': 'Mozilla/5.0 (Linux; U; Android 1.5; en-gb; HTC Magic Build/CRB17) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1'},
                    {'User-Agent': 'Opera/9.27 (Windows NT 5.1; U; en)'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.4.154.25 Safari/525.19'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.48 Safari/525.19'},
                    {'User-Agent': 'Wget/1.8.2'},
                    {'User-Agent': 'Mozilla/5.0 (PLAYSTATION 3; 1.00)'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; (R1 1.6))'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.1) Gecko/20061204 Firefox/2.0.0.1'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10 (.NET CLR 3.5.30729) JBroFuzz/1.4'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)'},
                    {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.12) Gecko/20050923 CentOS/1.0.7-1.4.1.centos4 Firefox/1.0.7'},
                    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727)'},
                    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.5) Gecko/2008120122 Firefox/3.0.5'},
                    {'User-Agent': 'Mozilla/5.0 (X11; U; SunOS i86pc; en-US; rv:1.7) Gecko/20070606'},
                    {'User-Agent': 'Mozilla/5.0 (X11; U; SunOS i86pc; en-US; rv:1.8.1.14) Gecko/20080520 Firefox/2.0.0.14'},
                    {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.5) Gecko/2008120121 Firefox/3.0.5'},
                    {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
                ]
                header = UA_list[random.randint(0, len(UA_list) - 1)]
                proxy = {
                    "http": self.proxyIP,
                    "https": self.proxyIP
                }
                print url,"， 当前代理，"+ self.proxyIP
                resp = requests.get(url, headers=header, proxies=proxy, timeout=(600, 60))
                if resp.status_code == 200:
                    result = re.search(r'CVE-[0-9]{4}-[0-9]{3,5}', resp.text)
                    if result:
                        line = "%-15s" % result.group() + self.cnvd_id
                        f.write(line + "\n")
                        f.flush()
                        print line + " 已匹配"
                    else:
                        print url +" 未匹配"
                elif resp.status_code == 403: # 403为waf拦截，启用代理
                    print "当前请求被waf拦截.......需更换代理"
                    self.flag = 1
                else:
                    print url + ":  " + str(resp.status_code)
            except requests.exceptions.ProxyError, e:
                print self.proxyIP + " 代理服务器拒绝建立连接，端口拒绝连接或未开放."
                print "Error,   " + str(e)
                self.flag = 1
            except requests.exceptions.ConnectTimeout, e:
                print self.proxyIP + "代理服务器没有响应."
                print "Error,   " + str(e)
                self.flag = 1
            except requests.exceptions.ConnectTimeout, e:
                print self.proxyIP + "说明与代理建立连接成功，代理也发送请求到目标站点，但是代理读取目标站点资源超时."
                print "Error,   " + str(e)
                self.flag = 1
            except Exception, e:
                error = url + ", Error: " + str(e)
                # f.write(error + "\n")
                # f.flush()
                print error
                self.flag = 1
            self.lock.release()
        self.lock.acquire()
        print threading.current_thread().getName()
        self.lock.release()

    # 读取url
    def read_url(self):
        for line in open('CNVD_url.txt'):
            id = line.strip()
            self.qurl.put(id)


    # 抓取url
    def gen_url(self):
        offset = 0
        f = open('CNVD_url.txt', mode='w')
        while True:
            try:
                url = "https://www.cnvd.org.cn/flaw/list.htm?flag=true"
                header = {
                    'Host': 'www.cnvd.org.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Referer': 'https://www.cnvd.org.cn/flaw/list.htm?flag=true',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Connection': 'close',
                    'Content - Length': '160',
                    'Upgrade-Insecure-Requests': '1'
                }
                data = {
                    'max': 20,
                    'offset': offset
                }
                req = requests.post(url, data=data, headers=header, timeout=(30, 60))
                if req.status_code == 200:
                    result = re.findall(r'/flaw/show/CNVD-\d{4}-\d{4,5}', req.text)
                    ran = len(result)
                    if ran == 10:
                        break
                    if result:
                        for i in range(ran - 10):
                            print result[i][11:]
                            f.write(result[i][11:] +"\n")
                            f.flush()
                time.sleep(5)
                offset += 20
            except Exception, e:
                print "Error: " + str(e)
                pass
        print "url生成完毕..........."


if __name__ == '__main__':
    f = open('CVE-CNVD.txt', mode='w')
    f.write("\tCVE\t\t\t\tCNVD\n")
    test = Crawl_Cnvd()
    # test.gen_url()
    test.create_thread()
    f.close()
