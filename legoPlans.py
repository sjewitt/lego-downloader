from pymongo import MongoClient
import gridfs


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
    plansDB = None
    LegoPlansDB = None   


    def __init__(self):
        print('bootstrapping API...')
        self.LegoPlansDB = MongoClient().LegoPlans
#         self.loadplans()
    
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
    Read the CSV at source URL, cache as dict/in MongoDB, return boolean loaded status
    This refreshes the download queue from the source
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def loadplans(self):

        _out = request.urlopen(self._sourceUrl)
        _content = _out.read().decode()
        _reader = _content.split('\r\n')
        _headers = _reader[0].split(',')
        _reader.pop(0)
        for row in _reader:
            _row = row.split(',')
            if len(_row) >= 5:
                _rowData = {
                    _headers[0]:_row[0].replace('"',''),   # SetNumber
                    _headers[1]:_row[1].replace('"',''),   # URL  
                    _headers[2]:_row[2].replace('"',''),   # Description
                    _headers[3]:_row[3].replace('"',''),   # Notes
                    _headers[4]:_row[4].replace('"',''),   # DateAdded
                    _headers[5]:_row[5].replace('"',''),   # DateRetrieved
                    'key':(_row[1].replace('"','').split('/')[-1]).split('.')[0]  # filename minus extension
                }
                
                self.planData.append(_rowData)

                '''
                Need to insert specific rows, otherwise I will replace all the downloaded flags...
                '''
                self.LegoPlansDB['DownloadQueue'].update({'SetNumber':_row[0].replace('"',''),'URL':_row[1].replace('"','')},
                    {
                        '$set':{
                            'SetNumber':_row[0].replace('"',''),
                            'URL':_row[1].replace('"',''),
                            'Description':_row[2].replace('"',''),
                            'Notes':_row[3].replace('"',''),
                            'DateAdded':_row[4].replace('"',''),
                            'DateRetrieved':_row[5].replace('"',''),     #From source
                            'DateStoredLocally':'yyyy-mm-dd',            #TODO
                    }}, 
                    upsert=True)
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
    
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def flagdownload(self,**kwargs):
        _out = {}
        if kwargs!= None and 'setnumber' in kwargs and 'flag' in kwargs:
            print('setting download flag ' + kwargs['flag'])
            _flag = False
            if kwargs['flag'] == 'true':
                _flag = True
            #TODO: Test for file already in the gridFS:
            _downloaded = False
            _downloadedCount = self.LegoPlansDB['fs.files'].find({'filename':kwargs['setnumber'] + '.pdf'}).count()
            if _downloadedCount > 0:
                _downloaded = True
                _flag = False    #we don't need to download it again
            
            self.LegoPlansDB['DownloadQueue'].update({'key':kwargs['setnumber']},{"$set":{"download": _flag,'downloaded':_downloaded}},upsert=True)
            _out = {"download": _flag,'downloaded':_downloaded}
        return(_out)
            
    
    '''
    retrieve the plans from the mongoDB cache. Can return all, get a specific set by set number or filter by subsring
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getplandata(self,**kwargs):
        
        '''
        Also need to have option for flagged as download but not downloaded. This state will exist briefly while downloading, but before 
        insertion into mongo. Also, will indicate if the fetcher has failed.
        '''
        
        _out = list()
        self.planData = list(self.LegoPlansDB['DownloadQueue'].find({},{'_id':0}))
        
        if kwargs!= None and 'show' in kwargs and kwargs['show'] == 'all':
            _out = self.planData
            
        #get specific plan data:
        elif kwargs!= None and 'setnumber' in kwargs:
            for plan in self.planData:
                if kwargs['setnumber'] == plan['SetNumber']:
                    _out.append(plan)
                    
        #get stored plan data:
        elif kwargs!= None and 'show' in kwargs and kwargs['show'] == 'stored':
            
            for plan in self.planData:
                if 'downloaded' in plan and plan['downloaded'] == True:
                    _out.append(plan)
                    
        #get stored plan data:
        elif kwargs!= None and 'show' in kwargs and kwargs['show'] == 'notstored':
            
            for plan in self.planData:
                if ('downloaded' in plan and plan['downloaded'] == False) or not 'downloaded' in plan:
                    _out.append(plan)
                    
                    
        #get stored plan data:
        elif kwargs!= None and 'show' in kwargs and kwargs['show'] == 'pending':
#             print('pending')
            for plan in self.planData:
                if ('download' in plan and plan['download'] == True) and not plan['downloaded']:
                    _out.append(plan)
            
            
            
            
                    
        elif kwargs!= None and 'filter' in kwargs:
            for plan in self.planData:
                if kwargs['filter'].lower() in plan['Notes'].lower() or kwargs['filter'].lower() in plan['Description'].lower():
                    _out.append(plan)
        return(_out)

    @cherrypy.expose
    def getstoredplan(self,**kwargs):
        
        print('getting local stored data')
        if kwargs!= None and 'getlocal' in kwargs:
            
            '''
            get GUID by filename:
            '''
#             self.LegoPlansDB = MongoClient().LegoPlans
            _id = self.LegoPlansDB['fs.files'].find_one({'filename':kwargs['getlocal']},{'_id':1})
            
            if _id is not None:
                cherrypy.response.headers['Content-Type'] = 'application/pdf'
                if 'action' in kwargs and kwargs['action'] == 'download':
                    cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="' + kwargs['getlocal'] + '"'
                else:
                    cherrypy.response.headers['Content-Disposition'] = 'inline; filename="' + kwargs['getlocal'] + '"'
                print(_id['_id'])
                fs = gridfs.GridFS(self.LegoPlansDB)
                _file = fs.get(_id['_id'])
            
            

                return(_file)
            else:
                return('No matching file')
        
        else:
            return('No filename in parameter')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def updateplan(self):
        #see SO# 3743769
        json_in = cherrypy.request.json
        self.LegoPlansDB['DownloadQueue'].update({'key':json_in['key']},{'$set':{json_in['field']:json_in['val']}})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def resetdownload(self):
        if hasattr(cherrypy.request, 'json'):
            json_in = cherrypy.request.json
            self.LegoPlansDB['DownloadQueue'].update({'key':json_in['key']},{'$set':{'download':True,'downloaded':False}})
            return{'msg':'download status reset','status':'ok'}
            
            #update cached data for UI as well:
            for plan in self.planData:
                if plan['key'] == json_in['key']:
                    plan['downloaded'] = False
        else:
            return({'msg':'Nothing to do...','status':'ok'})

    def stripThing(self,thing,thingToStrip):
        return(thing.replace(thingToStrip,''))

