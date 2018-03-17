'''
Created on 22 Feb 2018

@author: smegh
'''
# from lxml import html
import requests
from bs4 import BeautifulSoup
# import plugins
# from plugins import *
import importlib

#Static imports
# from plugin1 import PluginOne
# from plugin2 import PluginTwo
# 
# _a = PluginOne()
# _b = PluginTwo()
# 
# _a.doIt()
# _b.doIt()

#Dynamic imports. These would come from the config.:
# _modules = [{'module':'plugins.plugin1','class':'PluginOne'},{'module':'plugins.plugin2','class':'PluginTwo'}]
_modules = [{'module':'plugins.plugin1','class':'PluginOne'},{'module':'plugins.plugin2','class':'PluginTwo'}]

_str = '<html><body>TESTTESTSTS</body></html>'

_urls = ['http://www.jcms-consulting.co.uk','http://jcms-consulting.co.uk/obtree-wcm.html']
results = []

for url in _urls:
    soup = BeautifulSoup((requests.get(url)).content,'html.parser')
    
#     print(soup)
    
    
    for importDef in _modules:
    #     module = __import__(importDef['module'])
    #better to use importLib. It better resolves package namespaces:
#         module = importlib.import_module(importDef['module'],importDef['class'])
        module = importlib.import_module(importDef['module'])
        
        clss = getattr(module, importDef['class'])
        inst = clss()
        
        results.append({'plugin':importDef['module'],'url':url,'pluginResult':inst.doIt(soup)})
        
        
print(results)    
