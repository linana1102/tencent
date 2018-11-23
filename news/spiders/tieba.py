# -*- coding: utf-8 -*-
import json,time
import scrapy

from scrapy.spiders import Spider, Request
from scrapy.selector import Selector
from news.items import TiebaItem, PostItem, CommentItem, FloorItem
from news.settings import DEFAULT_REQUEST_HEADERS
from func import is_ad, parse_content
from six.moves.urllib.parse import quote
from news.conn import db


class TiebaSpider(Spider):
    name = 'tieba'
    allowed_domains = ['baidu.com']
    max_page = 100
    # start_urls = ['http://baidu.com/']
    url_tieba = "https://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}"
    url_tiezi = "http://tieba.baidu.com/p/{}?pn={}"

    def start_requests(self):
        """
        https://tieba.baidu.com/f/index/forumpark?pcn=娱乐明星&pci=0&ct=1&rn=20&pn=1
        https://tieba.baidu.com/f/index/forumpark?cn=港台东南亚明星&ci=0&pcn=娱乐明星&pci=0&ct=1&rn=20&pn=1
        https://tieba.baidu.com/f/index/forumpark?cn=内地明星&ci=0&pcn=娱乐明星&pci=0&ct=1&rn=20&pn=1
        http://tieba.baidu.com/f?kw=%E4%B8%AD%E5%9B%BD%E5%A5%BD%E5%A3%B0%E9%9F%B3
        http://tieba.baidu.com/f?kw=%E4%B8%AD%E5%9B%BD%E5%A5%BD%E5%A3%B0%E9%9F%B3 # 中国好声音
        //*[@id="ba_list"]/div/a/@href  tieba链接
        //*[@id="thread_list"]/li/div/div[2]/div[1]/div[1]/a/@href  帖子链接

        https://tieba.baidu.com/f?kw=%E4%B8%96%E7%95%8C%E6%9D%AF
        """
        lst_tieba = [u'李毅']
        for i in lst_tieba:
            url = self.url_tieba.format(i, 0)
            DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
            DEFAULT_REQUEST_HEADERS['Host'] = 'tieba.baidu.com'
            yield Request(url, callback=self.parse_tieba, meta={'name': i, 'page': 0}, headers=DEFAULT_REQUEST_HEADERS)

    def parse_tieba(self, response):
        """
        http://tieba.baidu.com/p/5796438629 帖子链接格式
        
        """
        name = response.meta['name']
        page_ = response.meta['page']
        # ser = Selector(response)
        ser = Selector(text=response.text.replace("<!--", '').replace("-->", ""))
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        if not page_:
            tieba = TiebaItem()
            tieba['name'] = name
            """
            response.xpath("//*[@id='pagelet_html_forum/pagelet/forum_card_number']").extract()
            [u'<code class="pagelet_html" id="pagelet_html_forum/pagelet/forum_card_number" style="display:none;"><!--<span class="">\r\n  <span class="card_numLabel">\u5173\u6ce8\uff1a</span>\r\n  <span class="card_menNum">3,199,027</span>\r\n  <span class="card_numLabel">\u8d34\u5b50\uff1a</span>\r\n  <span class="card_infoNum">14,047,464</span>\r\n</span>\r\n--></code>']
            """
            # sel1 = Selector(text=response.xpath("//*[@id='pagelet_html_forum/pagelet/forum_card_number']").extract_first(
            # ).replace("<!--", '').replace("-->", ""))
            tieba['men_num'] = ser.xpath(
                "//span[@class='card_menNum']/text()").extract_first()
            tieba['post_num'] = ser.xpath(
                "//span[@class='card_infoNum']/text()").extract_first()
            yield tieba

        # lists = ser.xpath(
        #     "//a[starts-with(@href,'/p/')]/@href").extract()
        for sel in ser.xpath('//li[contains(@class, "j_thread_list")]'):
            data = json.loads(sel.xpath('@data-field').extract_first())
            tiezi = PostItem()
            tiezi_id = data['id']
            tiezi['name'] = name
            tiezi['id'] = tiezi_id
            tiezi['author'] = data['author_name']
            tiezi['reply_num'] = data['reply_num']
            tiezi['good'] = data['is_good']
            if not tiezi['good']:
                tiezi['good'] = False
            tiezi['title'] = sel.xpath('.//div[contains(@class, "threadlist_title")]/a/text()').extract_first()   
            yield tiezi
            
            meta = {'name': name, 'post_id': tiezi_id, 'page': 1}
            url_tz = self.url_tiezi.format(tiezi_id, 1)
            yield Request(url_tz, callback=self.parse_tiezi,  meta=meta)

        # 翻页
        """https://tieba.baidu.com/f?kw=%E4%B8%96%E7%95%8C%E6%9D%AF&ie=utf-8&pn=50""" <= 50
        # next_page = sel.xpath('//a[@class="next pagination-item "]/@href')
        # if next_page:
        #     url_tb = 'http:{}'.format(next_page.extract_first())
        #     yield Request(url_tb, callback = self.parse_tieba, meta={'name': name, 'next': True})
        page_ += 1
        url_tb = self.url_tieba.format(name, 50*page_)
        DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
        DEFAULT_REQUEST_HEADERS['Host'] = 'tieba.baidu.com'
        yield Request(url_tb, callback=self.parse_tieba, meta={'name': name, 'page': page_}, headers=DEFAULT_REQUEST_HEADERS)
        

    def parse_tiezi(self, response):
        meta = response.meta
        page_ = meta['page']
        post_id_ = meta['post_id']
        has_comment = False
        for floor in response.xpath("//div[contains(@class, 'l_post')]"):
            if not is_ad(floor):
                data = json.loads(floor.xpath("@data-field").extract_first())
                item = FloorItem()
                item['id'] = data['content']['post_id']
                item['author'] = data['author']['user_name']
                item['comment_num'] = data['content']['comment_num']
                if item['comment_num'] > 0:
                    has_comment = True
                content = floor.xpath(
                    ".//div[contains(@class,'j_d_post_content')]/text()").extract_first()
                img_link = floor.xpath(
                    ".//div[contains(@class,'j_d_post_content')]/img/@src").extract()
                item['content'] = parse_content(content)
                item['img_link'] = img_link
                item['post_id'] = post_id_
                item['floor'] = data['content']['post_no']
                if 'date' in data['content'].keys():
                    item['time'] = data['content']['date']
                else:
                    item['time'] = floor.xpath(".//span[@class='tail-info']")\
                        .re_first(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}')
                yield item
        
        # 是否楼中楼
        if has_comment:
            url = "http://tieba.baidu.com/p/totalComment?tid=%d&fid=1&pn=%d" % (
                post_id_, page_)
            yield Request(url, callback=self.parse_comment, meta=meta)
        
        # 翻页
        next_page = response.xpath(
            u".//ul[@class='l_posts_num']//a[text()='下一页']/@href")
        if next_page:
            meta['page'] += 1
            url = response.urljoin(next_page.extract_first())
            yield Request(url, callback=self.parse_tiezi, meta=meta)
        # page_ += 1
        # meta['page'] = page_
        # url_tz = self.url_tiezi.format(post_id_, page_)
        # yield Request(url_tz, callback=self.parse_tiezi,  meta=meta)

    def parse_comment(self, response):
        comment_list = json.loads(response.body.decode('utf8'))[
            'data']['comment_list']
        for value in comment_list.values():
            comments = value['comment_info']
            for comment in comments:
                item = CommentItem()
                item['id'] = comment['comment_id']
                item['author'] = comment['username']
                item['floor_id'] = comment['post_id']
                item['post_id'] = comment['thread_id']
                item['content'] = parse_content(comment['content'])
                item['time'] = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(comment['now_time']))
                yield item
