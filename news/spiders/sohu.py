# -*- coding: utf-8 -*-
import re
import json
import datetime
import time
import random
import requests
from scrapy.spiders import Spider, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from news.settings import DEFAULT_REQUEST_HEADERS
from news.items import TencentItem
from news.spiders.func import getHTMLText, ListCombiner, md5, get_crawl_days
import sys
reload(sys)
sys.setdefaultencoding("utf8")

class SohuSpider(Spider):
    name = 'sohu'
    allowed_domains = ['sohu.com', 'v2.sohu.com',
                       'mil.sohu.com', 'society.sohu.com']
    # start_urls = ['http://souhu.com/']
    # http://www.sohu.com/a/240224969_161623
    # parse_pat = "(.*)sohu.com/a/(\d{9})_(\d+)"
    list_url = "http://v2.sohu.com/public-api/feed?scene={scene}&sceneId={scene_id}&page={page}&size=20&callback=jQuery112409677698489404083_{time_stamp}&_={time_stamp_}"
    # url_start = [('http://www.sohu.com/c/8/1460', 'CATEGORY', '1460'),
    #              ('http://www.sohu.com/c/8/1461', 'CATEGORY', '1461'),
    #              ('http://www.sohu.com/c/8/1462', 'CATEGORY', '1462'),
    #              ('http://www.sohu.com/c/8/1463', 'CATEGORY', '1463'),
    #              ('http://mil.sohu.com/', 'CHANNEL', '10'),
    #              ('http://society.sohu.com/', 'CHANNEL', '43'),
    #              ]
    urls = [
        # ('http://mil.sohu.com/', 'CHANNEL', '10'),
        # ('http://society.sohu.com/', 'CHANNEL', '43'),
    ]
    base_url = "http://www.sohu.com/a/"

    def _init_url(self):
        # 手动增加待爬取网页
        # 1460~1483;
        for i in range(1460, 1483): self.urls.append(('CATEGORY', str(i)))
        # 10~19,缺11；23~30; 41~46;
        for i in range(10,20): self.urls.append(('CHANNEL', str(i)))
        for i in range(23,31): self.urls.append(('CHANNEL', str(i)))
        for i in range(41,47): self.urls.append(('CHANNEL', str(i)))
        
        tag_lists = ['mil', 'health', 'society',
                     'business', 'history', 'travel', 
                     'learning', 'fashion', 'it', 
                     'baobao', 'chihe', 'cul', 
                     'astro', 'game', 'fun', 'acg', 'pets']
        for i in tag_lists:
            url = "http://{}.sohu.com/".format(i)
            resp = requests.get(url)
            ser = Selector(resp)
            lists = ser.xpath('//*[@id="left-nav"]//p/a/@href').extract()
            pat = r"(.*)sohu.com/tag/(\d+)"
            # ids = [i.split('/')[-1] for i in lists]
            ids = [ re.match(pat, i).groups()[1] for i in lists if re.match(pat, i)]
            for j in ids:
                self.urls.append(('TAG', str(j)))

    def start_requests(self):
        """
        http://www.sohu.com/c/8/1460  # 时政
            http://v2.sohu.com/public-api/feed?scene=CATEGORY&sceneId=1460&page=4&size=20&callback=jQuery112409677698489404083_1531189129879&_=1531189129899
        http://www.sohu.com/c/8/1461  # 国际
            http://v2.sohu.com/public-api/feed?scene=CATEGORY&sceneId=1461&page=2&size=20&callback=jQuery1124049199068046830385_1531190948977&_=1531190949022
        http://www.sohu.com/c/8/1462  # 社会
        http://www.sohu.com/c/8/1463  # 财经

        http://mil.sohu.com/ # 军事
            http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=10&page=3&size=20&callback=jQuery1124015149764043938707_1531191149427&_=1531191149447
            
            http://www.sohu.com/tag/68942
                http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=68942&page=3&size=20&callback=jQuery112404364346956366172_1531190666358&_=1531190666379


        http://society.sohu.com/ # 社会
            http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=43&page=2&size=20&callback=jQuery1124024381928962940513_1531191275875&_=1531191275899
            
            http://www.sohu.com/tag/72020
                http://v2.sohu.com/public-api/feed?scene=TAG&sceneId=72020&page=3&size=20&callback=jQuery1124017729912574429418_1531191360254&_=1531191360277

        # http://police.news.sohu.com/ # 警法
        # http://gongyi.sohu.com/ #公益
        # http://news.sohu.com/wurenji/index.shtml #无人机

        http://v2.sohu.com/public-api/feed?scene=CATEGORY&sceneId=1460&page=3&size=20&callback=jQuery112407722034989128386_1531201482224&_=1531201482300
        http://www.sohu.com/a/240253062_100180399
        http://www.sohu.com/a/240240714_114890
        http://www.sohu.com/a/240224969_161623  article_id author_id
        """ 
        self._init_url()
        print self.urls, '\n', len(self.urls)
        for scene, scene_id in self.urls:
            time_stamp = int(round(time.time()*1000))
            time_stamp_ = str(time_stamp + random.randint(5, 15))
            DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
            DEFAULT_REQUEST_HEADERS['Host'] = 'v2.sohu.com'
            # DEFAULT_REQUEST_HEADERS['Referer'] = 'http://www.sohu.com/{}/{}'.format(
                # tag, tag_id)
            yield Request(self.list_url.format(scene=scene, scene_id=scene_id, page='1',
                                time_stamp=str(time_stamp), time_stamp_=time_stamp_), callback=self.parse_list,
                                meta={'scene': scene, 'scene_id': scene_id, 'page': '1'}, headers=DEFAULT_REQUEST_HEADERS)

    def parse_list(self, response):
        scene = response.meta['scene']
        scene_id = response.meta['scene_id']
        page = int(response.meta['page'])
        pat = r".*jQuery.*\((\[.*?\])\);"
        pattern = re.match(pat, response.text).groups()[0]
        results = json.loads(pattern)
        for data in results:
            article_id = data.get('id', '')
            author_id = data.get('authorId', '')
            author = data.get('authorName', '')
            name = data.get('title', '')
            date = data.get('publicTime', '')
            url = "{}{}_{}".format(self.base_url, article_id, author_id)
            DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
            DEFAULT_REQUEST_HEADERS['Host'] = 'v2.sohu.com'
            # DEFAULT_REQUEST_HEADERS['Referer'] = 'http://www.sohu.com/{}/{}'.format(
                # tag, tag_id)
            yield Request(url, meta={'author': author, 'name': name, 'date': date}, callback=self.parse_news, headers=DEFAULT_REQUEST_HEADERS)
          
        # 翻页
        if len(results) == 20:
            page = str(page + 1)
            time_stamp = int(round(time.time()*1000))
            time_stamp_ = str(time_stamp + random.randint(5, 15))
            DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
            DEFAULT_REQUEST_HEADERS['Host'] = 'v2.sohu.com'
            # DEFAULT_REQUEST_HEADERS['Referer'] = 'http://www.sohu.com/{}/{}'.format(
                # tag, tag_id)
            yield Request(self.list_url.format(scene=scene, scene_id=scene_id, page=page,
                                time_stamp=str(time_stamp), time_stamp_=time_stamp_), callback = self.parse_list,
                                meta={'scene': scene, 'scene_id': scene_id, 'page': page}, headers=DEFAULT_REQUEST_HEADERS)
        


    def parse_news(self, response):
        sel = Selector(response)
        item = TencentItem()
        channel = 'sohu'
        title = response.meta['name']
        date = str(response.meta['date'])
        author = response.meta['author']
        item['channel'] = channel
        item['title'] = title
        item['date'] = date
        item['author'] = author
        item['link'] = str(response.url)
        item['content'] = ListCombiner(
            sel.xpath('//*[@id="mp-editor"]/p//text()').extract()[1:-2])
        item['img_link'] = sel.xpath('//p/img/@src').extract()
        item['tid'] = md5(ListCombiner([channel, title, author, date]))
        return item

    

