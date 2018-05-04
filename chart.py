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
    which = 7
    now  = datetime.datetime.now()
    for item in res:
        print item[0]
        results[item[0]] = list()
    for x in range(7):
        start = now - datetime.timedelta(which, 0, 0)
        end = now - datetime.timedelta(which - 1, 0, 0)
        which -= 1
        print start.strftime("%Y-%m-%d 00:00:00")
        print end.strftime("%Y-%m-%d 00:00:00")

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
