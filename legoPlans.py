''' REST API server for LEGO plans application. It uses a Mongo database instance
directly as a property, rather than an abstracted database codebase. 
This URL:

https://www.blue-ocean-ag.com/bi/

gives access to magazine set plans taht are not stand-alone LEGO sets
'''

import csv
from io import StringIO
from datetime import datetime
from urllib import request
import gridfs
import pymongo
import uuid
from pymongo import MongoClient
import cherrypy
from tempfile import TemporaryFile

from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'], output_encoding='utf-8', encoding_errors='replace')


class LegoPlans():
    ''' Simple REST-based utility to list and download Lego plans using the API at https://brickset.com/exportscripts/instructions.
     - Class exposing JSON rest endpoints for listing Lego plans '''
    _sourceUrl = 'https://brickset.com/exportscripts/instructions'
    planData = []
    planDataLoaded = False
    plansDB = None
    LegoPlansDB = None
    page_length = 50
    set_filter = None

    def __init__(self,db_server, db_port,collection):
        ''' initialiser '''
        print('bootstrapping API...')
        self.LegoPlansDB = MongoClient(db_server, db_port)[collection]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        ''' Just return a dict object listing the endpoints and what they do: '''
        return({
            'info':'Simple REST API for lego plans retrieval from https://brickset.com',
            'api':{
                'loadplans':'Read the CSV at source URL, cache as dict, return boolean loaded status',
                'unloadplans':'clear the cached plans',
                'plansloaded':'return boolean of whether thans are loaded or not',
                'getplandata':'retrieve the plans from the cache. Can return all, get a specific set by set number or filter by subsring'
                }
        })

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def previous_fetches(self):
        ''' return the log of previous fetches from source '''
        return list(self.LegoPlansDB['SourceDownloadRecord'].find({},{'_id':False}).sort('timestamp',pymongo.DESCENDING))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def loadplans(self):
        ''' Read the CSV at source URL, cache as dict/in MongoDB, return boolean loaded status
        This refreshes the download queue from the source '''
        now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        with request.urlopen(self._sourceUrl) as src_data:
            _out = {'timestamp':now,'status':'ok','message':'ok', 'error_count':0, 'errors':[], 'data':{'num_added':0, 'num_processed':0,'new_entries':[]}}
            _content = src_data.read().decode()
            # https://stackoverflow.com/questions/47741235/how-to-read-bytes-object-from-csv
            _f = StringIO(_content)
            csv_reader = csv.reader(_f,delimiter=",")
            header_is_read = False
            for _row in csv_reader:
                if not header_is_read:
                    _headers = _row # = ['SetNumber', 'URL', 'Description', 'DateAdded', 'DateModified']
                    header_is_read = True
                else:  # first row is headers, used as field names
                    try:
                        if len(_row) >= 5 and _row[1]:
                            row_data = {
                                _headers[0]:_row[0],   # SetNumber
                                _headers[1]:_row[1],   # URL
                                _headers[2]:_row[2],   # Description
                                _headers[3]:_row[3],   # DateAdded
                                _headers[4]:_row[4],   # DateModified
                                'key':_row[1].split('/')[-1].split('.pdf')[0]  # filename minus extension
                            }

                            self.planData.append(row_data)

                            # Need to insert specific rows, otherwise I will replace all the downloaded flags...
                            result = self.LegoPlansDB['DownloadQueue'].update_one({'SetNumber':row_data.get('SetNumber',None),'URL':row_data.get('URL',None)},
                                {
                                    '$set':{
                                        'SetNumber':row_data.get('SetNumber',None),
                                        'URL':row_data.get('URL',None),
                                        'Description':row_data.get('Description',None),
                                        'DateAdded':row_data.get('DateAdded',None),
                                        'DateModified':row_data.get('DateModified',None),  #From source
                                        'DateStoredLocally': now,
                                        'key':row_data.get('key',None) # filename minus extension
                                }},
                                upsert=True)
                            _out['data']['num_processed'] += 1
                            if not result.raw_result['updatedExisting']:
                                _out['data']['num_added'] += 1
                                _out['data']['new_entries'].append(row_data)
                        else:
                            pass
                    except IndexError as err:
                        _out['error_count'] += 1
                        _out['errors'].append({'error':str(err),'entry':row_data})  #this entry is the CSV row (a list, therefore)
                        _out['status'] = 'warning'
                    except Exception as err:
                        _out['error_count'] += 1
                        _out['errors'].append({'error':str(err),'entry':row_data})
                        _out['status'] = 'warning'

            self.planDataLoaded = True

        # return(self.plansloaded())
        self.LegoPlansDB['SourceDownloadRecord'].insert_one(_out)
        del _out['_id']
        return _out

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def unloadplans(self):
        ''' clear the cached plans '''
        self.planData = []
        self.planDataLoaded = False
        return self.plansloaded()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def plansloaded(self):
        ''' return boolean of whether thans are loaded or not '''
        return {'planDataLoaded':self.planDataLoaded}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def flagdownload(self,**kwargs):
        ''' flag an entry for processing by fetcher '''
        _out = {}
        if kwargs is not None and 'setnumber' in kwargs and 'flag' in kwargs:
            print('setting download flag ' + kwargs['flag'])
            _flag = False
            if kwargs['flag'] == 'true':
                _flag = True
            #TODO: Test for file already in the gridFS:
            is_downloaded = False
            downloaded_count = list(self.LegoPlansDB['fs.files'].find({'filename':kwargs['setnumber'] + '.pdf'}))
            if downloaded_count:
                is_downloaded = True
                _flag = False    #we don't need to download it again

            self.LegoPlansDB['DownloadQueue'].update_one({'key':kwargs['setnumber']},{"$set":{"download": _flag,'downloaded':is_downloaded}},upsert=True)
            _out = {"download": _flag,'downloaded':is_downloaded}
        return _out

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getplandata(self,**kwargs):
        '''  Also need to have option for flagged as download but not downloaded. This state will exist briefly while downloading, but before
        insertion into mongo. Also, will indicate if the fetcher has failed. '''
        _out = []
        self.planData = list(self.LegoPlansDB['DownloadQueue'].find({},{'_id':0}))
        if kwargs is not None and 'show' in kwargs and kwargs['show'] == 'all':
            _out = self.planData

        #get specific plan data:
        elif kwargs is not None and 'setnumber' in kwargs:
            for plan in self.planData:
                if kwargs['setnumber'] == plan['SetNumber']:
                    _out.append(plan)

        #get stored plan data:
        elif kwargs is not None and 'show' in kwargs and kwargs['show'] == 'stored':
            for plan in self.planData:
                if 'downloaded' in plan and plan['downloaded'] is True:
                    _out.append(plan)

        #get stored plan data:
        elif kwargs is not None and 'show' in kwargs and kwargs['show'] == 'notstored':

            for plan in self.planData:
                if ('downloaded' in plan and plan['downloaded'] is False) or not 'downloaded' in plan:
                    _out.append(plan)

        #get stored plan data:
        elif kwargs is not None and 'show' in kwargs and kwargs['show'] == 'pending':
            for plan in self.planData:
                if ('download' in plan and plan['download'] is True) and not plan['downloaded']:
                    _out.append(plan)

        elif kwargs is not None and 'filter' in kwargs:
            for plan in self.planData:
                if kwargs['filter'].lower() in plan['Notes'].lower() or kwargs['filter'].lower() in plan['Description'].lower():
                    _out.append(plan)
        return _out

    @cherrypy.expose
    def getstoredplan(self,**kwargs):
        ''' retrieve a PDF binary stored inh gridFS '''
        if kwargs is not None and 'getlocal' in kwargs:

            # get GUID by filename:
            _id = self.LegoPlansDB['fs.files'].find_one({'filename':kwargs['getlocal']},{'_id':1})
            if _id is not None:
                cherrypy.response.headers['Content-Type'] = 'application/pdf'
                if 'action' in kwargs and kwargs['action'] == 'download':
                    cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="' + kwargs['getlocal'] + '"'
                else:
                    cherrypy.response.headers['Content-Disposition'] = 'inline; filename="' + kwargs['getlocal'] + '"'
                fs = gridfs.GridFS(self.LegoPlansDB)
                _file = fs.get(_id['_id'])
                return _file
            return 'No matching file'
        return 'No filename in parameter'

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def updateplan(self):
        ''' update a plan record with Description or Notes. see SO# 3743769 '''
        json_in = cherrypy.request.json
        if self.LegoPlansDB['DownloadQueue'].count_documents({'key':json_in['key'], json_in['field']:json_in['val']}):
            return {'status':'ok','message':'field value has not changed'}
        result = self.LegoPlansDB['DownloadQueue'].update_one({'key':json_in['key']},{'$set':{json_in['field']:json_in['val'],'edited':True}})
        return result.raw_result

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def resetdownload(self):
        ''' re-queue a download '''
        if hasattr(cherrypy.request, 'json'):
            json_in = cherrypy.request.json
            self.LegoPlansDB['DownloadQueue'].update_one({'key':json_in['key']},{'$set':{'download':True,'downloaded':False}})
            return{'msg':'download status reset','status':'ok'}

        return {'msg':'Nothing to do...','status':'ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self,**kwargs):
        # https://riptutorial.com/cherrypy/example/25395/file-upload-with-cherrypy
        print(kwargs)
        # in_data=cherrypy.request
        print('debug')
        uploaded_set_number = kwargs.get('uploaded_set_number',None)
        uploaded_set_description = kwargs.get('uploaded_set_description',None)
        uploaded_set_notes = kwargs.get('uploaded_set_notes','-')
        uploaded_file = kwargs.get('uploaded_set_file',None)
        file_name = uploaded_file.filename
        # Process uploaded file data, and send to save function:
        key = uuid.uuid4()
        size = 0
        # need temp file here because I am not writing to FS:
        with TemporaryFile() as tmp:
            while True:
                file_data = uploaded_file.file.read(8192)
                if not file_data:
                    break
                tmp.write(file_data)
                size+=len(file_data)
        
            grid_fs = gridfs.GridFS(self.LegoPlansDB)
            # get raw file data here:
            tmp.seek(0)
            grid_fs.put(tmp.read(),filename=''.join([str(key),'.pdf']))
            print(key)
        
        # will need to do this - transaction: actually can't - need cluster or sharded deployment...
        # https://www.mongodb.com/docs/upcoming/core/transactions/?_ga=2.30935807.1188859118.1672320290-238380667.1654968213
        # step 1: insert metadata, as fif it was a standard queued job
        date_now = "DATE TODO"
        
        print(key)
        result = self.LegoPlansDB['DownloadQueue'].update_one({'SetNumber':uploaded_set_number,'URL':None},
        {
            '$set':{
                'SetNumber' : uploaded_set_number,
                'URL' : 'Manual upload',
                'Description' : uploaded_set_description,
                'Notes' : uploaded_set_notes,
                'DateAdded' : date_now,
                'DateModified' : date_now,  #From source
                'DateStoredLocally' : date_now,
                'key' : str(key),                # a UUID for manual upload
                #'key' : file_name,
                'download':True,            # Need these to properly show in the UI
                'downloaded':True           # Need these to properly show in the UI
        }},
        upsert=True)
        print(result)
        
        # TODO: Check form submission, and redirect to uploaded view if OK, or present a message if error:
        raise cherrypy.HTTPRedirect('/?filter=stored')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def default(self):
        ''' handle unknown endpoint '''
        return { 'message':'endpoint not found' }

    def strip_thing(self,thing,thing_to_strip):
        ''' utility to strip character x from string y '''
        return thing.replace(thing_to_strip,'')

    # NEW MODEL, SERVER-SIDE PAGINATION
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_page_length(self, **kwargs):
        ''' set the UI page length '''
        self.page_length = int(kwargs.get('page_length',50))
        return {'status':'ok', 'new_page_length': self.page_length}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_set_filter(self, **kwargs):
        ''' set a string filter for set number '''
        self.set_filter = kwargs.get('set_filter',None)
        return {'status':'ok', 'new_set_filter': self.set_filter}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_page_length(self):
        ''' return page length, for pagination object '''
        return {'status':'ok', 'page_length': self.page_length}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_set_filter(self):
        ''' return the current set number filter '''
        return {'status':'ok', 'set_filter': self.set_filter}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def paginated_plandata(self,**kwargs):
        ''' get specified page of plans, filtered as apprpriate '''
        curr_page = int(kwargs.get('page_num',1))
        # page_length = int(kwargs.get('page_length',self.page_length))
        page_length = self.page_length
        filter_key = kwargs.get('filter','')
        filter_mapper = {
            'stored':{'downloaded':True},
            'notstored':{'downloaded':{'$in':[None,False]}},
            'pending':{'download':True,'downloaded':{'$in':[None,False]} }
        }
        query = filter_mapper.get(filter_key,{})
        set_num = self.set_filter
        if set_num:
            set_regex = "".join(["^",set_num])
            query['SetNumber'] = {'$regex' :set_regex}

        total = self.filtered_count_plandata(query)
        entries = list(self.LegoPlansDB['DownloadQueue']
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
        ''' return a filtered count of matching documents '''
        return self.LegoPlansDB['DownloadQueue'].count_documents(count_filter)

