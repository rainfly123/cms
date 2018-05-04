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
        kwargs['db'] =  'chart'
        kwargs['charset'] =  DBConfig.getConfig('database', 'dbcharset')
        self._pool = PooledDB(MySQLdb, mincached=1, maxcached=15, maxshared=10, maxusage=10000, **kwargs)

    def getConn(self):
        return self._pool.connection()

_dbManager = DbManager()

def getConn():
    return _dbManager.getConn()

def QueryPrograms(gid):
    results = list()
    i = 0
    con = getConn()
    cur =  con.cursor()

    sql = "select program_name, time, url, class, subclass, flag, id from vod where gid = '{0}' and url != '' ".format(gid)
    cur.execute(sql)
    res = cur.fetchall()
    now = datetime.datetime.now()

    for item in res:
        program = dict()
        program['id'] = i
        program['program_name'] = item[0]
        program['time'] = item[1].strftime("%Y-%m-%d %H:%M")
        basename = os.path.splitext(item[2])[0]
        program['url'] = basename + ".jpg"
        program['class'] = item[3]
        program['subclass'] = item[4]
        program['flag'] = item[5]
        program['pid'] = item[6]
        program['gid'] = gid
        results.append(program)
        i += 1

    cur.close()
    con.close()
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
