#!/usr/bin/env python
#-*- coding: utf-8 -*- 

import MySQLdb
import time
import string
from DBUtils.PooledDB import PooledDB
import dbconfig
import datetime
import os

DBConfig = dbconfig.Parser()
class DbManager():
    def __init__(self):
        kwargs = {}
        kwargs['host'] =  DBConfig.getConfig('database', 'dbhost')
        kwargs['port'] =  int(DBConfig.getConfig('database', 'dbport'))
        kwargs['user'] =  DBConfig.getConfig('database', 'dbuser')
        kwargs['passwd'] =  DBConfig.getConfig('database', 'dbpassword')
        kwargs['db'] =  DBConfig.getConfig('database', 'dbname')
        kwargs['charset'] =  DBConfig.getConfig('database', 'dbcharset')
        self._pool = PooledDB(MySQLdb, mincached=1, maxcached=15, maxshared=10, maxusage=10000, **kwargs)

    def getConn(self):
        return self._pool.connection()

_dbManager = DbManager()

def getConn():
    return _dbManager.getConn()

def QueryPrograms():
    results = dict()
    con = getConn()
    cur =  con.cursor()

    sql = "select gid from access group by gid"
    cur.execute(sql)
    res = cur.fetchall()
    now  = datetime.datetime.now()
    for item in res:
        results[item[0]] = list()

    results["all"] = list()
    channels = results.keys()
    for channel in channels:
        for x in (7, 6, 5, 4, 3, 2, 1):
            start = now - datetime.timedelta(x, 0, 0)
            end = now - datetime.timedelta(x - 1, 0, 0)
            sstr = start.strftime("%Y-%m-%d 00:00:00")
            endstr = end.strftime("%Y-%m-%d 00:00:00")
            sql = "select count(*) from access where gid = '%s' and time >= '%s' and time < '%s'"%(channel, sstr, endstr)
            cur.execute(sql)
            res = cur.fetchall()
            total = res[0][0]
            results[channel].append(total)

    for channel in channels:
       for x in (0, 1, 2, 3, 4, 5, 6):
           results['all'][x] += results[channel][x]

    cur.close()
    con.close()
    print results
    return results


def DeleteChannel(gid):
    con = getConn()
    cur =  con.cursor()
    sql = "delete from live where gid=%s"%(gid)
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()


if __name__ ==  '__main__':
    QueryPrograms()
