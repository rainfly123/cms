#!/usr/bin/env python
#-*- coding: utf-8 -*- 
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpclient
import tornado.gen
import os.path
import json
import redi
import mysql

from tornado.options import define, options
define("port", default=1111, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        #truepassword = redi.get_user_password(username)
        truepassword = password
        if password == truepassword:
            self.set_secure_cookie("username", username, expires_days=None)
            self.redirect("/")
        else:
            self.render('error.html')

class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        chan = mysql.QueryLiveChannels()
        self.render("live.html", channels = chan)

class pvrHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        gid = self.get_argument("gid")
        if gid is None:
            gid = "cctv1"
        chan = mysql.QueryLiveChannels()
        prog = mysql.QueryPrograms(gid)
        self.render("pvr.html", channels = chan, programs = prog)

class liveHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        gid = self.get_argument("gid")
        if gid is None:
            gid = "cctv1"
        chan = mysql.QueryLiveChannels(gid)
        self.render("live.html", channels = chan)


newurl = "http://logistics.chinadnhh.com/kdapi/kdapi.php?wuliuid="
class LogqueryHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            logid = self.get_argument("logid")
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield client.fetch(newurl + logid, method='GET')
            data= response.body
            data = data.replace("true", "True")
            data = eval(data)
            result = []
            for x in data['Traces']:
                temp = x['AcceptTime'] + " " + x['AcceptStation']
                result.append(temp)
            if len(result) > 0 :
                ret  = {"code":0, "msg":"成功", "data":result}
            else:
                ret  = {"code":1, "msg":"暂无物流踪迹", "data":[]}
        except Exception,e:
                print e
                ret  = {"code":2, "msg":"服务器异常", "data":[]}
       
        self.write(json.dumps(ret))

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.redirect("/login")

class subclassHandler(BaseHandler):
    def get(self):
        val = self.get_argument("class")
        r = mysql.QuerysubClass(int(val))
        self.write(json.dumps({"code":0, "msg":"ok", "data":r}))


class uploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        classname = mysql.QueryClass()
        self.render('upload.html', user=self.current_user, classname = classname)

    def post(self):
        title = self.get_argument("title")
        tag = self.get_argument("tag")
        self.render('query.html')

class peditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pid = self.get_argument("pid")
        classname = mysql.QueryClass()
        prog = mysql.QueryProgramPID(pid)
        self.render('pedit.html', classname = classname, program = prog)

    def post(self):
        title = self.get_argument("title")
        flag = self.get_argument("flag")
        clas = self.get_argument("class")
        subclas = self.get_argument("subclass")
        gid = self.get_argument("gid")
        pid = self.get_argument("pid")
        mysql.UpdateProgram(pid, gid, subclas,clas, flag,title)
        self.redirect("/pvr?gid=%s"%gid)

class pdeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pid = self.get_argument("pid")
        gid = self.get_argument("gid")
        prog = mysql.DelProgram(pid)
        self.redirect("/pvr?gid=%s"%gid)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
         "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "chinaflower",
        "xsrf_cookies": False,
        "login_url": "/login"
    }

    application = tornado.web.Application([
        (r'/', WelcomeHandler),
        (r'/upload', uploadHandler),
        (r'/pedit', peditHandler),
        (r'/pdelete', pdeleteHandler),
        (r'/logquery', LogqueryHandler),
        (r'/pvr', pvrHandler),
        (r'/subclass', subclassHandler),
        (r'/live', liveHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
