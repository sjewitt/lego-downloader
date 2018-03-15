'''
Created on 22 Feb 2018

@author: smegh
'''
from plugins.abstract import AbstractPlugin

class PluginOne(AbstractPlugin):
    
    def doIt(self,args=None):
        _out = None
        print('extracting title:')
        if args:    #args should be a soup object
            _out = args.find('title')
            
        return(_out)