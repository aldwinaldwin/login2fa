""" api """
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
####
from password_strength import PasswordPolicy
import pyotp
####
from mymongo import MyMongo
from mylog import MyLog
from myconfig import MyConfig

# pylint: disable=fixme

c = MyConfig()
l = MyLog(c.cfg['virtualenv']['dir']+'_api')

appname = c.cfg['virtualenv']['dir']

mongohost = c.cfg['dbs']['mongo']['host']
mongodb = c.cfg['dbs']['mongo']['db']
sessionHashSecret = c.cfg['session']['hash_secret']

passpolicylength = c.cfg['password_strength']['length']
passpolicyuppercase = c.cfg['password_strength']['uppercase']
passpolicynumbers = c.cfg['password_strength']['numbers']
passpolicyspecial = c.cfg['password_strength']['special']
passpolicy = PasswordPolicy.from_names(
    length = passpolicylength,          # min length
    uppercase = passpolicyuppercase,    # need min. uppercase letters
    numbers = passpolicynumbers,        # need min. digits
    special = passpolicyspecial,        # need min. special characters
)

use2fa = c.cfg['2fa']

class Api:
    """ api functions """

    def __init__(self):
        self.mongo = MyMongo(mongohost)

    """ user functions """

    def password(self, password, hashed=None):
        try:
            import hashlib, os
            salt = os.urandom(32) if not hashed else hashed[:32]
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
            return salt+key if not hashed else (key==hashed[32:])
        except:
            l.log_exception('api.password')

    def testpassword(self, password):
        res = passpolicy.test(password)
        if res:
            error = 'Password needs minimun lenght of '+str(passpolicylength)+' characters'
            if passpolicyuppercase: error += ', minimum '+str(passpolicyuppercase)+' uppercase characters'
            if passpolicynumbers: error+= ', minimum '+str(passpolicynumbers)+' digits'
            if passpolicyspecial: error+= 'minimum '+str(passpolicyspecial)+' special characters'
            return error
        return None

    def UserGet(self, username):
        data2return = {'data': list()}
        try:
            who = {'username': username}
            what = { '_id':0, 'password': 0}
            data = self.mongo.get(mongodb, 'users', who, what)
            for doc in data:
                data2return['data'].append(doc)
            if not data2return['data']: data2return['error'] = 'username not found'
        except:
            l.log_exception('api.UserGet')
        return data2return

    def UserSession(self, request):
        try:
            sessionId = request.cookies.get('session_id')
            if not sessionId: return None
            who = {'session_id': sessionId}
            what =  { '_id':0, 'username': 1}
            data = self.mongo.getOne(mongodb, 'user_sessions', who, what)
            if not data or not data.get('username'): return None
        except:
            l.log_exception('api.UserSession')
        return data['username']

    def UserSetSession(self, username):
        import hashlib, time, datetime
        try:
            to_hash = '%s_'%(time.time())+sessionHashSecret
            sessionId = hashlib.sha1(to_hash.encode('utf-8')).hexdigest()
            who = {'username': username, 'session_id': sessionId, 'ttl': datetime.datetime.now()}
            self.mongo.insert_one(mongodb, 'user_sessions', who)
        except:
            l.log_exception('api.UserSetSession')
        return sessionId

    def UserLogout(self, username, sessionId):
        try:
            who = {'username': username, 'session_id': sessionId}
            self.mongo.remove(mongodb, 'user_sessions', who)
        except:
            l.log_exception('api.UserLogout')
        return {'ok': 'done'}

    def UserSetPassword(self, username, password):
        data2return = {'ok': 'done'}
        try:
            passwordFail = self.testpassword(password)
            if passwordFail: return {'error': passwordFail}
            who = {'username': username}
            what = { '_id':0, 'password': 1, 'username': 1}
            data = self.mongo.getOne(mongodb, 'users', who, what)
            if not data: return {'error': 'Invalid username'}
            if data.get('password'): return {'error': 'Password already set'}
            data = {'$set': {'password': self.password(password) } }
            if use2fa:
                data['$set']['secret2fa'] = pyotp.random_base32()
                data2return['uri_2fa'] = pyotp.totp.TOTP(data['$set']['secret2fa']).provisioning_uri(username, issuer_name=appname)
            self.mongo.upsert(mongodb, 'users', who, data)
        except:
            l.log_exception('api.UserSetPassword')
        return data2return

    def UserSetNewPassword(self, username, old_password, new_password):
        try:
            who = {'username': username}
            what = { '_id':0, 'password': 1}
            data = self.mongo.getOne(mongodb, 'users', who, what)
            if not data: return {'error': 'Invalid username'}
            if not data.get('password'): return {'error': 'Password not set'}
            if not self.password(old_password, data['password']): return {'error': 'Wrong old password'}
            data = {'$set': {'password': self.password(new_password) } }
            self.mongo.upsert(mongodb, 'users', who, data)
            return {'ok': 'done'}
        except:
            l.log_exception('api.UserSetNewPassword')

    def UserLogin(self, username, password, code2fa=None):
        try:
            who = {'username': username}
            what = { '_id':0, 'password': 1}
            if use2fa: what['secret2fa'] = 1
            data = self.mongo.getOne(mongodb, 'users', who, what)
            if not data or not data.get('password') or \
               not self.password(password, data['password']):
                    return {'error': 'Passwordcheck failed'}
            if use2fa and not pyotp.TOTP(data.get('secret2fa')).now()==code2fa:
                return {'error': 'Passwordcheck failed'}
            return {'ok': 'Passwordcheck passed'}
        except:
            l.log_exception('api.UserCheckPassword')
