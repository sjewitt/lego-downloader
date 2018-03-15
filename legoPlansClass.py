from urllib import request
import json
# from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'], output_encoding='utf-8', encoding_errors='replace')
# import csv
# from collections import OrderedDict
import cherrypy
# from cherrypy import tools

# from mako.template import Template

class LegoPlans():
    
    _sourceUrl = 'https://brickset.com/exportscripts/instructions'
    planData = []
    planDataLoaded = False


    def __init__(self):
        print('bootstrapping...')
        self.loadplans()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def default(self):
        return({'info':'Simple REST API for lego plans retrieval from https://brickset.com'})
        

    #issues with DictReader - kept getting single characters for headers, and inconsistent row sizes.
    #possily also issues as there are {} characters which may be causing parsing problems as well.
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def loadplans(self):
        if self.planDataLoaded == False:
        
            _out = request.urlopen(self._sourceUrl)
            _content = _out.read().decode()
            _reader = _content.split('\r\n')
            _headers = _reader[0].split(',')
            _reader.pop(0)
            for row in _reader:
                _row = row.split(',')
                if len(_row) >= 5:
                    _rowData = {_headers[0]:_row[0].replace('"',''),_headers[1]:_row[1].replace('"',''),_headers[2]:_row[2].replace('"',''),_headers[3]:_row[3].replace('"',''),_headers[4]:_row[4].replace('"','')}
                    self.planData.append(_rowData)
            
            self.planDataLoaded = True
            
        return(self.plansloaded())
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def unloadplans(self):
        self.planData = []
        self.planDataLoaded = False
        return(self.plansloaded())
        
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def plansloaded(self):
        return({'planDataLoaded':self.planDataLoaded})
    
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def getplandata(self,**kwargs):
        print(kwargs)
        _out = list()

        if kwargs!= None and 'setnumber' in kwargs and kwargs['setnumber'] == 'showall':
            _out = self.planData
        #get filtered data:
     
        else:
            for plan in self.planData:
                print(plan['SetNumber'])
                if kwargs!= None and 'setnumber' in kwargs and kwargs['setnumber'] == plan['SetNumber']:
                    print('fitering..')
                    _out.append(plan)
                 
        return(_out)

    def stripThing(self,thing,thingToStrip):
        return(thing.replace(thingToStrip,''))

class LegoPlansUI():
    def __init__(self):
        print('bootstrapping UI...')
        
    @cherrypy.expose
    def default(self):
        tmpl = lookup.get_template("index.html")
        return tmpl.render()
    
    @cherrypy.expose
    def listplans(self):
        tmpl = lookup.get_template("list-plans.html")
        return tmpl.render()
        
        

    
    
    