# -*- coding: utf-8 -*-

from news.config import MONGODB_CONFIG
import pymongo
from datetime import datetime, timedelta
from news.items import DomainDate
from news.util import gen_id
import re


class MongodbP(object):
    col_name = 'tencent_domain'

    def __init__(self):
        client = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], connect=False)
        self.conn = client[MONGODB_CONFIG['db']]
        if self.conn:
            print('MongoDB已连接1111')

    def process_item(self, itemlist):
        # print("插入数据")
        # tid = {'Tid': item['Tid']}
        # res = self.conn[self.col_name].update_one(tid, {'$set': item}, upsert=True)
        res = self.conn[self.col_name].insert_many(itemlist)

    def select_item(self, where, sort='_id', limit=0):
        result = self.conn[self.col_name].find(where).sort(sort)
        if limit > 0:
            result = result.limit(limit)
        return result

    def update_item(self, where, item):
        result = self.conn[self.col_name].update(where, item)
        return result

    def process_item_by_colname(self, name, itemlist):
        # print("插入数据")
        try:
            res = self.conn[name].insert_many(itemlist)
        except Exception as e:
            print(e)
        return res

    def select_item_by_colname(self, name, where, sort='_id', limit=0):
        result = self.conn[name].find(where).sort(sort)
        if limit > 0:
            result = result.limit(limit)
        return result


def gen_dates(b_date, days):
    day = timedelta(days=1)
    for i in range(days):
        yield b_date + day*i


def get_date_list(start=None, end=None):
    """
    获取日期列表
    :param start: 开始日期
    :param end: 结束日期
    :return:
    """
    if start is None:
        start = datetime.strptime("2009-01-01", "%Y-%m-%d")
    if end is None:
        end = datetime.now()
    data = []
    for d in gen_dates(start, (end-start).days):

        data.append(d.strftime("%Y%m%d"))
    return data


# def gen_id(li):
#     st = ''.join(li)
#     if isinstance(st, unicode):
#         st = st.encode('utf-8')
#     return hashlib.md5(st).hexdigest()


def save_domain_date(start=None, end=None):

    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sports.qq.com', 'edu.qq.com',
                       'finance.qq.com', 'games.qq.com', 'house.qq.com', 'auto.qq.com']
    mongo = MongodbP()

    datelist = get_date_list(start, end)
    for date in datelist[-1::-1]:
        itemlist = []
        for domain in allowed_domains:
            item = DomainDate()
            item["Tid"] = gen_id([domain, date])
            item["_id"] = item["Tid"]
            item["status"] = 0
            item["domain"] = domain
            item["date"] = date
            itemlist.append(item)
        try:
            # mongo.process_item(itemlist)
            mongo.process_item_by_colname("tencent_domain_1", itemlist)
        except Exception as e:
            print(e)
            print("要插入的数据是：%s" % (date, ))

        # result = mongo.select_item_by_colname("tencent_domain", {"status": 1, "url": 'news.qq.com'})
        # print(result.count())


def save_date(start=None, end=None):

    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sports.qq.com', 'edu.qq.com',
                       'finance.qq.com', 'games.qq.com', 'house.qq.com', 'auto.qq.com']
    mongo = MongodbP()

    datelist = get_date_list(start, end)
    for date in datelist[-1::-1]:
        item = dict()
        item["Tid"] = gen_id([date])
        item["_id"] = item["Tid"]
        item["status"] = 0
        item["date"] = date
        try:
            # mongo.process_item(itemlist)
            mongo.conn["date"].insert_one(item)
        except Exception as e:
            print(e)
            print("要插入的数据是：%s" % (date, ))

        # result = mongo.select_item_by_colname("tencent_domain", {"status": 1, "url": 'news.qq.com'})
        # print(result.count())


def generate_id(i):
    num = ''
    if i < 10:
        num = '0000' + str(i)
    elif i < 100:
        num = '000' + str(i)
    elif i < 1000:
        num = '00' + str(i)
    elif i < 10000:
        num = '0' + str(i)
    else:
        num = str(i)
    return num


def info_check():
    mong = MongodbP()
    allowed_domains = ['news.qq.com', 'tech.qq.com', 'ent.qq.com', 'sports.qq.com', 'edu.qq.com',
                       'finance.qq.com', 'games.qq.com', 'auto.qq.com', 'house.qq.com']
    datelist = ["20160325", "20171008", "20180508"]

    url_pattern = u'http://{}/a/{}/0{}.htm'
    # for domain in allowed_domains:
    #     print(domain)
    for date in datelist:
        # print("date:%s, domain: %s" % (date, domain))
        result = mong.conn["date_url"].find({"date": {"$gt":"20130630"}},
                                            {"url": 1, "_id": 0})
        url_list = []
        for item in result:
            url_list.append(item["url"].split(":")[1])
            # num_list.append(int(item["url"].split("/")[5].split(".")[0]))
        # print(len(url_list))
        # print(num_list[-1::-1])
        # max_diff = 1
        # diff_dict = {}
        # count_dict = {}
        # for i in range(2, len(num_list)):
        #     tmp = num_list[i]-num_list[i-1]
        #     if tmp > max_diff:
        #         num = num_list[i]
        #         max_diff = tmp
            # diff_dict[tmp] = diff_dict.get(tmp, 0) + 1
            # if tmp > 20:
            #     print("diff:  %d" % (tmp, ))
            #     url1 = url_pattern.format(domain, date, generate_id(num_list[i-1]))
            #     url2 = url_pattern.format(domain, date, generate_id(num_list[i]))
            #     print("%s,  %s," % (url1, url2))
        # print(diff_dict)
        # print("max_diff %d" % (max_diff, ))

        # num_len = len(num_list)
        # for i in num_list:
        #     for j in range(10000, 50000, 10000):
        #         if i <= j:
        #             count_dict[j] = (count_dict.get(j, 0)+1)
        #
        # for key, value in count_dict.items():
        #     count_dict[key] = str(count_dict[key]*100/num_len)+"%"
        # print("date: %s, total nume: %d" % (date, num_len), sorted(count_dict.items(), key=lambda item: item[0]))
        new_date = date[0:4] + "-" + date[4:6] + "-" + date[6:]
        interface_results = mong.conn["interface_date_url"].find({"date": new_date, "url": re.compile(domain)},
                                            {"url": 1, "_id": 0})
        interface_url_list = []
        for item in interface_results:
            interface_url_list.append(item["url"].split(":")[1])
        diff_list = []
        for url in interface_url_list:
            if url not in url_list:
                # print(url.split("/")[4])
                if url.split("/")[4] == date or url.split("/")[3] != "a":
                    # print(url.split("/")[3])
                    diff_list.append(url)
                    print(url)
        print(float(len(set(url_list)&set(interface_url_list)))/len(set(url_list)|set(interface_url_list)))
        # print(float(len(interface_url_list)+len(url_list)-len(diff_list))/(len(interface_url_list)+len(url_list)))

#
# if __name__ == '__main__':
#     start = datetime.strptime("2013-07-01", "%Y-%m-%d")
#     # end = datetime.strptime("2013-07-01", "%Y-%m-%d")
#     # save_domain_date(start=start)
#     # info_check()
#     # print("haha")
#     save_date(start=start)