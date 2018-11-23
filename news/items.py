# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TencentItem(scrapy.Item):
    # Tid = scrapy.Field()  # document编号,一个帖子的编号
    Link = scrapy.Field()
    item_name = 'tencent'
    Category = scrapy.Field()
    Title = scrapy.Field()
    From = scrapy.Field()
    Time = scrapy.Field()
    ReadCount = scrapy.Field()
    Content = scrapy.Field()
    PostCount = scrapy.Field()
    Posts = scrapy.Field()
    _id = scrapy.Field()


class TiebaItem(scrapy.Item):
    """贴吧信息
    """
    item_name = 'tieba'
    # define the fields for your item here like:
    # name = scrapy.Field()
    channel = 'Tieba' # 渠道
    name = scrapy.Field() # 贴吧名
    post_num = scrapy.Field() # 帖子数
    men_num = scrapy.Field() # 关注数

class PostItem(scrapy.Item):
    """帖子信息
    """
    item_name = 'post'
    id = scrapy.Field() # 帖子id
    title = scrapy.Field() # 贴名
    author = scrapy.Field() # 作者
    reply_num = scrapy.Field() # 回复数
    good = scrapy.Field()  # 加精
    name = scrapy.Field()  # 贴吧

class FloorItem(scrapy.Item):
    """楼层信息
    """
    item_name = 'floor'
    id = scrapy.Field()
    floor = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    img_link = scrapy.Field()
    comment_num = scrapy.Field()
    post_id = scrapy.Field()


class CommentItem(scrapy.Item):
    """楼中评论
    """
    item_name = 'comment'
    id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    floor_id = scrapy.Field()
    post_id = scrapy.Field()


class DomainDate(scrapy.Item):
    """
    滚动日期
    """
    item_name = 'date'
    Tid = scrapy.Field()
    _id = scrapy.Field()
    domain = scrapy.Field()
    date = scrapy.Field()
    status = scrapy.Field()


class UrlItem(scrapy.Item):
    item_name = "url"
    url = scrapy.Field()
    date = scrapy.Field()
    status = scrapy.Field()



class NewUrlItem(scrapy.Item):
    item_name = "new_url"
    Tid = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    status = scrapy.Field()
    scrapy_time = scrapy.Field()
