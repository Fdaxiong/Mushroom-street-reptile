# -*- coding: utf-8 -*-
import time
from pprint import pprint
import re
from copy import deepcopy
import collections
import json
import scrapy


class MushroomSpider(scrapy.Spider):
    name = 'mushroom'
    allowed_domains = ['www.mogu.com', 'list.mogu.com']
    start_urls = ['https://www.mogu.com/']

    def parse(self, response):
        # 拿到每一个主题市场
        theme_bazaar = response.xpath('//div[@class="cate-item-wrap"]/a/h3/text()').extract()
        # 主题url
        theme_bazaar_url = response.xpath('//div[@class="cate-item-wrap"]/a/@href').extract()[1:]
        for i in theme_bazaar:
            item = collections.OrderedDict()
            # 主题市场
            item['theme_bazaar'] = i
            # 主题市场URL
            item['theme_bazaar_url'] = theme_bazaar_url[theme_bazaar.index(i)]
            # 市场详情URL,返回是一个json数据
            bazaar = item['theme_bazaar_url'].split("/")[4]
            bazaar_url = "https://list.mogu.com/sync/menu?&action={}"
            # 抓包获取的市场数据详情url
            item["bazaar_details_url"] = bazaar_url.format(bazaar)
            yield scrapy.Request(
                item['bazaar_details_url'],
                callback=self.bazaar_details,
                meta={"item": deepcopy(item)},
            )

    def bazaar_details(self, response):
        """市场详情"""
        # 等待拼接的详情商品URL
        jios_url = "https://list.mogu.com/search?cKey=15&page=1&fcid={}&action={}"
        # 分割当前URL提取
        bazaar = response.url.split("/")[4]
        item = response.meta["item"]
        response = json.loads(response.text)
        # pprint(response)
        for i in response['data']['cateTree']:
            # 主推荐标题
            item['recommend'] = response['data']['cateTree']["%s" % i]["p"]['title']
            for a in range(len(response['data']['cateTree']["%s" % i]["c"])):
                # 小分类标题
                item['classify_title'] = response['data']['cateTree']["%s" % i]["c"][a]['title']
                # 小分类URL
                item['classify_url'] = "https://list.mogu.com" + response['data']['cateTree']["%s" % i]["c"][a]['link']
                # 小分类 id
                item['classify_fcid'] = response['data']['cateTree']["%s" % i]["c"][a]['fcid']
                # 设置索引后面一一对应
                item["index"] = 1
                # 拼接完整URL
                details_url = jios_url.format(item['classify_fcid'], bazaar)
                yield scrapy.Request(
                    details_url,
                    # url="https://list.mogu.com/book/accessories/20004357?mt=10.854.r29917",
                    # url="https://list.mogu.com/search?cKey=15&page=1&fcid=20004357&action=accessories",
                    callback=self.classify_details,
                    meta={"item": deepcopy(item)},
                    dont_filter=True
                )

    def classify_details(self, response):
        """
        处理商品详情,价格,图片
        规律URL:https://list.mogu.com/search?cKey=15&page=1&fcid=50243&action=clothing
        """
        item = response.meta["item"]
        response_ = json.loads(response.text)
        # pprint(response['result']['wall']['docs'][1]['img'])
        # pprint(response_)
        # 正则表达式匹配标题字段
        title = re.match(r".*title", str(response_))
        if title != None:
            for i in range(len(response_['result']['wall']['docs'])):
                # 商品标题
                item['commodity_title'] = (response_['result']['wall']['docs'][i]['title'])
                # 商品图片URL
                item['commodity_img'] = (response_['result']['wall']['docs'][i]['img'])
                # 商品URL
                item['commodity_link'] = (response_['result']['wall']['docs'][i]['link'])
                # 商品原价
                item['commodity_orgPrice'] = (response_['result']['wall']['docs'][i]['orgPrice'])
                # 商品现价
                item['commodity_price'] = (response_['result']['wall']['docs'][i]['price'])

            # 判断下一页
            next_url = response.url
            item["index"] += 1
            if item["index"] <= 100:
                nul = re.sub(r"&page=(\d+)", "&page=%s" % str(item["index"]), next_url)
                yield scrapy.Request(
                    url=nul,
                    callback=self.classify_details,
                    meta={"item": deepcopy(item)},
                )
            else:
                item["index"] = 1
            yield item
        else:
            # print("%s没有需要数据" % response.url)
            pass
