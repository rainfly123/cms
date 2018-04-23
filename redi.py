#!/usr/bin/env python
#-*- coding: utf-8 -*- 
import redis  
import json
import time
import random

pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0, password="")  
r = redis.Redis(connection_pool=pool)  

def get_user_password(username):

    if username is None:
        return None

    return r.get("u_" + username)

def set_video_title(vid, title):

    return r.hset("v_" + vid, "title", title)

def set_video_duration(vid, duration):

    return r.hset("v_" + vid, "duration", duration)

def set_video_snap(vid, snap):

    return r.hset("v_" + vid, "snap", snap)

def set_video_playurl(vid, playurl):

    return r.hset("v_" + vid, "playurl", playurl)

def get_video_title(vid):

    return r.hget("v_" + vid, "title")

def get_video_duration(vid):

    return r.hget("v_" + vid, "duration")

def get_video_snap(vid):

    return r.hget("v_" + vid, "snap")

def get_video_playurl(vid):

    return r.hget("v_" + vid, "playurl")

def gen_videoid():

    uuid = r.incr("globalid")
    uuid = str(uuid)
    r.rpush("videos", "v_" + uuid)
    return uuid


if __name__ == "__main__":
    uuid = gen_videoid()
    set_video_playurl(uuid, "www")
    print get_video_playurl(uuid)
