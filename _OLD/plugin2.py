'''
Created on 22 Feb 2018

@author: smegh
'''
from abstract import AbstractPlugin

class PluginTwo(AbstractPlugin):
    
    def doIt(self,args=None):
        print('Plugin two')
        if args:
            print(args)
    