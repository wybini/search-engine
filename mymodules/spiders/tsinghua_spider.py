#!/usr/bin/env python
#-*- coding:utf-8 -*-
#from urlparse import urljoin
from scrapy.utils.url import urljoin_rfc
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import HtmlResponse 

from scrapy.exceptions import DropItem

from mymodules.items import Website

import urllib
import re

class Tsinghua_Spider(BaseSpider):
    name = "tsinghua_spider"
    start_urls = [
#         "http://www.tsinghua.edu.cn",
#         "http://info.tsinghua.edu.cn"
        "http://www.csdn.net"
        
       
    ]
    
    def __init__(self):
        """init the allowed_domain"""
        self.allowed_domains = ['tsinghua.edu.cn']
       

    def parse(self, response):
        """In this parse,we use double yeild to return the item or Request"""
        if not isinstance(response, HtmlResponse):
            return
        hxs = HtmlXPathSelector(response)
#         print hxs

        refer_websites = hxs.select('//@href').extract()
         
        #if not self.gethostname(response.url) in self.allowed_domains:
        #    self.allowed_domains.append(self.gethostname(response.url))

        item = Website()
        item['url'] = response.url
#         item['title'] = hxs.select('/html/head/title/text()').extract()
#         print item['title']
        dic = hxs.select('/html/head/title/text()').extract()
        item['title'] = 'null'
        if dic is not None and len(dic) is not 0:
#             print hxs.select('/html/head/title/text()').extract()
            item['title'] = hxs.select('/html/head/title/text()').extract()[0]
        
        """FIXME:This XPath select all the elements,include the javascript code.BAD!!!"""
        str = ''
        list = hxs.select('/html/body//*/text()').extract()
        for s in list:
            str += s.strip()
            str += ' '

        item['content'] = str

        yield item

        for weburl in refer_websites:
            
            utf8_url = weburl.encode('utf-8')
            
            """The following regex to match the prefix and postfix of urls"""
            postfix = re.compile(r'.+\.((jpg)|(ico)|(rar)|(zip)|(doc)|(ppt)|(xls)|(css)|(exe)|(pdf))x?$')
            prefix = re.compile(r'^((javascript:)|(openapi)).+')

            if postfix.match(utf8_url):
                continue
            if prefix.match(utf8_url):
                continue
            if not utf8_url.startswith('http://'):
                #weburl = urljoin_rfc(response.url, weburl, response.encoding)
                weburl = 'http://'+self.gethostname(response.url)+'/'+weburl
            
            weburl = re.sub(r'/\.\./\.\./',r'/',weburl)
            weburl = re.sub(r'/\.\./',r'/',weburl)

            yield Request(weburl, callback=self.parse)
                
    def gethostname(self, res_url):
        """get the host name of a url"""
        proto, rest = urllib.splittype(res_url)
        host, rest = urllib.splithost(rest)
        return host
