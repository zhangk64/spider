#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/2 11:51
# @Author  : m02he
# @File    : CNNVD_CVE.py

import re
import Queue
import threading
import datetime
import requests

class Crawl_Cnnvd():
    def __init__(self):
        self.qurl = Queue.Queue()
        self.thread_num = 100
        self.lock = threading.Lock()

    def create_thread(self):
        self.gen_url()
        ths = []
        for t in range(0, self.thread_num):
            th = threading.Thread(target=self.request_url)
            # th.setDaemon(False)
            th.start()
            ths.append(th)
        for th in ths:
            th.join()

    def request_url(self):
        while True:
            self.lock.acquire()
            if self.qurl.empty():
                self.lock.release()
                break;
            base_url = "http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD="
            cnnvd_id = self.qurl.get()
            url = base_url + cnnvd_id
            try:
                header = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
                resp = requests.get(url, headers=header, timeout=600)
                if resp.status_code == 200:
                    result = re.search(r'CVE-[0-9]{4}-[0-9]{3,5}', resp.text)
                    if result:
                        line = "%-15s" % result.group() + cnnvd_id
                        f.write(line + "\n")
                        f.flush()
                        print line
                else:
                    print ".",
            except Exception, e:
                error = url + ", Error: " + str(e)
                # f.write(error + "\n")
                # f.flush()
                print error
            self.lock.release()
        self.lock.acquire()
        print threading.current_thread().getName()
        self.lock.release()


    def gen_url(self):
        t_year = datetime.datetime.now().year
        t_month = datetime.datetime.now().month
        for year in range(1988, t_year + 1):  # 1988
            for month in range(1, 12 + 1):
                if year == t_year and month > t_month:
                    return
                t = str(year) + "%02d" % month
                if year < 1999:
                    top = 100
                elif year < 2010:
                    top = 300
                elif year < 2016:
                    top = 1500
                else:
                    top = 2500
                for index in range(1, top):  # 最大暂定0为2000
                    cnnvd_id = "CNNVD-" + t + "-" + "%03d" % index
                    self.qurl.put(cnnvd_id)
        print "url生成完毕。"


if __name__ == '__main__':
    f = open('CVE-CNNVD.txt', mode='w')
    f.write("\tCVE\t\t\t\tCNNVD\n")
    test = Crawl_Cnnvd()
    test.create_thread()
    f.close()