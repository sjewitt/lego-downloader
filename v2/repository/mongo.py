import gridfs
import pymongo
import uuid
from pymongo import MongoClient
import repository.config as config


# config here!
conf = config.get()
lego_plans_database = MongoClient(conf.db_server, conf.db_port)[conf.db_collection]

def get_plans_data(is_downloaded=False,queued_for_download=False):
    print("Mongo: in get plans")
    query = {}
    if is_downloaded:
        query = {"download":True,"downloaded":True}
    if queued_for_download:
        query = {"download":True,"downloaded":False}
    
    result = lego_plans_database['DownloadQueue'].count_documents(query)    
    return {"item_count":result,"page_length":config.get().page_length}


def get_plans_paginated(page=1,length=50,is_downloaded=False,queued_for_download=False):
    breakpoint()
    query = {}
    if queued_for_download:
        query = {"download":True,"downloaded":False}
    if is_downloaded:
        query = {"download":True,"downloaded":True}
    
    
    try:
        if page > 1:
            result = list(lego_plans_database['DownloadQueue']
                .find(query,{"_id":False})
                .skip((page-1) * length)
                .limit(length)
                .sort('key',pymongo.ASCENDING)
            )
        else:
            result = list(lego_plans_database['DownloadQueue']
                .find(query,{"_id":False})
                .limit(length)
                .sort('key',pymongo.ASCENDING)
            )

    except Exception as ex:
        print(ex)
        result = {"error":f"cannot run query: {ex}"}

    return result

