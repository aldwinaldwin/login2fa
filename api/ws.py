""" api ws """
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
####
from pycnic.core import WSGI, Handler
from pycnic.errors import HTTP_400, HTTP_401
####
from api import Api
from mylog import MyLog
from myconfig import MyConfig
from mysignal import MySignal

api = Api()
c = MyConfig()
l = MyLog(c.cfg['virtualenv']['dir']+'_api_ws')
s = MySignal()

s.set_signalhandler()

class RootRoute(Handler):
    """ / """
    def get(self):
        """ GET / """
        self.response.set_header('Access-Control-Allow-Origin', '*')
        return { 'empty': ' as my mind' }

class UserGetRoute(Handler):
    """ /user/get """
    def post(self):
        """ POST /user/get """
        username = api.UserSession(self.request)
        if not username: raise HTTP_401("I can't let you do that")
        try: data = api.UserGet(username)
        except: l.log_exception('api_ws.UserGet')
        if 'error' in data.keys(): raise HTTP_401(data['error'])
        self.response.set_header('Access-Control-Allow-Origin', '*')
        return data

class UserSetPasswordRoute(Handler):
    """ /user/setpassword """
    def post(self):
        """ POST /user/setpassword """
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        if not username or not password:
            raise HTTP_400('Yo dawg, you need to provide a username and password')
        try: data = api.UserSetPassword(username, password)
        except: l.log_exception('api_ws.UserSetPassword')
        if 'error' in data.keys(): raise HTTP_401(data['error'])
        self.response.set_header('Access-Control-Allow-Origin', '*')
        self.response.set_cookie("session_id", api.UserSetSession(username))
        return data

class UserSetNewPasswordRoute(Handler):
    """ /user/setnewpassword """
    def post(self):
        """ POST /user/setnewpassword """
        username = api.UserSession(self.request)
        if not username: raise HTTP_401("I can't let you do that")
        old_password = self.request.data.get('old_password')
        new_password = self.request.data.get('new_password')
        if not old_password or not new_password:
            raise HTTP_400('Yo dawg, you need to provide a old_password and a new_password')
        try: data = api.UserSetNewPassword(username, old_password, new_password)
        except: l.log_exception('api_ws.UserSetNewPassword')
        if 'error' in data.keys(): raise HTTP_401(data['error'])
        self.response.set_header('Access-Control-Allow-Origin', '*')
        return data

class UserLoginRoute(Handler):
    """ /user/login """
    def post(self):
        """ POST /user/login """
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        code2fa = self.request.data.get('code2fa') if c.cfg['2fa'] else None
        if not username or not password:
            raise HTTP_400('Yo dawg, you need to provide a username and password')
        if c.cfg['2fa'] and not code2fa:
            raise HTTP_400('Yo dawg, you need to provide a code2fa')
        try: data = api.UserLogin(username, password, code2fa)
        except: l.log_exception('api_ws.UserCheckPassword')
        if 'error' in data.keys(): raise HTTP_401(data['error'])
        self.response.set_header('Access-Control-Allow-Origin', '*')
        self.response.set_cookie("session_id", api.UserSetSession(username))
        return data

class UserLogoutRoute(Handler):
    """ /user/logout """
    def post(self):
        """ POST /user/logout """
        username = api.UserSession(self.request)
        if not username: raise HTTP_401("I can't let you do that")
        sessionId = self.request.cookies.get('session_id')
        try: data=api.UserLogout(username, sessionId)
        except: l.log_exception('api_ws.UserLogout')
        self.response.set_header('Access-Control-Allow-Origin', '*')
        return data

class App(WSGI):
    """ pycnic app """
    try:
        routes = [('/', RootRoute()),
                  ('/user/get', UserGetRoute()),
                  ('/user/setpassword', UserSetPasswordRoute()),
                  ('/user/setnewpassword', UserSetNewPasswordRoute()),
                  ('/user/login', UserLoginRoute()),
                  ('/user/logout', UserLogoutRoute()),
                 ]
    except:
        l.log_exception('api_ws.App')
        pass
