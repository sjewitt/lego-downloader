'''
Created on 16 Mar 2018

@author: silas
'''
from pymongo import MongoClient
import gridfs
import requests

LegoPlansDB = MongoClient().LegoPlans

# downloaded = list(LegoPlansDB['DownloadQueue'].find({'downloaded': True,'download':True}))
downloaded = list(LegoPlansDB['fs.files'].find({},{'filename':1}))
for download in downloaded:
    print(download['filename'].split('.')[0])
    #update queue:
    LegoPlansDB['DownloadQueue'].update({'key':download['filename'].split('.')[0]},{'$set':{'download':True,'downloaded':True}})
