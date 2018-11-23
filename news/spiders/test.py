# -*- coding: utf-8 -*-import reimport jsonimport datetime, timeimport requestsimport randomimport mathimport sysimport scrapyimport pymongofrom urlparse import urlparsefrom scrapy.spiders import CrawlSpider, Rule, Spider, Requestfrom scrapy.linkextractors import LinkExtractorfrom scrapy.selector import Selectorfrom news.settings import DEFAULT_REQUEST_HEADERSfrom news.items import UrlItemfrom news.spiders.func import getHTMLText, ListCombiner, md5, get_crawl_daysfrom news.config import MONGODB_CONFIGfrom news.middlewares.resource import PROXIES, PORTfrom news.util import gen_idclass MongodbP(object):    col_name = 'date_url'    def __init__(self):        client = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], connect=False)        self.conn = client[MONGODB_CONFIG['db']]        if self.conn:            print('MongoDB已连接1111')    def process_item(self, item):        # print("插入数据")        res = self.conn[self.col_name].insert_one(item)        return res    def select_item(self, where, sort='_id', limit=0):        result = self.conn[self.col_name].find(where).sort(sort)        if limit > 0:            result = result.limit(limit)        return result    def update_item(self, where, item):        result = self.conn[self.col_name].update(where, item)        return result    def process_item_by_colname(self, name, item, ):        # print("插入数据")        tid = {'Tid': item['Tid']}        res = self.conn[name].update_one(tid, {'$set': item}, upsert=True)        return res    def select_item_by_colname(self, name, where):        result = self.conn[name].find_one(where)        return resultclass TencentNewsSpider(CrawlSpider):    name = 'test'    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sports.qq.com', 'edu.qq.com',                       'finance.qq.com', 'games.qq.com', 'house.qq.com', 'auto.qq.com']    url_pattern = u'http://{}/a/{}/0{}.htm'    # allowed_domains = ['news.qq.com']    mongo = MongodbP()    def start_requests(self):        print("starting")        # result = self.mongo.select_item_by_colname('tencent_domain_1', {'status': 0})        # date_list = ["20160325", "20171008", "20180508"]        # for date in date_list:        result = self.mongo.select_item_by_colname('tencent_domain_1', {"status": 0})        if result:            info = result            info['status'] = 1            self.mongo.process_item_by_colname('tencent_domain_1', info)            for i in range(1, 99999):                num = ''                if i < 10:                    num = '0000' + str(i)                elif i < 100:                    num = '000' + str(i)                elif i < 1000:                    num = '00' + str(i)                elif i < 10000:                    num = '0' + str(i)                else:                    num = str(i)                url = self.url_pattern.format(info["domain"], info["date"], num)                print(url)                yield Request(url, callback=self.parse_news, dont_filter=False, meta={"date": info["date"]},                                headers=DEFAULT_REQUEST_HEADERS)        # urls = ['http://tech.qq.com/a/20100505/000931.htm', 'http://tech.qq.com/a/20100505/000932.htm',        #         'http://tech.qq.com/a/20100505/000531.htm', 'http://tech.qq.com/a/20100505/000530.htm',        #         "http://news.qq.com/a/20090708/006102.htm"]        # urls = ['http://news.qq.com/a/20170310/00000343.htm', 'http://news.qq.com/a/20170310/00000486.htm',        #         'http://news.qq.com/a/20180808/00000799.htm', 'http://news.qq.com/a/20180808/000001075.htm',        #         "http://tech.qq.com/a/20170310/000003753.htm", "http://tech.qq.com/a/20140510/00000446.htm",        #         "http://tech.qq.com/a/20180808/0000016.htm", "http://ent.qq.com/a/20170310/000001652.htm"]        # for url in urls:        #     # print('url:', url)        #     yield Request(url, callback=self.parse_news, dont_filter=False, headers=DEFAULT_REQUEST_HEADERS)    def parse_news(self, response):        print("starting parse")        if response.status == 200:            title = response.xpath('//head//title/text()').extract_first()            if title != u'404-1':                print("sucessful : %s" % (response.url, ))                item = dict()                item["url"] = response.url.replace("https", "http")                item["date"] = response.meta["date"]                item["status"] = 0                try:                    self.mongo.conn["date_url"].insert_one(item)                except Exception as e:                    print(e)                self.mongo.conn["date_url"].ensure_index('url', unique=True)                self.mongo.conn["date_url"].ensure_index('date')def fetchUrl(url):    proxy = random.choice(PROXIES)    proxy_url = 'http://{}:{}'.format(proxy, PORT)    proxy_dict = {"http": proxy_url}    # DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'    DEFAULT_REQUEST_HEADERS[        'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'    # DEFAULT_REQUEST_HEADERS['Host'] = 'tech.qq.com'    DEFAULT_REQUEST_HEADERS['Referer'] = ''    category = url[url.find('//') + 2: url.find('.')]    DEFAULT_REQUEST_HEADERS['Host'] = "{}.qq.com".format(category)    return requests.get(url, proxies=proxy_dict, headers=DEFAULT_REQUEST_HEADERS)def writeDebugMessage(type, message):    write = True    filename = 'debug.log'    if write:        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))        with open(filename, 'a') as f:            f.write(nowTime + " " + type + " " + message + "\n")def writeTimeMessage(type, message):    write = False    filename = 'time.log'    if write:        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))        with open(filename, 'a') as f:            f.write(nowTime + " " + type + " " + message + "\n")