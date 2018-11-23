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


class IfengSpider(Spider):
    name = 'ifeng'
    allowed_domains = ['ifeng.com']
    start_urls = ['http://ifeng.com/']
    list_url = "http://v2.sohu.com/public-api/feed?scene={scene}&sceneId={scene_id}&page={page}&size=20&callback=jQuery112409677698489404083_{time_stamp}&_={time_stamp_}"

    def parse(self, response):
        pass
    urls = []
    base_url = "http://www.sohu.com/a/"

    def _init_url(self):
        """
        http://finance.ifeng.com/listpage/2/marketlist.shtml

        http://news.ifeng.com/listpage/11502/20180711/2/rtlist.shtml
            "/html/body/div[12]/div[1]/div/ul/li/a/@href"  60 <55

        http://tech.ifeng.com/listpage/800/20180710/1/rtlist.shtml
            "//*[@id="box_content"]//h2/a/@href"   55 <55


        http://tech.ifeng.com/listpage/11517/1/list.shtml
        http://tech.ifeng.com/listpage/11493/1/list.shtml
        http://tech.ifeng.com/listpage/11516/1/list.shtml
        http://tech.ifeng.com/listpage/6529/1/list.shtml
        http://tech.ifeng.com/listpage/803/1/list.shtml
        http://tech.ifeng.com/listpage/801/1/list.shtml
        http://tech.ifeng.com/listpage/806/1/list.shtml
        http://tech.ifeng.com/listpage/824/1/list.shtml
        http://tech.ifeng.com/listpage/805/1/list.shtml
        http://tech.ifeng.com/listpage/3003/1/list.shtml
            "//*[@id="box_content"]//h2/a/@href" 55 20页
        
        http://tech.ifeng.com/discovery/
        http://digi.ifeng.com/
        http://digi.ifeng.com/mobile/

        http://finance.ifeng.com/a/20180711/16378182_0.shtml
        """
        # 手动增加待爬取网页
        # 1460~1483;
        for i in range(1460, 1483):
            self.urls.append(('CATEGORY', str(i)))
        # 10~19,缺11；23~30; 41~46;
        for i in range(10, 20):
            self.urls.append(('CHANNEL', str(i)))
        for i in range(23, 31):
            self.urls.append(('CHANNEL', str(i)))
        for i in range(41, 47):
            self.urls.append(('CHANNEL', str(i)))

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
            ids = [re.match(pat, i).groups()[1]
                   for i in lists if re.match(pat, i)]
            for j in ids:
                self.urls.append(('TAG', str(j)))

    def start_requests(self):
        """
        
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
                                               time_stamp=str(time_stamp), time_stamp_=time_stamp_), callback=self.parse_list,
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
