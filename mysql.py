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

def UpdatePVRUrl(mysqlid, url):
    con = getConn()
    cur =  con.cursor()

    sql = "update vod set url = '{0}' where id = '{1}' ".format(url, mysqlid)
    cur.execute(sql)
    con.commit()

    cur.close()
    con.close()

def DeletePVRUrl(mysqlid):
    con = getConn()
    cur =  con.cursor()

    sql = "delete from vod where id = '{0}' ".format(mysqlid)
    cur.execute(sql)
    con.commit()

    cur.close()
    con.close()

def QueryPrograms(gid):
    results = list()
    con = getConn()
    cur =  con.cursor()

    sql = "select time, program_name, url from vod where gid = '{0}' ".format(gid)
    cur.execute(sql)
    res = cur.fetchall()
    now = datetime.datetime.now()

    for item in res:
        program = dict()
        program['time'] = item[0].strftime("%Y-%m-%d %H:%M")
        program['program_name'] = item[1]
        program['url'] = item[2]
        program['type'] = 0 #vod
        if item[2] is None:
            if item[0] > now:
                program['type'] = 2 #reserve
            else:
                program['type'] = 1  #live
        results.append(program)
    cur.close()
    con.close()
    return results

def QueryLiveChannels():
    results = list()
    con = getConn()
    cur =  con.cursor()

    sql = "select gid, name, url, enable_vod, logo from live"
    cur.execute(sql)
    res = cur.fetchall()
    now = datetime.datetime.now()

    for item in res:
        program = dict()
        program['gid'] = item[0]
        program['name'] = item[1]
        program['url'] = item[2]
        program['enable_vod'] =  item[3]
        program['logo'] =  item[4]

        results.append(program)
    cur.close()
    con.close()
    return results



if __name__ ==  '__main__':
    print QueryEPG()
    print QueryPrograms("cctv1")
    print QueryLiveChannels()
