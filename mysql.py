#!/usr/bin/env python
#-*- coding: utf-8 -*- 

import MySQLdb
import time
import string
from DBUtils.PooledDB import PooledDB
import dbconfig
import datetime


ERROR = {0:"OK", 1:"Parameter Error", 2:"Database Error", 3:u"您已赞", 4:u"你无权开通直播"}
Default_Snapshot = "http://7xvsyw.com2.z0.glb.qiniucdn.com/n.jpg"

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

def QueryEPG():
    channels = list()
    results= dict()
    
    con = getConn()
    cur =  con.cursor()
    sql = "select gid from live where enable_vod = 1"
    cur.execute(sql)
    res = cur.fetchall()
    for channel in res:
        channels.append(channel[0])

    for channel in channels:
        programs = list()
        sql = "select id, time, store_path from vod where gid = '{0}' and url is NULL order by time ".format(channel)
        cur.execute(sql)
        res = cur.fetchall()
        for r in res:
            program = dict()
            program['mysqlid'] = r[0]
            program['time'] = r[1]
            program['store_path'] = r[2]
            program['gid'] =  channel
            programs.append(program)

        results[channel] = programs

    cur.close()
    con.close()
    return results

def QueryPrograms(gid):
    results = list()
    i = 0
    con = getConn()
    cur =  con.cursor()

    sql = "select program_name, time, url, class, subclass, flag from vod where gid = '{0}' and url != '' ".format(gid)
    cur.execute(sql)
    res = cur.fetchall()
    now = datetime.datetime.now()

    for item in res:
        program = dict()
        program['id'] = i
        program['program_name'] = item[0]
        program['time'] = item[1].strftime("%Y-%m-%d %H:%M")
        program['url'] = item[2]
        program['class'] = item[3]
        program['subclass'] = item[4]
        program['flag'] = item[5]
        results.append(program)
        i += 1

    for item in results:
        sql = "select class.name, subclass.name from class, subclass where class.class =%d and class.class=subclass.class and\
            subclass.class=%d"%(item['class'],item['subclass'])
        cur.execute(sql)
        res = cur.fetchall()
        for ite in res:
            item['class'] = ite[0]
            item['subclass'] = ite[1]

    cur.close()
    con.close()
    return results

def QueryLiveChannels(gid=None):
    results = list()
    i = 0
    con = getConn()
    cur =  con.cursor()

    if gid is None:
        sql = "select gid, name, url, enable_vod, logo from live"
    else:
        sql = "select gid, name, url, enable_vod, logo from live where gid='%s'"%(gid)
    cur.execute(sql)
    res = cur.fetchall()
    now = datetime.datetime.now()

    for item in res:
        program = dict()
        program['id'] = i
        program['gid'] = item[0]
        program['name'] = item[1]
        program['url'] = item[2]
        program['enable_vod'] =  item[3]
        program['logo'] =  item[4]
        results.append(program)
        i+=1
    cur.close()
    con.close()
    return results



if __name__ ==  '__main__':
    print QueryEPG()
    print QueryPrograms("cctv1")
    print QueryLiveChannels()
    print QueryLiveChannels("cctv1")
