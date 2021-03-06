





## 蘑菇街爬虫

- ### 主题市场

  - 进入https://www.mogu.com

    - 拿到主题的市场的标题和URL链接

    - 查看源码直接提取
    
    - ![](/蘑菇街爬虫/img/1.png)
      
    - ```Python
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
      ```
    
      
    
      

- ### 市场详情
  - ##### 中级分类
    
    - ###### <https://list.mogu.com/book/clothing/50240?acm=3.mce.1_10_1lrea.128038.0.izZN3rtTd5cy5.pos_0-m_507613-sd_119>
    
    - 传入主题URL链接
      
    - 获取四个推荐标题(中级分类)
    
    - 注意!代码走到这里.数据是动态加载(源代码是没有我们需要的数据)
    
    - ![](/蘑菇街爬虫/img/3.png)
    
    - ###### <https://list.mogu.com/sync/menu?callback=jQuery21109356741833187436_1560996011434&action=clothing&_=1560996011435>
    
    - 打开我们通过抓包分析的URL
    
    - ![](/蘑菇街爬虫/img/4.png)
    
    - 打开后是一个没有优化的json数据,下滑找到了我们的中级分类"当季热卖"
    
      ​        因为这个数据是死的,我们要让这个数据跟着我们URL来变动,使一一对应
    
      ​		最后查看我们打开的URL发现是一个get请求,get请求是一个明文的,在URL上显示需要的参数
    
      ​		排除不需要的参数简化URL:<https://list.mogu.com/sync/menu?&action=clothing>
    
      ​		重复上面步骤,对不同主题市场页面进行抓包,发现action的参数是变化的
    
      ​		这个参数我们其实在前面见过,不知道你有没有细心发现,在传入市场详情的URL里面有这个参数
    
      ​		我们同过分割URL提取我们一一对应的action参数
    
    - ```python
          # 市场详情URL,返回是一个json数据
          bazaar = item['theme_bazaar_url'].split("/")[4]
          bazaar_url = "https://list.mogu.com/sync/menu?&action={}"
          # 抓包获取的市场数据详情url
           item["bazaar_details_url"] = bazaar_url.format(bazaar)
      ```
    
      ​		
  
  ----
  
  
  
  - ##### 小分类
    - classify_details()
    
    - 传入分类URL链接
  
    - 这个函数是提取所有分类
    
      ​	转换json数据,循环一一对应提取
    
      ````python
      response = json.loads(response.text)
      # pprint(response)
      for i in response['data']['cateTree']:
      # 主推荐标题(中级分类)
          item['recommend'] = response['data']['cateTree']["%s" % i]["p"]['title']
          for a in range(len(response['data']['cateTree']["%s" % i]["c"])):
              # 小分类标题
              item['classify_title'] = response['data']['cateTree']["%s" % i]["c"][a]['title']
              # 小分类URL
              item['classify_url'] = "https://list.mogu.com" + response['data']['cateTree']["%s" % i]["c"][a]['link']
              # 小分类 id
              item['classify_fcid'] = response['data']['cateTree']["%s" % i]["c"][a]['fcid']
      ````
    
      
    
  
- ### 商品详情
  - commodity_details()
  
  - 传入小分类的商品URL链接  
  
  - 商品详情也是动态加载出来的

  - 我们接着抓包,直接搜索商品名字看看能不能找到商品的相关信息
  
  - ![](/蘑菇街爬虫/img/6.png)
  
    ​	这种情况我们只能一个一个数据包找了.数据包是非常多的,动态加载出来的一般在XHR和JS里面我们只需要在`	这两个选项里面找就基本上可以找到,同时可以减少我们的工作负担
  
  - ![](C:\Users\88487\Desktop\蘑菇街爬虫\img\7.png)
  
  - 打开我们抓包到的URL链接 <https://list.mogu.com/search?callback=jQuery21107305972596121317_1561013397166&_version=8193&ratio=3%3A4&cKey=15&page=1&sort=pop&ad=0&fcid=50243&action=clothing&mt=10.848.r29125&ptp=31.TjHLnb._cate.4.jtgAlgwM&_=1561013397167>
  
    
  
  - ![](/蘑菇街爬虫/img/8.png)
  
  - 分析简化URL,<https://list.mogu.com/search?&cKey=15&page=1&fcid=50243&action=clothing>
  
    - 这几个是关键参数 ckey,page,fcid action
    - 除了ckey是不变化的,其他都是变化的
    - page对应的页数
    - fcid对应的是小分类ID
    - action对应的是主题市场
  
  - 知道了URL规律我们就可以进行拼接了
  
  - ```python
      # 等待拼接的详情商品URL
      jios_url = "https://list.mogu.com/search?cKey=15&page=1&fcid={}&action={}"
      # 拼接完整URL
      details_url = jios_url.format(item['classify_fcid'], bazaar)
    ```
  
  - 提取数据
  
    - 商品链接
  
    - 商品价格
  
    - 商品原价
  
    - ````Python
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
      ````
  
- 处理错误
  
  - 在这里我写完所有代码遇见一个错误,就是有一些页面是没有商品的  比如配饰的服饰配饰中的帽子或棒球帽
  
    	###### <https://list.mogu.com/book/accessories/20003726?mt=10.854.r29917&ptp=31.aaKPHb._cate.15.Kb2Do1a0#sp_topbanner>
  
  - 拼接起来的URL,也是有数据的,但不是我们想要的数据会导致上面的提取字段出错误
  
  		 ###### https://list.mogu.com/search?&cKey=15&page=1&fcid=20003726&action=accessories
  	
  - ![](/蘑菇街爬虫/img/9.png)
  
  - 这个错误用正则表达式进行查找就好了,查找某一个字段,有这个字段我就进行提取,没有则不进行提取,同时pass通过,进行下一个URL链接提取
  
  - ````Python
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
              else:
                  # print("%s没有需要数据" % response.url)
                  pass
      ````
  
      
  
    
  
  ### 翻页详情
  
  - 在这里我们爬虫就快写完了,上面分析URL有一个参数page是页数
  
  - 所有我们只有找到每一页的的规律就可以进行翻页了
  
  - 我们可以先使用这个方法,我不管它有多少页,直接判断一个页面有多少个商品,小于这个商品数量是不是就意外着已经到了最后一页.很显然一页加载出来的商品还是比较多的,其实在抓包的时候可以很直观的看到给了我们多少商品
  
  - ![](/蘑菇街爬虫/img/11.png)
  
  - 找不到每一页固定的商品个数这种方法是行不通的,哪我们尝试下面这种方法
  
  - 我可以先尝试输入一个最大页数,如果有数据就会显示,没有就不会显示
  
  - ![](/蘑菇街爬虫/img/10.png)
  
  - 仿佛我们输入无论多少页服务器都会给我数据,数据更像是前面随机给我的
  
  - 后面通过重复输入不同的页数找出规律,只要超出了的服务器加载的页数,无论你数多少页,都从前面的页数随机给一页数据给我们
  
  - 最后仿佛要绝望,我还是不相信它能一直加载数据给我们,
  
    ​	因为是动态ajxj加载数据的,滚轮下滑到一定的位置就会加载一页商品给我们
  
    ![](/蘑菇街爬虫/img/12.png)
  
    
  
  - 最后同过模拟请求发现只加载100页就停下来了
  
  - 所以我们每一个小分类加载page到100页就可以了
  
  - 后面遇到一个问题,因为scrapy是异步加载的,会导致一个URL还没有到100页,另一个URL就加载到了100,会导致if判断出错
  
  - 所以在这里我们个每一个小分类添加索引 index.让index索引从一开始,一旦满足条件就页数加1重新把URL交给classify_details函数重新提取商品信息,每一个各自的小分类索引到了100才结束各自的循环,同时初始化index
  
  - 在这里我们要知道每次传过来的URL,同时替换新的页数拼接起URL,传给classify_details自己
  
  - ````Python
    
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
    ````
  
  - 到了这里我们的所有信息已经提取完成了,每一个商品对应每一个字典
  
  

- ### 保存数据写入Excel

  - def sava_data(self, item):

  - 我们使用 openpyxl 库写入Excel

  - 设置好我们的表头

  - ```Python
     ws["A1"] = "大分类"
            ws["B1"] = "中级分类"
            ws["C1"] = "小分类"
            ws["D1"] = "商品标题"
            ws["E1"] = "价格"
            ws["F1"] = "原价"
            ws["G1"] = "小分类链接"
            ws["H1"] = "商品图片链接"
            ws["I1"] = "商品链接"
    ```

  - 写入我们的数据

  - ```Python
      ws.append(
                [
                    item["theme_bazaar"],
                    item["recommend"],
                    item["classify_title"],
                    item["commodity_title"],
                    item["commodity_price"],
                    item["commodity_orgPrice"],
                    item["classify_url"],
                    item["commodity_img"],
                    item["commodity_link"],
      
                ]
    ```

  - 最后保存Excel

  - ```Python
     wb.save("蘑菇街_再也不修改版.xlsx")
    ```







____

---

  ### 完整代码

##### mushroom.py

```Python
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

```

##### pipelines.py

````Python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from pprint import pprint
import pandas as pd
from openpyxl import Workbook

wb = Workbook()
ws = wb.active


class MogujiePipeline(object):
    def process_item(self, item, spider):
        # 保存数据excel
        self.sava_data(item)
        # pprint(item)
        return item

    def sava_data(self, item):
        """
        保存数据函数写入Excel
        """
       
        ws["A1"] = "大分类"
        ws["B1"] = "中级分类"
        ws["C1"] = "小分类"
        ws["D1"] = "商品标题"
        ws["E1"] = "价格"
        ws["F1"] = "原价"
        ws["G1"] = "小分类链接"
        ws["H1"] = "商品图片链接"
        ws["I1"] = "商品链接"

        ws.append(
            [

                item["theme_bazaar"],
                item["recommend"],
                item["classify_title"],
                item["commodity_title"],
                item["commodity_price"],
                item["commodity_orgPrice"],
                item["classify_url"],
                item["commodity_img"],
                item["commodity_link"],

            ]
        )
        pprint(item)
        wb.save("蘑菇街_再也不修改版.xlsx")

````





### Excel数据可视化透视图



![](/蘑菇街爬虫/img/数据表.png)

![](/蘑菇街爬虫/img/透视图.png)
