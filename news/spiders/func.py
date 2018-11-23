# -*- coding: utf-8 -*-
import requests, hashlib,datetime

from datetime import datetime as DT
from bs4 import BeautifulSoup
import re
import json
from six.moves.urllib import request

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}


def getHTMLText(url):
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print("产生异常")


def ListCombiner(lst):
    string = ''
    for e in lst:
        string += e
    return string

def md5(string):
    """
    md5 加密
    """
    m = hashlib.md5()
    m.update(string.encode(encoding='utf-8'))
    return m.hexdigest()


def get_crawl_days(dates, cut_day=180, format_str="%Y-%m-%d"):
    """
    爬取日期获取，默认7天
    """
    return [(DT.strptime(dates, format_str) - datetime.timedelta(days=i)).strftime(format_str) for i in xrange(0, cut_day)]

# tieba
def is_ad(s):
    """判断楼层是否为广告"""
    ad = s.xpath(u".//span[contains(text(), '广告')]")
    # 广告楼层中间有个span含有广告俩字
    return ad

def parse_content(content):
    if not content or not content.strip():
        return None
    content = content.replace('\r', '\n') #古老的帖子会出现奇怪的\r
    s = BeautifulSoup(content, 'lxml')
    if s.html:
        s=s.html
    if s.body:
        s=s.body
    if s.div:
        s = s.div  #post 外层有个div
    if s.p:
        s = s.p
    l = list(s.children)
    for i in range(len(l)):
        parse_func = (is_str, is_br, is_img, is_video, other_case)
        for func in parse_func:
            try:
                ret = func(l[i])
            except:
                continue
            if ret is not False: 
                l[i] = ret
                break
    return strip_blank(''.join(l))

def strip_blank(s): #按个人喜好去掉空白字符
    s = re.sub(r'\n[ \t]+\n', '\n', s)
    s = re.sub(r'  +', ' ', s) #去掉多余的空格
    s = re.sub(r'\n\n\n+', '\n\n', s) #去掉过多的连续换行
    return s.strip()

def is_str(s): 
    if s.name: 
        return False
    #NavigableString类型需要手动转换下
    return str(s)

def is_br(s):
    if s.name == 'br':
        return '\n'
    return False

def is_img(s):
    # 处理了部分表情
    if s.name == 'img':
        src = str(s.get('src'))
        return get_emotion_text(src)
    return False

def is_video(s):
    t = str(s.get('class'))
    if 'video' in t:
        url = s.find('a').get('href')
        return ' ' + getJumpUrl(url) + ' '
    return False

#bs带的get_text功能，很好很强大
#粗体红字之类的都一句话搞定了
def other_case(s): 
    return s.get_text()

# 发送请求到 jump.bdimg.com/.. 来获取真实链接
# 阻止302跳转后可以大大节省时间

class RedirctHandler(request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise Exception(headers.getheaders('location')[0])


def getJumpUrl(url):
    req = request.Request(url)
    opener = request.build_opener(RedirctHandler())
    try:
        opener.open(url)
    except Exception as e:
        return str(e)



import os
print (os.getcwd)
emotion_data = json.loads(open('{}/news/spiders/emotion.json'.format(os.getcwd()), 'r').read())


def get_emotion_text(url):
    for data in emotion_data:
        match = re.findall(data['regex'], url)
        if not match:
            continue
        if isinstance(match[0], tuple):
            match = match[0]
        for emotion in data['emotion_list']:
            flag = True
            for i in range(len(match)):
                if emotion['pattern'][i] == '__index__':
                    index = int(match[i]) - 1
                    if index >= len(emotion['text']):
                        return ' ' + url + ' '
                elif emotion['pattern'][i] != match[i]:
                    flag = False
                    break
            if flag:
                return '[' + emotion['text'][index] + ']'
    return ' ' + url + ' '
