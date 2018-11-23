# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule, Spider, Request
from news.settings import DEFAULT_REQUEST_HEADERS
import datetime
import time
from news.pipelines import NewsPipeline
import json


class TencentRollNewsSpider(Spider):
    name = "tencent_rolls_news_spider"

    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sports.qq.com', 'edu.qq.com',
                       'finance.qq.com', 'games.qq.com', 'auto.qq.com', 'house.qq.com']
    # allowed_domains = ['house.qq.com']
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'

    list_url = 'http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site={class_}&mode=1&cata=&date={date}&page={page}&_={time_stamp}'
    date_time = datetime.datetime.now().strftime('%Y-%m-%d')
    time_stamp = int(round(time.time() * 1000))
    item_num = 0
    urls = []
    mongo = NewsPipeline()

    def start_requests(self):
        print("starting")
        result = self.mongo.select_item_by_colname('date', {"status": 0})
        # datelist = ["20140303", "20150510", "20161210", "20170210", "20180810"]
        # datelist = ["20160325", "20171008", "20180508"]

        # result = self.mongo.select_item_by_colname('tencent_domain', {"date": date, 'domain': domain})
        # result = self.mongo.select_item_by_colname('tencent_domain_1', {"date": date, "status": 0})
        print(result)
        if result:
            info = result
            info['status'] = 1
            self.mongo.process_item_by_colname('date', info)
            domain = "sports.qq.com"
            category = domain.split(".")[0]
            DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
            DEFAULT_REQUEST_HEADERS['Host'] = 'roll.news.qq.com'
            DEFAULT_REQUEST_HEADERS['Referer'] = 'http://{}.qq.com/articleList/rolls/'.format(category)
            date = info["date"]
            new_date = date[0:4]+"-"+date[4:6]+"-"+date[6:]
            print(new_date)
            url = self.list_url.format(class_=category, date=new_date, page='1', time_stamp=str(self.time_stamp))
            yield Request(
                url,
                dont_filter=True,
                callback=self.parse_list, meta={'category': category, 'date': new_date},
                headers=DEFAULT_REQUEST_HEADERS)

    def parse_list(self, response):
        # print("page***********************")
        results = json.loads(response.text[9:-1])
        article_info = results['data']['article_info']
        # print(article_info)
        category = response.meta['category']
        for element in article_info:
            url = element['url']
            item = dict()
            item["url"] = url
            item["date"] = ''.join(response.meta["date"].split("-"))
            item["status"] = 0
            try:
                print(item)
                self.mongo.conn["date_url"].insert_one(item)
            except Exception as e:
                print(e)
            self.mongo.conn["date_url"].ensure_index('url', unique=True)
            self.mongo.conn["date_url"].ensure_index('date')
            print("url: %s" % (url,))
        list_page = results['data']['page']
        list_count = results['data']['count']
        print("page %d, count %d" % (list_page, list_count))
        if list_page <= list_count:
            time_stamp = int(round(time.time() * 1000))
            yield Request(self.list_url.format(class_=category, date=response.meta['date'], page=str(list_page + 1),
                                               time_stamp=str(time_stamp)), callback=self.parse_list,
                          dont_filter=True,
                          meta=response.meta, headers=DEFAULT_REQUEST_HEADERS)
