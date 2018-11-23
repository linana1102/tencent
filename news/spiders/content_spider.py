# -*- coding: utf-8 -*-
import re
import json
import time
import math
import random
import pymongo
from scrapy.spiders import Spider, Request
from news.settings import DEFAULT_REQUEST_HEADERS
from news.items import TencentItem
import ast
from news.middlewares.resource import PROXIES, PORT
import requests
from news.config import MONGODB_CONFIG


class TencentSpider(Spider):
    name = 'tencent_contents'
    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sport.qq.com', 'edu.qq.com',
                       'finance.qq.com', 'games.qq.com', 'auto.qq.com', 'house.qq.com']
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
    mongo = ''
    url_pattern1 = r'(.*)/a/(\d{8})/(\d+)\.htm'
    url_pattern2 = r'(.*)/omn/(\d{8})/(.+)\.html'
    url_pattern3 = r'(.*)/omn/([A-Z0-9]{14,19})'
    url_pattern4 = r'(.*)/cmsn/([A-Z0-9]{8})/(.+)'
    url_pattern5 = r'(.*)/omn/(.+)\.html'

    def start_requests(self):
        DEFAULT_REQUEST_HEADERS[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        DEFAULT_REQUEST_HEADERS['Host'] = 'news.qq.com'
        DEFAULT_REQUEST_HEADERS['Referer'] = ''

        self.mongo = MongodbP()
        start = time.time()
        results = self.mongo.conn["date_url"].find().limit(2000)
        print(time.time()-start)
        start = time.time()
        url_list = []
        for item in results:
            url_list.append(item["url"])
            self.mongo.conn["date_url"].delete_one({"_id": item["_id"]})
        print(time.time()-start)

        # url_list = [
        #     # "http://sports.qq.com/a/20170417/037759.htm",
        #     # "https://finance.qq.com/a/20170320/026597.htm",
        #     "http://sports.qq.com/a/20160228/019306.htm"
        # ]
        # results = [
        #     # {"Url": "https://new.qq.com/omn/20180906/20180906A0D52T.html"},
        #     #        {"Url": "http://tech.qq.com/a/20120621/000205.htm"},
        #     {"Url": "http://new.qq.com/omn/20180906A0IZ7V.html"}
        #     ]

        for url in url_list:
            print(url)
            category = url[url.find('//')+2: url.find('.')]
            DEFAULT_REQUEST_HEADERS['Host'] = "{}.qq.com".format(category)
            yield Request(url, callback=self.parse_news, dont_filter=True, headers=DEFAULT_REQUEST_HEADERS)

    def parse_news(self, response):

        """
        https://news.qq.com/a/20180709/007392.htm
        """
        link = response.url
        # print(link)
        print('response link: %s' % (link, ))
        category = response.xpath('//div[@class="a_Info"]/span[@class="a_catalog"]/a/text()').extract_first()
        title = response.xpath('//div[@class="hd"]/h1/text()').extract_first()
        if not title:
            titles = response.xpath('//title/text()').extract_first().split("_")
            if titles:
                title = titles[0]
        print("title %s" % (title,))

        from_new = '腾讯新闻'
        news_time = response.xpath('//div[@class="a_Info"]/span[@class="a_time"]/text()').extract_first()
        if not news_time:
            pattern = re.match(self.url_pattern1, str(link))
            if pattern:
                news_time = pattern.group(2)
                # print(news_time)

        content = ''
        texts = response.xpath('//div[@class="Cnt-Main-Article-QQ"]//p/text()').extract()

        if not texts:
            # "http://auto.qq.com/a/20120227/000075.htm"
            texts = response.xpath('//div[@id="Cnt-Main-Article-QQ"]/p//text()').extract()
        if not texts:
            # "https://finance.qq.com/a/20121203/005320.htm"
            texts = response.xpath('//div[@id="Cnt-Main-Article-QQ"]/text()').extract()
        if not texts:
            # "http://sports.qq.com/a/20120910/000457.htm"
            texts = response.xpath('//div[@id="ArticleCnt"]/p//text()').extract()
        if not texts:
            texts = response.xpath('//div[@id="ArticleCnt"]/text()').extract()
        if not texts:
            # "http://tech.qq.com/a/20081022/000095.htm"
            texts = response.xpath('//div[@id="ArtCnt"]/p//text()').extract()
        if not texts:
            # "http://tech.qq.com/a/20081022/000095.htm"
            texts = response.xpath('//div[@id="ArtCnt"]/text()').extract()
        if not texts:
            # http://edu.qq.com/a/20050511/000159.htm
            texts = response.xpath('//p[@style="text-indent:2em;"]/text()').extract()
        if not texts:
            # # "http://tech.qq.com/a/20050510/000068.htm"
            texts = response.xpath('//p[@style="TEXT-INDENT: 2em"]/text()').extract()
        if not texts:
            # "https://news.qq.com/a/20050420/000038.htm"
            texts = response.xpath('//td[@id="textflag"]//text()').extract()
        if not texts:
            # https://finance.qq.com/a/20050422/000119.htm
            texts = response.xpath('//td//text()').extract()

        url_type = response.xpath('//div[@id="toolBar"]/ul/li[@id="slide"]/a/span//text()').extract_first()
        # print(url_type)
        if url_type:
            url_type = url_type.strip()
        else:
            url_type = response.xpath('//div[@id="toolBar"]/ul/li[@class="play"]//text()').extract_first()
        for text in texts:
            content += text
        if not content and url_type == "幻灯播放":
            jsUrl = response.url.split('.htm')[0]
            res = fetchUrl(jsUrl + ".hdBigPic.js")
            if res.status_code == 404:
                res = fetchUrl(jsUrl + ".hdPic.js")

            if res.status_code == 200:
                result = re.search(r'\{.*\}', res.text).group()
                data = ast.literal_eval(result)
                # "https://news.qq.com/a/20151224/060317.htm"
                data_info = data["Children"][0]["Children"][1]["Children"]
                for info in data_info:
                    # image_url += info["Children"][1]["Children"][0]["Content"] + "\n"
                    # image_url += info["Children"][2]["Children"][0]["Content"] + "\n"
                    s = info["Children"][3]["Children"][0]["Content"]
                    content_list = re.findall(">(.*?)<", s)
                    if content_list:
                            content += content_list[0]
                    else:
                        content += s

                if not content:
                    # url = "http://ent.qq.com/a/20121230/000001.htm"
                    s = data["Children"][0]["Children"][-1]["Children"][0]["Content"]
                    # print(s)
                    contentlist = re.findall("<SPAN.*?>(.*?)<", s)
                    # print(contentlist)
                    for x in contentlist:
                        content += x
                    if not content:
                        contentlist = re.findall("<.*?>(.*?)<", s)
                        for x in contentlist:
                            content += x

        if not content and (re.search(self.url_pattern2, link, re.I) or \
                re.search(self.url_pattern3, link, re.I) or re.search(self.url_pattern4, link, re.I) \
                or re.search(self.url_pattern5, link, re.I)):
            pat = lambda x: x[0] if x else ''
            title = pat(response.xpath('//h1/text()').extract())
            content = "".join(response.xpath('//div[@class="content-article"]/p//text()').extract())
            if not content:
                content = "".join(response.xpath('//div[@id="Cnt-Main-Article-QQ"]/p//text()').extract())
            if not content:
                contentList = response.xpath('//div[@class="content-article"]/script/text()').extract_first()
                if contentList:
                    contentList = eval(contentList.split("=")[1])
                    for record in contentList:
                        content += record["value"]
            if not content and re.search("notfound", link, re.I).group() == "notfound":
                # "Link" : "https://new.qq.com/notfound.htm?uri=http://new.qq.com/omn/20180906/20180906A0IZ7V.html"
                url = "https://openapi.inews.qq.com/getQQNewsNormalContent?id={}00&chlid=news_rss&refer" \
                      "=mobilewwwqqcom&otype=jsonp&ext_data=all&srcfrom=newsapp&callback=getNewsContentOnlyOutput"
                id = link.split("/")[-1].split(".")[0]
                res = fetchUrl(url.format(id))
                if res:
                    data = ast.literal_eval(re.search(r'\{.*\}', res.text).group())
                if data:
                    content = data["ext_data"]["cnt_html"]
        if not content:
            # url = "http://ent.qq.com/a/20121118/000066.htm"
            text_list = re.findall("<div id=\"Cnt-Main-Article-QQ\".*?>(.*?)</div>", response.text, re.S)
            content = ""
            if text_list:
                text = text_list[0]
                # print(text)
                textList = re.findall(">(.*?)<", text, re.S)
                for text in textList:
                    content += text

        print("content %s" % (content, ))

        if not texts:
            writeDebugMessage('texts', '标签解析失败 url:' + link)
        if not content:
            writeDebugMessage('content', '标签解析失败 url:' + link)

        followCount = ''
        postCount = 0
        posts = []

        # 获取所有回复以及回复的评论
        cmtId = 0
        cmtIds = re.compile(u'cmt_id = (.*?);').findall(response.text)
        if not cmtIds:
            cmtIds = re.compile(r'aid:.*?\"(\d+)\"').findall(response.text)

        commentPattern = u'http://coral.qq.com/article/{}/comment/v2?callback=_article{}commentv2&orinum=30&oriorder=o&pageflag=1' \
                     u'&cursor={}&scorecursor=0&orirepnum=30&reporder=o&reppageflag=1&source=1&_=1535971412259'

        replyPattern = u'http://coral.qq.com/comment/{}/reply/v2?callback=_comment{}replyv2&targetid={}&reqnum=30' \
                       u'&pageflag=2&source=1&cursor={}&_=1536039539617'
        if len(cmtIds) > 0:
            cmtId = cmtIds[0]
        # print('cmtId:', cmtId)
        cursor = u'0'

        numMax = 30
        state = True
        while state:
            commUrl = commentPattern.format(cmtId, cmtId, str(cursor))

            res = fetchUrl(commUrl)
            comment = json.loads(res.text[res.text.find('{'): -1])
            if comment['errCode'] == 0:
                cursor = comment['data']['last']
                oriCommList = comment['data']['oriCommList']
                oriCommListLen = len(oriCommList)
                postCount = int(comment['data']['oritotal'])
                comUserList = comment['data']['userList']
                # print('len', oriCommListLen)
                # print('cursor:', cursor)

                # 如果评论不足30条, 则退出循环
                if oriCommListLen < numMax:
                    state = False

                # 拼接所有评论
                for oriComm in oriCommList:
                    post = {}
                    oriCommId = oriComm['id']
                    post['PostFrom'] = comUserList[oriComm['userid']]['nick']
                    post['PostTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(oriComm['time'])))
                    post['PostContent'] = oriComm['content']
                    post['Replies'] = []

                    #查看该评论有没有回复
                    orireplynum = int(oriComm['orireplynum'])
                    if orireplynum > 0:
                        replyCursor = u'0'
                        replPageTotal = int(math.ceil(orireplynum / 30.0))
                        for i in range(0, replPageTotal):
                            replyUrl = replyPattern.format(oriCommId, oriCommId, cmtId, replyCursor)
                            replyRes = fetchUrl(replyUrl)
                            # print("comment response %s" %(replyRes.text, ))
                            replyInfo = json.loads(replyRes.text[replyRes.text.find('{'): -1])
                            print(replyInfo)
                            # replyUserList = replyInfo['data']['userList']
                            if replyInfo['errCode'] == 0:
                                if replyInfo:
                                    replyUserList = replyInfo.get("data", {}).get("userList", {})
                                    replyCursor = replyInfo.get("data", {}).get("first", '')
                                    # repCommList = replyInfo['data']['repCommList']
                                    repCommList = replyInfo.get("data", {}).get("repCommList", [])
                                    for repComm in repCommList:
                                        #puserid userid  time  content
                                        replies = {}
                                        replies['ReplyFrom'] = replyUserList[repComm['userid']]['nick']
                                        replies['ReplyTo'] = replyUserList[repComm['puserid']]['nick']
                                        replies['ReplyTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(repComm['time'])))
                                        replies['ReplyContent'] = repComm['content']
                                        post['Replies'].append(replies)
                    posts.append(post)

            else:
                state = False

        item = TencentItem()

        item['Link'] = link
        # item['Tid'] = md5(item['Link'])
        item['Category'] = category
        item['Title'] = title
        item['From'] = from_new
        item['Time'] = news_time
        item['ReadCount'] = 0
        item['Content'] = content
        item['PostCount'] = postCount
        item['Posts'] = posts
        self.mongo.conn["tencent_news"].ensure_index('Link', unique=True)
        self.mongo.conn["tencent_news"].ensure_index('Time')
        return item


def fetchUrl(url):
    proxy = random.choice(PROXIES)
    proxy_url = 'http://{}:{}'.format(proxy, PORT)
    proxy_dict = {"http": proxy_url, "https": 'http://{}:{}'.format(proxy, PORT)}

    # DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
    DEFAULT_REQUEST_HEADERS[
        'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    # DEFAULT_REQUEST_HEADERS['Host'] = 'tech.qq.com'
    DEFAULT_REQUEST_HEADERS['Referer'] = ''
    category = url[url.find('//') + 2: url.find('.')]
    # print(category)
    DEFAULT_REQUEST_HEADERS['Host'] = "{}.qq.com".format(category)
    print(url)
    return requests.get(url, proxies=proxy_dict, headers=DEFAULT_REQUEST_HEADERS, timeout=60)


def writeDebugMessage(type, message):
    write = True

    filename = 'debug.log'
    if write:
        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        with open(filename, 'a') as f:
            f.write(nowTime + " " + type + " " + message + "\n")


def writeTimeMessage(type, message):
    write = False

    filename = 'time.log'
    if write:
        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        with open(filename, 'a') as f:
            f.write(nowTime + " " + type + " " + message + "\n")


class MongodbP(object):
    col_name = 'tencent_news'

    def __init__(self):
        client = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], connect=False)
        self.conn = client[MONGODB_CONFIG['db']]
        if self.conn:
            print('MongoDB已连接1111')

    def process_item(self, item):
        # print("插入数据")
        # tid = {'Tid': item['Tid']}
        # print(item)
        try:
            res = self.conn[self.col_name].insert_one(item)
        except Exception as e:
            writeDebugMessage('error', '标签解析失败 url:' + item["Link"])
            writeDebugMessage("error", e.message)


    def select_item(self, where, sort='_id', limit=0):
        result = self.conn[self.col_name].find(where).sort(sort)
        if limit > 0:
            result = result.limit(limit)
        return result

    def update_item(self, where, item):
        result = self.conn[self.col_name].update(where, item)
        return result

    def process_item_by_colname(self, name, item):
        # print("插入数据")
        tid = {'Tid': item['Tid']}
        # print(tid)
        res = self.conn[name].update_one(tid, {'$set': item}, upsert=True)
        return res

    def select_item_by_colname(self, name, where, sort='_id', limit=0):
        result = self.conn[name].find(where).sort(sort)
        if limit > 0:
            result = result.limit(limit)
        return result


