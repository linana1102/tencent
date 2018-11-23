# -*- coding: utf-8 -*-

from news.middlewares.resource import PROXIES, PORT
import random


class RandomProxy(object):
    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        request.meta['proxy'] = 'http://{}:{}'.format(proxy, PORT)
