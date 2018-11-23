# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import os
import pymongo
from news.config import MONGODB_CONFIG

from news.conn import db


class NewsPipeline(object):
    conn = ''

    def __init__(self):
        # 219服务器
        client = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], connect=False)
        self.conn = client[MONGODB_CONFIG['db']]
        if self.conn:
            print('MongoDB已连接')

    def process_item(self, item, spider):
        # if item.item_name == "tencent":
        #     db_name = 'tencent'
        #     filter_data = {'Tid': item['Tid']}
        # print(item)
        # update_data = dict(item)
        # self.conn[db_name].update_one(filter_data, {'$set': update_data}, upsert=True)
        self.conn["tencent_news"].insert_one(item)
        return item

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
        # tid = {'Tid': item['Tid']}
        res = self.conn[name].insert_one(item)
        # res = self.conn[name].update_one(tid, {'$set': item}, upsert=True)
        return res

    def select_item_by_colname(self, name, where, sort='_id', limit=0):
        #result = self.conn[name].find(where).sort(sort)
        #if limit > 0:
        #    result = result.limit(limit)
        result = self.conn[name].find_one(where)
        return result
        # return result
