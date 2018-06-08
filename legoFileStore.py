'''
Created on 16 Mar 2018

@author: silas
'''
from pymongo import MongoClient
import gridfs
import requests

LegoPlansDB = MongoClient().LegoPlans

queue = LegoPlansDB['DownloadQueue'].find_one({'downloaded': {'$in' : [None,False]},'download':True})

if not queue is None:
    if 'url' in queue:
        _file = requests.get(queue['url'])
    elif 'URL' in queue:
        _file = requests.get(queue['URL'])
    _name = queue['key'] + '.pdf'    
    print(_name)
    
    #test for response code. If 200, proceed, if not, abort and set a ststus of unavailable on the document.
    print(_file.status_code)
    if _file.status_code == 200:

        fs = gridfs.GridFS(LegoPlansDB)
        key = fs.put(_file.content,filename=_name)
        print(key)
        '''
        and flag as downloaded
        '''
        LegoPlansDB['DownloadQueue'].update({'key':queue['key']},{'$set':{'downloaded':True}})
    else:
        print('Flag as unavailable')
        LegoPlansDB['DownloadQueue'].update({'key':queue['key']},{'$unset':{'download':True,'downloadeded':True},'$set':{'unavailable':True}})
    
else:
    print('Nothing to do...')
