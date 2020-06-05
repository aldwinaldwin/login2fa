""" MyConfig """
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
####
import yaml
####
try:
    import mylog
except:
    from framework import mylog

l = mylog.MyLog('MyConfig')

__all__ = ['MyConfig']

class MyConfig(object):
    """ config """
    #cfgFile='config.conf'
    cfg = None

    def __init__(self, cfgFile='config.conf'):
        """ constructor """
        try:
            self.cfgFile = cfgFile
            stream = open(self.cfgFile, 'r')
            self.cfg = yaml.load(stream, Loader=yaml.FullLoader) #yaml.SafeLoader
        except:
             l.log_exception('MyConfig.init')

    def save(self, cfgFile='config.conf'):
        """ save """
        try:
            if len(self.cfg)>0:
                with open(cfgFile, 'w') as outfile:
                    yaml.dump(self.cfg, outfile, default_flow_style=False)
                    outfile.close()
            else:
                open(cfgFile, 'w').close()
        except:
            l.log_exception('MyConfig.save')
