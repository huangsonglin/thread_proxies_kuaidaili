#!user/bin/python
#-*- coding: utf-8 -*-
__author__: 'huangsonglin@dcpai.cn'
__Time__: '2019/9/2 16:19'

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
import time,datetime
from concurrent.futures import ThreadPoolExecutor, wait

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/68.0.3440.75 Safari/537.36',
           "Accept": "application/json, text/javascript, */*; q=0.01",
           "Accept-Encoding": "gzip, deflate",
           "Accept-Language": "zh-CN,zh;q=0.9",
           "Connection": "keep-alive"}

# 获取页面最大max值
def get_maxpage(url, proxies):
    r = requests.get(url, headers=headers, proxies=proxies)
    print(r.status_code, r.text)
    soup = BeautifulSoup(r.content, 'html.parser')
    div = soup.find('div', class_='pagination')
    page = div.find_all('a')[-2].text
    print(page)
    return page


# 获取页面IP
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
    return data


# 检查代理是否可用
def check_ip(proxies):
    now = datetime.datetime.now().strftime("%m_%d")
    filename = 'proxies_%s.txt' % str(now)
    try:
        r = requests.get('https://www.baidu.com/', proxies=proxies)
        r.encoding = r.apparent_encoding
        if u'百度' in r.text and r.status_code == 200:
            with open(filename, 'a+', encoding='utf-8') as f:
                f.write(str(proxies) + '\n')
    except:
        pass

def get_proxies(file):
    with open(file, 'r', encoding='utf-8') as f:
        iplist = f.readlines()
        if len(iplist) != 0:
            randowip = random.choice(iplist)
            randowip = randowip.replace("'", '"')
            randowip = json.loads(randowip)
            dic = random.choice(randowip)
            IP = dic['IP']
            proxies = {}.fromkeys(['http', 'https'], IP)
        else:
            proxies = None
        return proxies

# 线程池方式获取ip
def Function_concurrent_getIp(url, proxies=None):
    futures = []
    maxpage = get_maxpage(url, proxies)
    maxpage = int(maxpage)
    Pool = ThreadPoolExecutor(max_workers=maxpage)
    for i in range(maxpage):
        func = Pool.submit(get_ip, url, i+1, proxies)
        with open('FristPage.txt', 'a', encoding='utf-8') as f:
            f.write(str(func.result()))
            f.write('\n')
        futures.append(func)
    wait(futures)

if __name__ == '__main__':
    urls = ['http://www.xicidaili.com/nn', 'http://www.xicidaili.com/nt', 'http://www.xicidaili.com/wn',
            'http://www.xicidaili.com/wt']
    proxiesIp = get_proxies()
    print(proxiesIp)
    req = requests.get('http://www.baidu.cn', proxies=proxiesIp)
    print(req.status_code)
    # for url in urls:
    #     proxies = get_proxies()
    #     t = threading.Thread(target=Function_concurrent_getIp, args=(url, proxies))
    #     t.start()
    #     threads.append(t)
    # for t in threads:
    #     t.join()
    # with open('FristPage.txt', 'r', encoding='utf-8') as f:
    #     iplist = f.readlines()
    #     num = len(iplist)
    #     Pool = ThreadPoolExecutor(max_workers=num)
    #     futures = []
    #     for line in iplist:
    #         line = line.replace("'", '"')
    #         line = json.loads(line)
    #         for dic in line:
    #             proxies = "%s://%s" % (dic['Type'], dic['IP'])
    #             proxies = {}.fromkeys(['http', 'https'], proxies)
    #             func = Pool.submit(check_ip, proxies)
    #             futures.append(func)
    #     wait(futures)




