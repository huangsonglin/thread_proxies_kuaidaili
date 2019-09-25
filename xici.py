#!user/bin/python
# -*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/9/16 15:21'

import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
import re
import json
import random
from bs4 import BeautifulSoup
import threading
from multiprocessing.dummy import Pool
import time, datetime
from concurrent.futures import ThreadPoolExecutor, wait

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
						 'Chrome/68.0.3440.75 Safari/537.36',
		   "Accept": "application/json, text/javascript, */*; q=0.01",
		   "Accept-Encoding": "gzip, deflate",
		   "Accept-Language": "zh-CN,zh;q=0.9",
		   "Connection": "keep-alive"}


def get_maxpage(url, proxies=None):
	r = requests.get(url, headers=headers, proxies=proxies)
	soup = BeautifulSoup(r.content, 'html.parser')
	div = soup.find('div', class_='pagination')
	page = div.find_all('a')[-2].text
	return page


def get_ip(url, index, proxies=None):
	erverurl = url + f'/{index}.html'
	r = requests.get(erverurl, headers=headers, proxies=proxies)
	soup = BeautifulSoup(r.content, 'html.parser')
	ipList = soup.find(id='ip_list').find_all('td')
	data = []
	for ips in ipList:
		if ips.text.count(".") == 3:
			IP = ips.text
			data.append({"IP": IP})
		elif len(re.findall('\d', ips.text)) == len(ips.text) and ips.text != "":
			Port = ips.text
			IP = data[-1]
			newip = "%s:%s" % (data[-1]['IP'], Port)
			data[-1].update(IP=newip)
		elif "HTTP" in ips.text.upper():
			Type = ips.text
			data[-1].update(Type=Type)
		else:
			pass
	with open('ip.txt', 'w', encoding='utf-8') as f:
		for ip in data:
			f.write(str(ip) + '\n')


def get_proxies(file):
	with open(file, 'r', encoding='utf-8') as f:
		iplist = f.readlines()
		DicIp = random.choice(iplist)
		DicIp = DicIp.replace("'", '"')
		DicIp = json.loads(DicIp)
		IP = DicIp['IP']
		proxies = {}.fromkeys(['http', 'https'], IP)
		return proxies


if __name__ == '__main__':
	# urls = ['http://www.xicidaili.com/nn', 'http://www.xicidaili.com/nt', 'http://www.xicidaili.com/wn',
	# 		'http://www.xicidaili.com/wt']
	# threads = []
	# print(get_proxies('ip.txt'))
	# req = requests.get("http://music.migu.cn/v3", headers=headers, proxies=get_proxies('ip.txt'))
	# print(req.status_code, req.text)
# with open('ip.txt', 'r', encoding='utf-8') as f:
# 	iplist = f.readlines()
# 	for ip in iplist:
# 		ip = ip.replace("'", '"')
# 		ip = json.loads(ip)
# 		IP = ip['IP']
# 		proxies = {}.fromkeys(['http', 'https'], IP)
# 		try:
# 			req = requests.get('http://www.migu.cn', proxies=proxies, timeout=1)
# 			if req.status_code != 200:
# 				f.write(None)
# 		except:
# 			pass
	proxiesIp = '125.123.126.10:9999'
	proxies = {}.fromkeys(['http', 'https'], proxiesIp)
	print(proxies)
