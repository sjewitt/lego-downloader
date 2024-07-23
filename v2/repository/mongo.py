import gridfs
import pymongo
import uuid
from pymongo import MongoClient
import repository.config as config
from domain.exceptions import ItemNotDownloadedException, ItemNotFoundException, ItemRemovedException


# config here!
conf = config.get()
lego_plans_database = MongoClient(conf.db_server, 
                                  conf.db_port)[conf.db_collection]

def get_plans_data(is_downloaded=False,queued_for_download=False):
    print("Mongo: in get plans")
    query = {}
    if is_downloaded:
        query = {"download":True,"downloaded":True}
    if queued_for_download:
        query = {"download":True,"downloaded":False}
    
    result = lego_plans_database['DownloadQueue'].count_documents(query)    
    return {"item_count":result,"page_length":config.get().page_length}

def get_plans_count(is_downloaded=False,
                        queued_for_download=False):
    query = {}
    if queued_for_download:
        query = {"download":True,"downloaded":False}
    if is_downloaded:
        query = {"download":True,"downloaded":True}
    result = lego_plans_database['DownloadQueue'].count_documents(query)
    return result

def get_plans_paginated(page=1,length=50,
                        is_downloaded=False,
                        queued_for_download=False,
                        not_queued=False):
    ''' if we pass use_filter, we explicitly need to EXCLUDE where plans
     are either queued or unqueued. May need to reorganize this whole
    section as different handler functions... '''

    count_data = get_plans_count(is_downloaded,queued_for_download)
    query = {}
    if queued_for_download:
        query = {"download":True,"downloaded":False}
    if is_downloaded:
        query = {"download":True,"downloaded":True}
    if not_queued:
        query={'$or':[{"download":False, "download":{"$exists":False}}]}
        pass

    try:
        # if page > 1:
        result = list(lego_plans_database['DownloadQueue']
            .find(query,{"_id":False})
            .skip((page-1) * length)
            .limit(length)
            .sort('key',pymongo.ASCENDING)
        )
        # else:
            # result = list(lego_plans_database['DownloadQueue']
            #     .find(query,{"_id":False})
            #     .limit(length)
            #     .sort('key',pymongo.ASCENDING)
            # )
        x = {"count":count_data,'page':page,'filter':query, 'data':result}
        return x
    except Exception as ex:
        print(ex)
        return {"error":f"cannot run query: {ex}"}

def get_item_data(plan_id:str=None):
    if plan_id:
        try:
            # check that the supplied key maps to a record, and if so, the record is actually downloaded 
            result = dict(lego_plans_database['DownloadQueue'].find_one({'key':plan_id},{'_id':False}))
            return result
        except Exception as ex:
            return({
                'message':'plan not found', 
                'error': str(ex),
                'key':plan_id},)

# return the file object to front-end; set FastAPI download header
# at API endpoint:
def get_item_download(plan_id:str=None):
    if plan_id:
        try:
            result = lego_plans_database['DownloadQueue'].find_one({'key':plan_id},{'_id':False})
            if result:
                result = dict(result)
                if result['downloaded']:

                    _id = lego_plans_database['fs.files'].find_one({'filename':f"{plan_id}.pdf"},{'_id':1})
                    if _id is not None:
                        # fet the file object and pass back to API:
                        fs = gridfs.GridFS(lego_plans_database)
                        _file = fs.get(_id['_id'])
                        return "DOWNLOAD",_file

                    return result
                raise ItemNotDownloadedException(f"plan {result['key']} exists, but is not downloaded")
            raise ItemNotFoundException(f"Cannot find specified Plan ({plan_id})")
        except ItemNotFoundException as ex:
            return({
                'message':'plan not found', 
                'error': str(ex),
                'key':plan_id},)
        except ItemNotDownloadedException as ex:
            return({
                'message':'plan found, but is not downloaded.', 
                'error': str(ex),
                'key':plan_id},)
        except Exception as ex:
            return({
                'message':f"Unspecified error occurred for plan with key {result['key']}", 
                'error': str(ex),
                'key':plan_id},)


