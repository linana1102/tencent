# -*- coding: utf-8 -*-
import pymongo
import redis
import copy

# execute mode(testing / dev / prod)
MODE = 'dev'

# define different executing mode database connection
if MODE == 'prod':
    host = '172.18.21.117'
    port = 27017
    database = 'news'
    rds_host = '172.18.21.197'
    rds_port = 6379
elif MODE == 'dev':
    host = '172.18.19.219'
    port = 27017
    database = 'news'
    rds_host = '172.18.19.218'
    rds_port = 6379
elif MODE == 'testing':
    host = '172.18.19.101'
    port = 27017
    database = 'news'
    rds_host = '172.18.19.101'
    rds_port = 6379
else:
    host = '127.0.0.1'
    port = 27017
    database = 'news'
    rds_host = '127.0.0.1'
    rds_port = 6379

BASE_CONFIG = {'host': host,
               'port': port,
               'db': database}

ARTICLE_CONFIG = copy.deepcopy(BASE_CONFIG)
ARTICLE_CONFIG['collection'] = 'article'

TEST_CONFIG = copy.deepcopy(BASE_CONFIG)
TEST_CONFIG['collection'] = 'test'

TIEBA_OVER_VIEW_CONFIG = copy.deepcopy(BASE_CONFIG)
TIEBA_OVER_VIEW_CONFIG['collection'] = 'tieba_over_view'

TIEBA_POST_CONFIG = copy.deepcopy(BASE_CONFIG)
TIEBA_POST_CONFIG['collection'] = 'tieba_post'

TIEBA_FLOOR_CONFIG = copy.deepcopy(BASE_CONFIG)
TIEBA_FLOOR_CONFIG['collection'] = 'tieba_floor'

TIEBA_COMMENT_CONFIG = copy.deepcopy(BASE_CONFIG)
TIEBA_COMMENT_CONFIG['collection'] = 'tieba_comment'

DB_CONFIG = {
    'base': BASE_CONFIG,
    'article': ARTICLE_CONFIG,
    'test': TEST_CONFIG,
    'tieba_over_view': TIEBA_OVER_VIEW_CONFIG,
    'tieba_post': TIEBA_POST_CONFIG,
    'tieba_floor': TIEBA_FLOOR_CONFIG,
    'tieba_comment': TIEBA_COMMENT_CONFIG,
}

REDIS_CONFIG = {
    'host' : rds_host,
    'port' : rds_port
}

class RedisWrapper(object):
    """
    Redis连接类
    """
    shared_state = {}
    def __init__(self):
        self.__dict__ = self.shared_state

    def redis_connect(self):
        connection_pool = redis.ConnectionPool(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'])
        return redis.StrictRedis(connection_pool=connection_pool)

redis_conn = RedisWrapper().redis_connect()

class MongodbConnection(object):
    """
    MongoDB连接类
    """
    def __init__(self, flag=0):
        self.conn = None
        self.set_db_conn()

    def set_db_conn(self):
        mongo_config=DB_CONFIG["base"]
        client = pymongo.MongoClient(mongo_config['host'], mongo_config['port'], connect=False)
        self.conn = client[mongo_config['db']]

    def get_db_conn(self):
        db = self.conn
        return db

db_conn = MongodbConnection().get_db_conn()
db = {
    'article': db_conn[DB_CONFIG["article"]["collection"]],
    'test': db_conn[DB_CONFIG["test"]["collection"]],
    'tieba_over_view': db_conn[DB_CONFIG["tieba_over_view"]["collection"]],
    'tieba_post': db_conn[DB_CONFIG["tieba_post"]["collection"]],
    'tieba_floor': db_conn[DB_CONFIG["tieba_floor"]["collection"]],
    'tieba_comment': db_conn[DB_CONFIG["tieba_comment"]["collection"]],
}
