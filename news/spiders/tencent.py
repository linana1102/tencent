# # -*- coding: utf-8 -*-
# import re
# import json
# import datetime, time
# import requests
# import random
# import math
# import sys
# import scrapy
# import pymongo
# from urlparse import urlparse
# from scrapy.spiders import CrawlSpider, Rule, Spider, Request
# from scrapy.linkextractors import LinkExtractor
# from scrapy.selector import Selector
# from news.settings import DEFAULT_REQUEST_HEADERS
# from news.items import TencentItem
# from news.spiders.func import getHTMLText, ListCombiner, md5, get_crawl_days
# from news.config import MONGODB_CONFIG
# from news.middlewares.resource import PROXIES,PORT
#
#
#
# class TencentNewsSpider(CrawlSpider):
#     name = 'tencent_news'
#     allowed_domains = ['new.qq.com', 'news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sport.qq.com', 'edu.qq.com',
#                        'finance.qq.com', 'games.qq.com', 'auto.qq.com', 'house.qq.com']
#
#     # start_urls = ['http://new.qq.com/', 'http://news.qq.com/', 'http://tech.qq.com/', 'http://ent.qq.com/',
#     #               'http://sport.qq.com/', 'http://edu.qq.com/', 'http://finance.qq.com/', 'http://games.qq.com/',
#     #               'http://auto.qq.com/', 'http://house.qq.com']
#
#     # start_urls = ['https://js.aq.qq.com/js/aq_common.js']
#
#     mongo = ''
#     # rules = ()
#     url_pattern1 = r'(.*)/a/(\d{8})/(\d+)\.htm'
#     url_pattern2 = r'(.*)/omn/(\d{8})/(.+)\.html'
#     url_pattern3 = r'(.*)/omn/([A-Z0-9]{14,19})'
#     url_pattern4 = r'(.*)/cmsn/([A-Z0-9]{8})/(.+)'
#     url_pattern5 = r'(.*)/omn/(.+)\.html'
#     # rules = (
#     #     Rule(LinkExtractor(allow=(url_pattern1)), 'parse_news'),
#     #     Rule(LinkExtractor(allow=(url_pattern2)), 'parse_news'),
#     #     Rule(LinkExtractor(allow=(url_pattern3)), 'parse_news'),
#     #     Rule(LinkExtractor(allow=(url_pattern4)), 'parse_news'),
#     # )
#
#     # url_pattern = r'[a-zA-z]+://[^\s]*'
#     # rules = (
#     #     Rule(LinkExtractor(allow=(url_pattern)), 'parse_news'),
#     # )
#
#     def start_requests(self):
#         self.mongo = MongodbP()
#         url = "http://www.qq.com"
#         yield Request(url, callback=self.parse_news, dont_filter=False,
#                       headers=DEFAULT_REQUEST_HEADERS)
#
#     def parse_news(self, response):
#         selfUrl = response.url
#         print('selfUrl:', selfUrl)
#
#         parseResult = urlparse(response.url)
#         rootUrl = parseResult.scheme + "://" + parseResult.netloc
#
#         res = re.findall(r"href=\"(.+?)\"", response.text)
#         for url in res:
#             if url.find("javascript") > -1 or url.find("img.com") > -1 or len(url) < 10:
#                 continue
#             if url.find("//") == 0:
#                 url = "http:" + url
#             if url.find("/") == 0:
#                 url = rootUrl + url
#             if url.find(".qq.") == -1 and url.find(".tencent.") == -1:
#                 continue
#
#             if re.search(self.url_pattern1, url, re.I) or re.search(self.url_pattern2, url, re.I) or\
#                     re.search(self.url_pattern3, url, re.I) or re.search(self.url_pattern4, url, re.I) \
#                     or re.search(self.url_pattern5, url, re.I):
#                 item = {}
#                 item['Url'] = url
#                 item['Tid'] = md5(url)
#                 item['Status'] = 0
#                 print('insertUrl:', url)
#                 self.mongo.process_item_by_colname('tencent_url', item)
#
#             else:
#                 yield Request(url, callback=self.parse_news, dont_filter=False,
#                               headers=DEFAULT_REQUEST_HEADERS)
#
#
#         # self.mongo = MongodbP()
#         # url = response.url
#         # print('url:', url)
#         # item = {}
#         # item['Url'] = url
#         # item['Date'] = ''
#         # item['Tid'] = md5(url)
#         # item['Title'] = ''
#         # item['Status'] = 0
#         # print('item')
#         # print(item)
#         # self.mongo.process_item(item)
#
#         # sys.exit()
#
#     def parse_news1(self, response):
#         print ('new1_url', response.url)
#         return
#         """
#         https://news.qq.com/a/20180709/007392.htm
#         """
#         sel = Selector(response)
#         pattern = re.match(self.url_pattern1, str(response.url))
#         item = TencentItem()
#         pat = lambda x: x[0] if x else ''
#         channel = 'tencent'
#         title = pat(sel.xpath('//h1/text()').extract())
#         date = pattern.group(2)
#         author = pat(sel.xpath('//*[@class="a_source"]//text()').extract())
#         item['channel'] = channel
#         item['title'] = title
#         item['date'] = date
#         item['author'] = author
#         item['link'] = str(response.url)
#         item['content'] = ListCombiner(
#             sel.xpath('//*[@id="Cnt-Main-Article-QQ"]/p//text()').extract())
#         item['img_link'] = sel.xpath(
#             '//*[@id="Cnt-Main-Article-QQ"]/p/img/@src').extract()
#         item['tid'] = md5(ListCombiner([channel, title, author, date]))
#         return item
#
#     def parse_news2(self, response):
#         print ('new2_url', response.url)
#         return
#         """
#         http://new.qq.com/omn/20180709/20180709A039CA.html
#         https://new.qq.com/cmsn/NEW20180/NEW20180708001061.html
#         http://new.qq.com/cmsn/20180709/20180709000767.html
#         http://new.qq.com/cmsn/20180709/TWF2018070902311500
#         """
#         sel = Selector(response)
#         pattern = re.match(self.url_pattern2_, str(response.url))
#         item = TencentItem()
#         pat = lambda x: x[0] if x else ''
#         channel = 'tencent'
#         title = pat(sel.xpath('//h1/text()').extract())
#         date = pattern.group(2)
#         author = pat(sel.xpath('//*[@class="a_source"]//text()').extract())
#         item['channel'] = channel
#         item['title'] = title
#         item['date'] = date
#         item['author'] = author
#         item['link'] = str(response.url)
#         item['content'] = ListCombiner(sel.xpath('//p//text()').extract())
#         item['img_link'] = sel.xpath('//p/img/@src').extract()
#         item['tid'] = md5(ListCombiner([channel, title, author, date]))
#         return item
#
#     def parse_news3(self, response):
#         print ('new3_url', response.url)
#         return
#         """
#         http://new.qq.com/omn/20180707A10IKG.html
#         """
#         sel = Selector(response)
#         pattern = re.match(self.url_pattern3, str(response.url))
#         item = TencentItem()
#         channel = 'tencent'
#         date = re.search(r"(\d{8})", pattern.group(2)).group(0)
#         author = ''
#
#         str1 = 'http://openapi.inews.qq.com/getQQNewsNormalContent?id='
#         str2 = '&chlid=news_rss&refer=mobilewwwqqcom&otype=jsonp&ext_data=all&srcfrom=newsapp&callback=getNewsContentOnlyOutput'
#         out = getHTMLText(str1 + pattern.group(2) + str2)
#         g = re.search("getNewsContentOnlyOutput\\((.+)\\)", out)
#         out = json.loads(g.group(1))
#         title = out["title"]
#
#         item['channel'] = channel
#         item['date'] = date
#         item['title'] = title
#         item['content'] = out["ext_data"]["cnt_html"]
#         item['author'] = author
#         item['link'] = str(response.url)
#         item['img_link'] = sel.xpath('//p/img/@src').extract()
#         item['tid'] = md5(ListCombiner([channel, title, author, date]))
#         return item
#
#
# class TencentSpider(Spider):
#     name = 'tencent_content'
#     allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sport.qq.com', 'edu.qq.com',
#                        'finance.qq.com', 'games.qq.com', 'auto.qq.com', 'house.qq.com']
#     url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
#     mongo = ''
#
#     def start_requests(self):
#         DEFAULT_REQUEST_HEADERS[
#             'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
#         DEFAULT_REQUEST_HEADERS['Host'] = 'news.qq.com'
#         DEFAULT_REQUEST_HEADERS['Referer'] = ''
#
#         self.mongo = MongodbP()
#
#         # res = self.mongo.select_item({'Status': 1}, '_id')
#         # for news in res:
#         #     news['Status'] = 0
#         #     self.mongo.update_item({'_id': news['_id']}, news)
#         # return
#
#
#         # url = 'https://news.qq.com/a/20180903/080709.htm'
#         # yield Request(url, callback=self.parse_news, meta={'news': {}}, dont_filter=True, headers=DEFAULT_REQUEST_HEADERS)
#         #
#         # return
#
#
#         res = self.mongo.select_item({'Status' : 0}, '_id')
#         for i in range(0, 10000) :
#             news = res[i]
#             url = news['Url']
#             # print('url', url)
#             category = url[url.find('//')+2: url.find('.')]
#             DEFAULT_REQUEST_HEADERS['Host'] = "{}.qq.com".format(category)
#             # print(DEFAULT_REQUEST_HEADERS['Host'])
#
#             # print("=============")
#             #
#             # break
#             # #      http://tech.qq.com/a/20180703/042791.htm
#             # url = 'http://tech.qq.com/a/20170331/003773.htm'
#
#             yield Request(url, callback=self.parse_news, meta={'news':news}, dont_filter=True, headers=DEFAULT_REQUEST_HEADERS)
#
#     def parse_news(self, response):
#         print('parse_news:')
#         # tid = md5(response.url)
#         #
#         # res = self.mongo.select_item_by_colname('tencent', {'Tid': tid})
#         # if res :
#         #     print(res[0]['Url'])
#         #     return
#
#         """
#         https://news.qq.com/a/20180709/007392.htm
#         """
#         link = response.url
#         print(link)
#         category = response.xpath('//div[@class="a_Info"]/span[@class="a_catalog"]/a/text()').extract_first()
#         title = response.xpath('//div[@class="hd"]/h1/text()').extract_first()
#         from_new = '腾讯新闻'
#         news_time = response.xpath('//div[@class="a_Info"]/span[@class="a_time"]/text()').extract_first()
#
#         content = ''
#         # texts = response.xpath('//div[@class="Cnt-Main-Article-QQ"]//p[@class="text"]/text()').extract()
#         texts = response.xpath('//div[@class="Cnt-Main-Article-QQ"]//p/text()').extract()
#         for text in texts:
#             content += text
#
#         # if not content and response.text.find('幻灯播放') > -1:
#         #     jsUrl = response.url.split('.htm')[0]
#         #     res = fetchUrl(jsUrl + ".hdBigPic.js")
#         #     if res.status_code == 404 :
#         #         res = fetchUrl(jsUrl + ".hdPic.js")
#         #
#         #     if res.status_code == 200 :
#         #
#         #         s = res.text[0 : res.text.find("/*")].strip()
#         #         print(s)
#         #         # imgContents = json.loads()
#         #         print('imgContents', json.load(s))
#
#         if not texts:
#             writeDebugMessage('texts', '标签解析失败 url:' + link)
#         if not content:
#             writeDebugMessage('content', '标签解析失败 url:' + link)
#
#         # return
#
#         followCount = ''
#         postCount = 0
#         posts = []
#
#         # 获取所有回复以及回复的评论
#         cmtId = 0
#         cmtIds = re.compile(ur'cmt_id = (.*?);').findall(response.text)
#         # ???? 怎么找到的
#         commentPattern = u'http://coral.qq.com/article/{}/comment/v2?callback=_article{}commentv2&orinum=30&oriorder=o&pageflag=1' \
#                      u'&cursor={}&scorecursor=0&orirepnum=30&reporder=o&reppageflag=1&source=1&_=1535971412259'
#         # ???? 怎么找到的
#         replyPattern = u'http://coral.qq.com/comment/{}/reply/v2?callback=_comment{}replyv2&targetid={}&reqnum=30' \
#                        u'&pageflag=2&source=1&cursor={}&_=1536039539617'
#         if len(cmtIds) > 0:
#             cmtId = cmtIds[0]
#         print('cmtId:', cmtId)
#         cursor = u'0'
#
#         numMax = 30
#         state = True
#         while state:
#             commUrl = commentPattern.format(cmtId, cmtId, str(cursor))
#
#             res = fetchUrl(commUrl)
#             comment = json.loads(res.text[res.text.find('{') : -1])
#             if comment['errCode'] == 0:
#                 cursor = comment['data']['last']
#                 oriCommList = comment['data']['oriCommList']
#                 oriCommListLen = len(oriCommList)
#                 postCount = int(comment['data']['oritotal'])
#                 comUserList = comment['data']['userList']
#                 print('len', oriCommListLen)
#                 print('cursor:', cursor)
#
#                 # 如果评论不足30条, 则退出循环
#                 if oriCommListLen < numMax :
#                     state = False
#
#                 # 拼接所有评论
#                 for oriComm in oriCommList :
#                     post = {}
#                     oriCommId = oriComm['id']
#                     post['PostFrom'] = comUserList[oriComm['userid']]['nick']
#                     post['PostTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(oriComm['time'])))
#                     post['PostContent'] = oriComm['content']
#                     post['Replies'] = []
#
#                     #查看该评论有没有回复
#                     orireplynum = int(oriComm['orireplynum'])
#                     if orireplynum > 0 :
#                         replyCursor = u'0'
#                         replPageTotal = int(math.ceil(orireplynum / 30.0))
#                         for i in range(0, replPageTotal) :
#                             replyUrl = replyPattern.format(oriCommId, oriCommId, cmtId, replyCursor)
#                             replyRes = fetchUrl(replyUrl)
#                             replyInfo = json.loads(replyRes.text[replyRes.text.find('{'): -1])
#                             replyUserList = replyInfo['data']['userList']
#                             if replyInfo['errCode'] == 0 :
#                                 replyCursor = replyInfo['data']['first']
#                                 repCommList = replyInfo['data']['repCommList']
#                                 for repComm in repCommList :
#                                     #puserid userid  time  content
#                                     replies = {}
#                                     replies['ReplyFrom'] = replyUserList[repComm['userid']]['nick']
#                                     replies['ReplyTo'] = replyUserList[repComm['puserid']]['nick']
#                                     replies['ReplyTime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(repComm['time'])))
#                                     replies['ReplyContent'] = repComm['content']
#                                     post['Replies'].append(replies)
#                     posts.append(post)
#
#             else:
#                 state = False
#
#         item = TencentItem()
#
#         item['Link'] = link
#         item['Tid'] = md5(item['Link'])
#         item['Category'] = category
#         item['Title'] = title
#         item['From'] = from_new
#         item['Time'] = news_time
#         item['ReadCount'] = 0
#         item['Content'] = content
#         item['PostCount'] = postCount
#         item['Posts'] = posts
#
#         news = response.meta['news']
#         news['Status'] = 1
#         self.mongo.update_item({'_id': news['_id']}, news)
#
#         return item
#
#
#         # sel = Selector(response)
#         # pattern = re.match(self.url_pattern, str(response.url))
#         # print('pattern')
#         # print(pattern)
#         #
#         # item = TencentItem()
#         #
#         # # url = response.meta['url']
#         # # title = response.meta['title']
#         # # column = response.meta['column']
#         # # time_ = response.meta['time']
#         # # category = response.meta['category']
#         #
#         # def pat(x):
#         #     return x[0] if x else ''
#         #
#         # channel = 'tencent'
#         # title = pat(sel.xpath('//h1/text()').extract())
#         # date_ = pattern.group(2)
#         # author = pat(sel.xpath('//*[@class="a_source"]//text()').extract())
#         # item['channel'] = channel
#         # item['title'] = title
#         # item['date'] = date_
#         # item['author'] = author
#         # item['link'] = str(response.url)
#         # item['content'] = ListCombiner(
#         #     sel.xpath('//*[@id="Cnt-Main-Article-QQ"]/p//text()').extract())
#         # item['img_link'] = sel.xpath(
#         #     '//*[@id="Cnt-Main-Article-QQ"]/p/img/@src').extract()
#         # item['tid'] = md5(ListCombiner([channel, title, author, date_]))
#         # return item
#
# def fetchUrl(url) :
#     proxy = random.choice(PROXIES)
#     proxy_url = 'http://{}:{}'.format(proxy, PORT)
#     proxy_dict = {"http": proxy_url}
#
#     # DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
#     DEFAULT_REQUEST_HEADERS[
#         'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
#     # DEFAULT_REQUEST_HEADERS['Host'] = 'tech.qq.com'
#     DEFAULT_REQUEST_HEADERS['Referer'] = ''
#     category = url[url.find('//') + 2: url.find('.')]
#     DEFAULT_REQUEST_HEADERS['Host'] = "{}.qq.com".format(category)
#     return requests.get(url, proxies=proxy_dict, headers=DEFAULT_REQUEST_HEADERS)
#
# def writeDebugMessage(type, message):
#     write = True
#
#     filename = 'debug.log'
#     if write:
#         nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#         with open(filename, 'a') as f:
#             f.write(nowTime + " " + type + " " + message + "\n")
#
#
# def writeTimeMessage(type, message):
#     write = False
#
#     filename = 'time.log'
#     if write:
#         nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#         with open(filename, 'a') as f:
#             f.write(nowTime + " " + type + " " + message + "\n")
#
#
# class MongodbP(object):
#     col_name = 'tencent_news'
#
#     def __init__(self):
#         client = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], connect=False)
#         self.conn = client[MONGODB_CONFIG['db']]
#         if self.conn:
#             print('MongoDB已连接1111')
#
#     def process_item(self, item):
#         # print("插入数据")
#         tid = {'Tid': item['Tid']}
#         res = self.conn[self.col_name].update_one(tid, {'$set': item}, upsert=True)
#         return res
#
#     def select_item(self, where, sort='_id', limit=0):
#         result = self.conn[self.col_name].find(where).sort(sort)
#         if limit > 0:
#             result = result.limit(limit)
#         return result
#
#     def update_item(self, where, item):
#         result = self.conn[self.col_name].update(where, item)
#         return result
#
#     def process_item_by_colname(self, name, item):
#         # print("插入数据")
#         tid = {'Tid': item['Tid']}
#         res = self.conn[name].update_one(tid, {'$set': item}, upsert=True)
#         return res
#
#     def select_item_by_colname(self, name, where, sort='_id', limit=0):
#         result = self.conn[name].find(where).sort(sort)
#         if limit > 0:
#             result = result.limit(limit)
#         return result
#
#
