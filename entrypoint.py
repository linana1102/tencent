from scrapy.cmdline import execute
import time

# execute(['scrapy', 'crawl', 'tieba'])
# execute(['scrapy', 'crawl', 'tencent_content'])
# execute(['scrapy', 'crawl', 'tencent_news'])
# start = time.time()
# execute(['scrapy', 'crawl', 'test'])
execute(['scrapy', 'crawl', 'tencent_contents'])
# print(int(time.time()-start))



