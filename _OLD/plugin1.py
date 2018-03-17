'''
Created on 22 Feb 2018

@author: smegh
'''
from abstract import AbstractPlugin

class PluginOne(AbstractPlugin):
    
    def doIt(self,args=None):
        print('Plugin one')
        if args:
            print(args)