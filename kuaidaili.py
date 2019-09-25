#!user/bin/python
# -*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/9/3 15:16'

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import pymysql
import requests
import re
import json
import os
from bs4 import BeautifulSoup
import threading
from multiprocessing.dummy import Pool
import time, datetime
from concurrent.futures import ThreadPoolExecutor, wait
from apscheduler.schedulers.background import BackgroundScheduler

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
						 'Chrome/68.0.3440.75 Safari/537.36',
		   "Accept": "application/json, text/javascript, */*; q=0.01",
		   "Accept-Encoding": "gzip, deflate",
		   "Accept-Language": "zh-CN,zh;q=0.9",
		   "Connection": "keep-alive"}

session = requests.Session()


def sql():
	db = pymysql.Connect(host="192.168.10.37", user='root', password="root", database="web_learn", charset='utf8mb4')
	command = db.cursor()
	return command

def maxPage(url):
	r = session.get(url, headers=headers, verify=False)
	soup = BeautifulSoup(r.content, 'html.parser')
	element = soup.find(id='listnav').find_all('a')[-1]
	maxpage = element.text
	return int(maxpage)


def getIp(url):
	r = session.get(url, headers=headers, verify=False)
	soup = BeautifulSoup(r.content, 'html.parser')
	TableList = soup.find_all('tr')[1:]
	db = sql()
	for ipList in TableList:
		ips = (ipList.text[1:].split('\n'))
		now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		IPS = ips[0]
		Port = ips[1]
		Type = ips[3]
		Addr = ips[4]
		inster = f"INSERT INTO proxiy_ip(ip, types, `port`, address, createtime) " \
				 f"VALUES ('{IPS}', '{Type}', '{Port}', '{Addr}', '{now}')"
		db.execute(inster)
	db.connection.commit()

def concurrent_getIp(url):
	maxpage = maxPage(url)
	pool = ThreadPoolExecutor(max_workers=maxpage)
	futures = []
	for i in range(maxpage):
		newurl = url + f"{i+1}/"
		func = pool.submit(getIp, newurl)
		futures.append(func)
	wait(futures)

def checkIp(proxies):
	checkurl = 'https://www.baidu.com/'
	try:
		req = requests.get(checkurl, proxies=proxies, headers=headers, timeout=2)
		req.encoding = req.apparent_encoding
		if req.status_code == 200 and u'百度' in req.text:
			return True
		else:
			return False
	except:
		return False


def threads_getIp(page):
	url = 'https://www.kuaidaili.com/free/'
	threads = []
	for i in range(1, int(page) + 1):
		if i == 1:
			pageurl = url
		else:
			pageurl = f'https://www.kuaidaili.com/free/inha/{i}/'
		t = threading.Thread(target=getIp, args=(pageurl,))
		t.start()
		time.sleep(3)
		threads.append(t)
	[t.join() for t in threads]
	while True:
		thread_num = len(threading.enumerate())
		if thread_num <=1:
			break
	futures = []
	db = sql()
	db.execute('select id, ip,`port` from proxiy_ip')
	datas = list(db.fetchall())
	pool = ThreadPoolExecutor(max_workers=10)
	for data in datas:
		n = data[0]
		proxiesIp = "http://%s:%s" % (data[1], data[2])
		proxies = {}.fromkeys(['http', 'https'], proxiesIp)
		func = pool.submit(checkIp, proxies)
		result = func.result()
		futures.append(func)
		if not result:
			db.execute\
				(f'UPDATE proxiy_ip SET vaild=0, updatetime="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" '
				 f'WHERE id={n}')
		else:
			db.execute \
				(f'UPDATE proxiy_ip SET vaild=1, updatetime="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" '
				 f'WHERE id={n}')
		db.connection.commit()
	wait(futures)


if __name__ == '__main__':
	page = maxPage(url)
	threads_getIp(page)
