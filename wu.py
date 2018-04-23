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
        truepassword = redi.get_user_password(username)
        if password == truepassword:
            self.set_secure_cookie("username", username, expires_days=None)
            self.redirect("/")
        else:
            self.render('error.html')

class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('index.html', user=self.current_user)

class QueryHandler(BaseHandler):
    def get(self):
        self.render("query.html")

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

class luruHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('index.html', user=self.current_user)

    def post(self):
        logid = self.get_argument("logid")
        info = self.get_argument("info")
        #user=self.get_secure_cookie('username')
        #print info,logid,user
        redi.set_logistics_info(logid, info)
        self.render('luru.html', user=self.current_user, info=info)

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
        (r'/luru', luruHandler),
        (r'/logquery', LogqueryHandler),
        (r'/query', QueryHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
