'''
Created on 16 Mar 2018

@author: silas
'''
from pymongo import MongoClient
import gridfs
import requests

LegoPlansDB = MongoClient().LegoPlans

queue = LegoPlansDB['DownloadQueue'].find_one({'downloaded': {'$in' : [None,False]},'download':True})
print(queue)
if not queue is None:
    if 'url' in queue:
        _file = requests.get(queue['url'])
    elif 'URL' in queue:
        _file = requests.get(queue['URL'])
    _name = queue['key'] + '.pdf'    
    print(_name)
# print(_file.content)

    fs = gridfs.GridFS(LegoPlansDB)
    key = fs.put(_file.content,filename=_name)
    print(key)
    '''
    and flag as downloaded
    '''
    LegoPlansDB['DownloadQueue'].update({'key':queue['key']},{'$set':{'downloaded':True}})
    
else:
    print('Nothing to do...')
