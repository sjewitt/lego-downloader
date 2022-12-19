from pymongo import MongoClient
import gridfs
import csv
from io import StringIO
import uuid

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
    page_length = 50
    set_filter = None


    def __init__(self):
        print('bootstrapping API...')
        self.LegoPlansDB = MongoClient().LegoPlans
#         self.loadplans()
    
    '''
    Just return a dict object listing the endpoints and what they do:
    '''
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
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
        with request.urlopen(self._sourceUrl) as src_data:
            _content = src_data.read().decode()
            # https://stackoverflow.com/questions/47741235/how-to-read-bytes-object-from-csv
            _f = StringIO(_content)
            csv_reader = csv.reader(_f,delimiter=",")
            header_is_read = False
            # row_counter = 0
            
            _debug = {}
            for _row in csv_reader:
                
                if not header_is_read:
                    _headers = _row # = ['SetNumber', 'URL', 'Description', 'DateAdded', 'DateModified']
                    header_is_read = True
                else:  # first row is headers, used as field names
                    try:
                        if len(_row) >= 5 and _row[1]:
                            _rowData = {
                                _headers[0]:_row[0],   # SetNumber
                                _headers[1]:_row[1],   # URL  
                                _headers[2]:_row[2],   # Description
                                _headers[3]:_row[3],   # DateAdded
                                _headers[4]:_row[4],   # DateModified
                                'key':_row[1].split('/')[-1].split('.pdf')[0]  # filename minus extension
                            }
                            # debug
                            if _row[1].split('/')[-1].split('.')[0] in _debug:
                                _debug[_row[1].split('/')[-1].split('.')[0]] += 1
                            else:
                                _debug[_row[1].split('/')[-1].split('.')[0]] = 1
                                
                            if _row[2] == '71247_X_Enchanted Car':
                                pass       #71247_X_Enchanted Car
                            
                            self.planData.append(_rowData)  #this may not be needed if I properly paginate
                            
                            ''' Need to insert specific rows, otherwise I will replace all the downloaded flags... '''
                            self.LegoPlansDB['DownloadQueue'].update_one({'SetNumber':_rowData.get('SetNumber',None),'URL':_rowData.get('URL',None)},
                                {
                                    '$set':{
                                        'SetNumber':_rowData.get('SetNumber',None),
                                        'URL':_rowData.get('URL',None),
                                        'Description':_rowData.get('Description',None),
                                        'DateAdded':_rowData.get('DateAdded',None),
                                        'DateModified':_rowData.get('DateModified',None),  #From source
                                        'DateStoredLocally':'yyyy-mm-dd',            #TODO
                                        'key':_rowData.get('key',None) # filename minus extension
                                }}, 
                                upsert=True)
                        
                        else:
                            pass
                        
                    except IndexError as err:
                        print(str(err))

            self.planDataLoaded = True  
            
            for thing in _debug:
                if _debug[thing] > 1:
                    print(thing, _debug[thing])
                
            
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
            _downloadedCount = list(self.LegoPlansDB['fs.files'].find({'filename':kwargs['setnumber'] + '.pdf'}))
            if _downloadedCount:
                _downloaded = True
                _flag = False    #we don't need to download it again
            
            self.LegoPlansDB['DownloadQueue'].update_one({'key':kwargs['setnumber']},{"$set":{"download": _flag,'downloaded':_downloaded}},upsert=True)
            _out = {"download": _flag,'downloaded':_downloaded}
        return(_out)
            
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
            
            ''' get GUID by filename: '''
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
    @cherrypy.tools.json_out()
    def updateplan(self):
        #see SO# 3743769
        json_in = cherrypy.request.json
        if self.LegoPlansDB['DownloadQueue'].count_documents({'key':json_in['key'], json_in['field']:json_in['val']}):
            return {'status':'ok','message':'field value has not changed'}
        result = self.LegoPlansDB['DownloadQueue'].update_one({'key':json_in['key']},{'$set':{json_in['field']:json_in['val'],'edited':True}})
        return result.raw_result

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def resetdownload(self):
        if hasattr(cherrypy.request, 'json'):
            json_in = cherrypy.request.json
            self.LegoPlansDB['DownloadQueue'].update_one({'key':json_in['key']},{'$set':{'download':True,'downloaded':False}})
            return{'msg':'download status reset','status':'ok'}
            
            #update cached data for UI as well:
            for plan in self.planData:
                if plan['key'] == json_in['key']:
                    plan['downloaded'] = False
        else:
            return({'msg':'Nothing to do...','status':'ok'})
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def default(self):
        return({ 'message':'endpoint not found' })

    def stripThing(self,thing,thingToStrip):
        return(thing.replace(thingToStrip,''))
    
    # NEW MODEL, SERVER-SIDE PAGINATION
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_page_length(self, **kwargs):
        self.page_length = int(kwargs.get('page_length',50))
        return {'status':'ok', 'new_page_length': self.page_length}
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_set_filter(self, **kwargs):
        self.set_filter = kwargs.get('set_filter',None)
        return {'status':'ok', 'new_set_filter': self.set_filter}
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_page_length(self):
        return {'status':'ok', 'page_length': self.page_length}
    
    @cherrypy.expose
    @cherrypy.tools.json_out()    
    def get_set_filter(self):
        return {'status':'ok', 'set_filter': self.set_filter}
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def paginated_plandata(self,**kwargs):
        
        curr_page = int(kwargs.get('page_num',1));
        # page_length = int(kwargs.get('page_length',self.page_length))
        page_length = self.page_length
        filter_key = kwargs.get('filter','')
        filter_mapper = {
            'stored':{'downloaded':True},
            'notstored':{'downloaded':{'$in':[None,False]}},
            'pending':{'download':True,'downloaded':{'$in':[None,False]} }
        }
        query = filter_mapper.get(filter_key,{})
        # set_num = kwargs.get('set',None)
        set_num = self.set_filter
        if set_num:
            set_regex = "".join(["^",set_num])
            query['SetNumber'] = {'$regex' :set_regex}

        # total = self.filtered_count_plandata(filter_mapper.get(filter_key,{}))
        total = self.filtered_count_plandata(query)
        entries = list(self.LegoPlansDB['DownloadQueue']
                      # .find(filter_mapper.get(filter_key,{}),{'_id':0})
                      .find(query,{'_id':0})
                       .skip((curr_page-1) * page_length)
                       .limit(page_length).sort('key',1))
        paged_data = {
            'pagination_data':{
                'total':total,
                'curr_page':curr_page,  
                'page_length':page_length,
                'filter_key':filter_key,
                'set_filter' : self.get_set_filter()['set_filter']
                },
            'entries':entries}
        return paged_data
    
    def filtered_count_plandata(self,count_filter={}):
        return self.LegoPlansDB['DownloadQueue'].count_documents(count_filter)

