""" MyMongo """
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
####
import bson
from time import sleep
#####
# $ sudo pip install pymongo
#####
import pymongo
#####
from mylog import MyLog

l = MyLog('MyMongo')

__all__ = ['MyMongo']

class MyMongo(object):
    """ mongodb functions """
    # pylint: disable=bare-except
    # pylint: disable=no-self-use
#    pool = None
#    dbase = None
#    connected = False

    def __init__(self, mongo_hosts, son=True):
        """ constructor """
        self.connected = False
        try:
            if son: self.pool = pymongo.MongoClient(mongo_hosts, document_class=bson.SON)
            else: self.pool = pymongo.MongoClient(mongo_hosts)
#            self.connect()
        except:
            l.log_exception('MyMongo.init: '+mongo_hosts)

    def connect(self, db):
        """ connect to mongodb """
        counter = 0
        while not self.connected and not counter>20:
            self.connected = False
            try:
                self.dbase = self.pool[db]
                self.connected = True
            except:
                l.log_exception('MyMongo.connect')
                sleep(0.2)

    def get(self, mydb, mycol, who, what=None, sort=None, son=False, limit=None):
        """ db.mycol.find(who,what) """
        try:
            self.connect(mydb)
            data = list()
            if (son):
                opts = bson.CodecOptions(document_class=bson.SON)
                col = self.dbase[mycol].with_options(codec_options=opts)
            else:
                col = self.dbase[mycol]
            if what: cursor = col.find(who, what)
            else: cursor = col.find(who)
            if sort:
                srt = []
                for tpl in sort:
                    if tpl[1]==1: srt.append((tpl[0], pymongo.ASCENDING))
                    else: srt.append((tpl[0], pymongo.DESCENDING))
                cursor = cursor.sort(srt)
            if limit: cursor = cursor.limit(limit)

            for doc in cursor:
                data.append(doc)
            return data
        except:
            l.log_exception('MyMongo.get')

    #https://emptysqua.re/blog/pymongo-key-order/
    def getOne(self, mydb, mycol, who, what=None, sort=None, son=False):
        """ db.mycol.findOne(who,what)[key] """
        try:
            self.connect(mydb)
            if (son):
                opts = bson.CodecOptions(document_class=bson.SON)
                col = self.dbase[mycol].with_options(codec_options=opts)
            else:
                col = self.dbase[mycol]
            if sort:
                srt = []
                for tpl in sort:
                    if tpl[1]==1: srt.append((tpl[0], pymongo.ASCENDING))
                    else: srt.append((tpl[0], pymongo.DESCENDING))
            else: srt=[]
            if what: data = col.find_one(who, what, sort=srt)
            else: data = col.find_one(who, sort=srt)
            return data
        except:
            l.log_exception('MyMongo.getOne')

    def command(self, mydb, arg1, arg2=None, **kwargs):
        """ db.command(arg1, arg2=None, **kwargs) """
        try:
            self.connect(mydb)
            if arg2: return self.dbase.command(arg1, arg2, **kwargs)
            else: return self.dbase.command(arg1, **kwargs)
        except:
            pass
            l.log_exception('MyMongo.command')

    def distinct(self, mydb, mycol, key, query=None):
        """ db.mycol.distinct(key) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            if query: return col.distinct(key, query)
            else: return col.distinct(key)
        except:
            l.log_exception('MyMongo.distinct')

    def count(self, mydb, mycol, query={}):
        """ db.mycol.count(query) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            return col.count(query)
        except:
            l.log_exception('MyMongo.count')

    def upsert(self, mydb, mycol, key, data={}):
        """ db.mycol.upsert(key, data) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            res = col.update(key, data, upsert=True)
            return str(res)
        except:
            l.log_exception('MyMongo.upsert')

    def insert_one(self, mydb, mycol, data, writeConcern=True):
        """ db.mycol.insert_one(data, writeConcern) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            res = col.insert_one(data) if writeConcern else col.insert_one(data, {'writeConcern': {'w': 0}})
            return res
        except:
            l.log_exception('MyMongo.insert_one')

    def remove(self, mydb, mycol, key={}):
        """ db.mycol.remove(key) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            res = col.remove(key)
            return str(res)
        except:
            l.log_exception('MyMongo.remove')

    def drop(self, mydb, mycol):
        """ db.mycol.drop() """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            res = col.drop()
            return str(res)
        except:
            l.log_exception('MyMongo.drop')

    def rename(self, mydb, mycol, newname):
        """ db.mycol.rename(newname) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            res = col.rename(newname)
            return str(res)
        except:
            l.log_exception('MyMongo.rename')

    def aggregate(self, mydb, mycol, pipeline, sort=None, limit=None, **kwargs):
        """ db.mycol.aggregate(pipeline) """
        try:
            self.connect(mydb)
            col = self.dbase[mycol]
            if sort: pipeline.append({"$sort": bson.SON(sort)})
            if limit: pipeline.append({"$limit": limit})
            res = list(col.aggregate(pipeline, **kwargs))
            return res
        except:
            l.log_exception('MyMongo.aggregate')
