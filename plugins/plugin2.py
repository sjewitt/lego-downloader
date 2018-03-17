'''
Created on 22 Feb 2018

@author: smegh
'''
from plugins.abstract import AbstractPlugin

class PluginTwo(AbstractPlugin):
    
    def doIt(self,args=None):
        print('extracting first p tag:')
        _out = None
        if args:
            _out = args.find('p')
        return(_out)
    