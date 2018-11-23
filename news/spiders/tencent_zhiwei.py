# -*- coding: utf-8 -*-
import re
import json
import datetime,time
import scrapy
from scrapy.spiders import CrawlSpider, Rule, Spider, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from news.settings import DEFAULT_REQUEST_HEADERS
from news.items import TencentItem
from news.spiders.func import getHTMLText, ListCombiner, md5, get_crawl_days
import pymongo
from news.config import MONGODB_CONFIG


class TencentSpider(CrawlSpider):
    name = 'tencent_zhiwei'
    allowed_domains = ['news.qq.com', 'new.qq.com']
    start_urls = ['http://news.qq.com/']
    url_pattern1 = r'(.*)/a/(\d{8})/(\d+)\.htm'
    url_pattern2 = r'(.*)/omn/(.+)\.html'
    url_pattern2_ = r'(.*)/omn/(\d{8})/(.+)\.html'
    url_pattern3 = r'(.*)/omn/([A-Z0-9]{14,19})'
    url_pattern4 = r'(.*)/cmsn/([A-Z0-9]{8})/(.+)'
    rules = (
	    Rule(LinkExtractor(allow=(url_pattern1)),'parse_news1'),
        Rule(LinkExtractor(allow=(url_pattern2)),'parse_news2'),
        Rule(LinkExtractor(allow=(url_pattern3)),'parse_news3'),
        Rule(LinkExtractor(allow=(url_pattern4)),'parse_news2'),
    )

    def parse_news1(self, response):
        """
        https://news.qq.com/a/20180709/007392.htm
        """
        sel = Selector(response)
        pattern = re.match(self.url_pattern1, str(response.url))
        item = TencentItem()
        pat = lambda x: x[0] if x else ''
        channel = 'tencent'
        title = pat(sel.xpath('//h1/text()').extract())
        date = pattern.group(2)
        author = pat(sel.xpath('//*[@class="a_source"]//text()').extract())
        item['channel'] = channel
        item['title'] = title
        item['date'] = date
        item['author'] = author
        item['link'] = str(response.url)
        item['content'] = ListCombiner(
            sel.xpath('//*[@id="Cnt-Main-Article-QQ"]/p//text()').extract())
        item['img_link'] = sel.xpath(
            '//*[@id="Cnt-Main-Article-QQ"]/p/img/@src').extract()
        item['tid'] = md5(ListCombiner([channel, title, author, date]))
        return item

    def parse_news2(self, response):
        """
        http://new.qq.com/omn/20180709/20180709A039CA.html
        https://new.qq.com/cmsn/NEW20180/NEW20180708001061.html
        http://new.qq.com/cmsn/20180709/20180709000767.html
        http://new.qq.com/cmsn/20180709/TWF2018070902311500
        """
        sel = Selector(response)
        pattern = re.match(self.url_pattern2_, str(response.url))
        item = TencentItem()
        pat = lambda x: x[0] if x else ''
        channel = 'tencent'
        title = pat(sel.xpath('//h1/text()').extract())
        date = pattern.group(2)
        author = pat(sel.xpath('//*[@class="a_source"]//text()').extract())
        item['channel'] = channel
        item['title'] = title
        item['date'] = date
        item['author'] = author
        item['link'] = str(response.url)
        item['content'] = ListCombiner(sel.xpath('//p//text()').extract())
        item['img_link'] = sel.xpath('//p/img/@src').extract()
        item['tid'] = md5(ListCombiner([channel, title, author, date]))
        return item

    def parse_news3(self, response):
        """
        http://new.qq.com/omn/20180707A10IKG.html
        """
        sel = Selector(response)
        pattern = re.match(self.url_pattern3, str(response.url))
        item = TencentItem()
        channel = 'tencent'
        date = re.search(r"(\d{8})", pattern.group(2)).group(0)
        author = ''

        str1 = 'http://openapi.inews.qq.com/getQQNewsNormalContent?id='
        str2 = '&chlid=news_rss&refer=mobilewwwqqcom&otype=jsonp&ext_data=all&srcfrom=newsapp&callback=getNewsContentOnlyOutput'
        out = getHTMLText(str1+pattern.group(2)+str2)
        g = re.search("getNewsContentOnlyOutput\\((.+)\\)", out)
        out = json.loads(g.group(1))
        title = out["title"]

        item['channel'] = channel
        item['date'] = date
        item['title'] = title
        item['content'] = out["ext_data"]["cnt_html"]
        item['author'] = author
        item['link'] = str(response.url)
        item['img_link'] = sel.xpath('//p/img/@src').extract()
        item['tid'] = md5(ListCombiner([channel, title, author, date]))
        return item


class TencentRollSpider(Spider):
    name = 'test_zhiwei'
    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sport.qq.com', 'edu.qq.com',
                       'finance.qq.com', 'games.qq.com', 'auto.qq.com', 'house.qq.com']
    # start_urls = ['http://news.qq.com/articleList/rolls/']
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'

    list_url = 'http://roll.news.qq.com/interface/cpcroll.php?site={class_}&mode=1&cata=&date={date}&page={page}&_={time_stamp}'
    # date_time = datetime.datetime.now().strftime('%Y-%m-%d')
    date_time = '2018-7-3'
    time_stamp = int(round(time.time()*1000))

    def start_requests(self):
        categories = ['tech', 'news', 'ent', 'sports',
                      'finance', 'games', 'auto', 'edu', 'house']
        dates = get_crawl_days(self.date_time, 5400)

        # print(dates)

        for date in dates:
            for category in categories:
                DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
                DEFAULT_REQUEST_HEADERS['Host'] = 'roll.news.qq.com'
                DEFAULT_REQUEST_HEADERS['Referer'] = 'http://{}.qq.com/articleList/rolls/'.format(
                    category)

                url = self.list_url.format(class_=category, date=date, page='1', time_stamp=str(self.time_stamp))
                print(url)
                print(date)

                yield Request(self.list_url.format(class_=category, date=date, page='1', \
                                                   time_stamp=str(self.time_stamp)), callback=self.parse_list, \
                              meta={'category': category, 'date': date}, headers=DEFAULT_REQUEST_HEADERS)

                break
            break

    def parse_list(self, response):

        # print(response.body_as_unicode())
        sites = json.loads(response.body_as_unicode())


        print('sites:', sites)
        if sites['response']['code'] == 0 :
            for article in sites['data']['article_info']:
                print(article['title'])
                print(article['url'])






        return
        results = json.loads(response.text[9:-1])
        article_info = results['data']['article_info']
        category = response.meta['category']
        date = response.meta['date']
        for element in article_info:
            time_ = element['time']
            title = element['title']
            column = element['column']
            url = element['url']
            if column != u'图片':
                DEFAULT_REQUEST_HEADERS['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
                DEFAULT_REQUEST_HEADERS['Host'] = '{}.qq.com'.format(category)
                DEFAULT_REQUEST_HEADERS['Referer'] = ''

                yield Request(url, callback=self.parse_news, meta={'column': column,
                                                                   'url': url,
                                                                   'title': title,
                                                                   'time': time_,
                                                                   'category': category,
                                                                   'date': date
                                                                   },
                              dont_filter=True, headers=DEFAULT_REQUEST_HEADERS)
        # 翻页
        list_page = results['data']['page']
        list_counts = results['data']['count']
        if list_page < list_counts:
            time_stamp = int(round(time.time() * 1000))
            yield Request(self.list_url.format(class_=category, date=date,
                    page=str(list_page+1), time_stamp=str(time_stamp)), \
                    callback=self.parse_list, meta={'category': category, 'date': date}, dont_filter=True)

    def parse_news(self, response):
        """
        https://news.qq.com/a/20180709/007392.htm
        """
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        item = TencentItem()

        # url = response.meta['url']
        # title = response.meta['title']
        # column = response.meta['column']
        # time_ = response.meta['time']
        # category = response.meta['category']

        def pat(x): return x[0] if x else ''
        channel = 'tencent'
        title = pat(sel.xpath('//h1/text()').extract())
        date_ = pattern.group(2)
        author = pat(sel.xpath('//*[@class="a_source"]//text()').extract())
        item['channel'] = channel
        item['title'] = title
        item['date'] = date_
        item['author'] = author
        item['link'] = str(response.url)
        item['content'] = ListCombiner(
            sel.xpath('//*[@id="Cnt-Main-Article-QQ"]/p//text()').extract())
        item['img_link'] = sel.xpath(
            '//*[@id="Cnt-Main-Article-QQ"]/p/img/@src').extract()
        item['tid'] = md5(ListCombiner([channel, title, author, date_]))
        return item

class MongodbP(object):
    col_name = 'tieba_name'

    def __init__(self):
        client = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], connect=False)
        self.conn = client[MONGODB_CONFIG['db']]
        if self.conn:
            print('MongoDB已连接1111')

    def process_item(self, item):
        print("插入数据")
        self.conn[self.col_name].insert_one(item)
        return item

    def select_item(self, where, sort=[]):
        result = self.conn[self.col_name].find(where).sort(sort)
        return result

    def update_item(self, where, item):
        result = self.conn[self.col_name].update(where, item)
        return result
