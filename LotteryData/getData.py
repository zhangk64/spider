#!/usr/bin/env python
# -*- coding:utf8 -*-
import requests
import re
import csv
import threading


# 请求一次数据
def req(username=None, passwd=None):
    # login
    login_url = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    login_data = {
        "Action": "GetLotteryOpen",
        "LotteryCode": "1407",
        "IssueNo": "0",
        "DataNum": "1",
        "SourceName": "APP"
    }
    headers = {
        'Host': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'Connection': 'keep-alive',
        'Content-Length': '74',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Origin': 'xxxxxxxxxxxxxxxxxxxx',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; FRD-L19 Build/LMY48Z) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Referer': 'xxxxxxxxxxxxxxxxxxxx',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Cookie': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'X-Requested-With': 'xxxxxxxxxxxxxxxxxxxx',
    }
    r = requests.post(login_url, login_data, headers=headers)
    r.encoding = "utf-8"
    data = r.text
    dict = eval(re.sub("null", "None", data, 0))
    lotteryData = dict["BackData"]
    for d in lotteryData:
        s = d["OpenTime"], d["LotteryOpen"], d["IssueNo"]
        return s


# 计算和值（大小，单双）
def cal(lott):
    a_lott = lott.split(",")
    sum = 0
    for i in a_lott:
        sum += (int(i))
    return sum


# 计算一行数据
def deal():
    data = req()
    # print "------", data
    s_data = [str(data[0]), str(data[2]), str(data[1])]
    value = cal(data[1])
    sv = str(value)
    if value < 10:
        sv = ' ' + sv
    # print value
    s_data.append(sv)
    if value > 10:
        s_data.append("大")
    else:
        s_data.append("小")
    if value % 2 == 0:
        s_data.append("双")
    else:
        s_data.append("单")

    return s_data


# 定时器函数
def collect():
    # writer.writerow(["Time", "Number", "Lottery", "Size", "Single"])
    s_data = deal()
    for i in s_data:
        print i.decode('UTF-8').encode('GBK'),
    # print str(i).decode('string_escape'),
    print ("")
    global writer
    writer.writerow(s_data)

    global timer
    timer = threading.Timer(60, collect)
    timer.start()


if __name__ == "__main__":
    writer = csv.writer(file('data.csv', 'ab+'))
    # writer.writerow(["Time", "Number", "Lottery", "Size", "Single"])
    timer = threading.Timer(0, collect)  # 首次启动
    timer.start()
