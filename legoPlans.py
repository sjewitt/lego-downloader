from urllib import request
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'], output_encoding='utf-8', encoding_errors='replace')
import cherrypy

'''
Simple REST-based utility to list and download Lego plans using the API at https://brickset.com/exportscripts/instructions.

 - Class exposing JSON rest endpoints for listing Lego plans
'''

class LegoPlans():
    
    _sourceUrl = 'https://brickset.com/exportscripts/instructions'
    planData = []
    planDataLoaded = False


    def __init__(self):
        self.loadplans()
    
    '''
    Just return a dict object listing the endpoints and what they do:
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def default(self):
        return({
            'info':'Simple REST API for lego plans retrieval from https://brickset.com',
            'api':{
                'loadplans':'Read the CSV at source URL, cache as dict, return boolean loaded status',
                'unloadplans':'clear the cached plans',
                'plansloaded':'return boolean of whether thans are loaded or not',
                'getplandata':'retrieve the plans from the cache. Can return all, get a specific set by set number or filter by subsring'
                }
        })
        

    #issues with DictReader - kept getting single characters for headers, and inconsistent row sizes.
    #possily also issues as there are {} characters which may be causing parsing problems as well.
    '''
    Read the CSV at source URL, cache as dict, return boolean loaded status
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
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
    
    '''
    clear the cached plans
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def unloadplans(self):
        self.planData = []
        self.planDataLoaded = False
        return(self.plansloaded())
        
    '''
    return boolean of whether thans are loaded or not
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def plansloaded(self):
        return({'planDataLoaded':self.planDataLoaded})
    
    '''
    retrieve the plans from the cache. Can return all, get a specific set by set number or filter by subsring
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getplandata(self,**kwargs):
        _out = list()
        if kwargs!= None and 'setnumber' in kwargs and kwargs['setnumber'] == 'showall':
            _out = self.planData
            
        #get filtered data:
        elif kwargs!= None and 'setnumber' in kwargs:
            for plan in self.planData:
                if kwargs['setnumber'] == plan['SetNumber']:
                    _out.append(plan)
                    
        elif kwargs!= None and 'filter' in kwargs:
            for plan in self.planData:
                if kwargs['filter'].lower() in plan['Notes'].lower() or kwargs['filter'].lower() in plan['Description'].lower():
                    _out.append(plan)
            
        return(_out)

    def stripThing(self,thing,thingToStrip):
        return(thing.replace(thingToStrip,''))

