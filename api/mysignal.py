""" mysignal """
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
####
import signal
####
from mylog import MyLog

l = MyLog('MySignal')


__all__ = ['MySignal']

class MySignal(object):

    def __init__(self):
        """ constructor """
        self.exitFlag = 0

    def signalhandler(self, signum, stack):
        """ handle ctrl-c signal """
        l.log('Exiting gracefully! ', 'info')
        self.exitFlag = 1

    def set_signalhandler(self):
        """ set signalhandler """
        signal.signal(signal.SIGTERM, self.signalhandler)
        signal.signal(signal.SIGINT, self.signalhandler)
