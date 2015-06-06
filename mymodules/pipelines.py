from scrapy import signals
from scrapy.exceptions import DropItem
import os

from pybloomfilter import BloomFilter
from mymodules.searchIndex import SearchIndex
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from gi.overrides.Gdk import Cursor
import traceback

class FilterWordsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = ['politics', 'religion']
    

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            if word in unicode(item['description']).lower():
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item

class DuplicatesPipeline(object):
    

    def __init__(self):
        self.bf = BloomFilter(10000000, 0.01, 'filter.bloom')
        self.f_write = open('visitedsites','w')
        self.si = SearchIndex()
        self.si.SearchInit()
        self.count_num = 0
        self.db = MySQLdb.connect("localhost","root","","storecount")
        self.cursor = self.db.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS POPULAR")
        sql1 = """CREATE TABLE POPULAR(URL text(512),COUNT_MARK INT);"""
    
        try:
            self.cursor.execute(sql1)
            self.db.commit()
#             print "cao create"
        except:
            traceback.print_exc()
            self.db.rollback()
#         self.dbpool = adbapi.ConnectionPool('MySQLdb',
#                                             host = '127.0.0.1',
#                                             db = 'storecount',
#                                             user = 'root',
#                                             passwd = '',
#                                             cursorclass = MySQLdb.cursors.DictCursor,
#                                             charset = 'utf8',
#                                             use_unicode = True)
        self.mark = 0
        
        
#     def _conditional_insert(self,tx,item):
#         sql = 'insert into popular values (%s, %d)'
#         tx.execute(sql, (item['url'],self.mark))

    def process_item(self, item, spider):
#         print '************%d pages visited!*****************' %len(self.bf)
        if self.bf.add(item['url']):#True if item in the BF
            sql2 = "UPDATE POPULAR SET COUNT_MARK = COUNT_MARK + 1 WHERE URL = '%s'" %item['url']
            try:
                print "update"
                self.cursor.execute(sql2)
                self.db.commit()
            except:
                traceback.print_exc()
                self.db.rollback()
#             self.dbpool.runOperation("UPDATE popular SET mark+1")
            
            raise DropItem("Duplicate item found: %s" % item)
            
            
        else:
            #print '%d pages visited!'% len(self.url_seen)
            self.count_num += 1
            self.save_to_file(item['url'],item['title'])
            self.si.AddIndex(item)
            sql3 = """INSERT INTO POPULAR(URL,COUNT_MARK) VALUES ("%s",0);""" % item['url']
            try:
                self.cursor.execute(sql3)
                self.db.commit()
                
            except:
                traceback.print_exc()
                self.db.rollback()
#             self._conditional_insert(self,self.dbpool, item['url'], 0)
            
#             print self.count_num
            if self.count_num >=100000 and self.count_num % 10000 :
                print self.count_num
            return item
        

    def save_to_file(self,url,utitle):
        self.f_write.write(url)
        self.f_write.write('\t')
        self.f_write.write(utitle.encode('utf-8'))
        self.f_write.write('\n')

    def __del__(self):
        """docstring for __del__"""
        self.f_write.close()
        self.si.IndexDone()
