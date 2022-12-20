from pymongo import MongoClient
import gridfs
import requests
import argparse

def start_fetcher(db_server, db_port, collection):
    LegoPlansDB = MongoClient(db_server, db_port)[collection]
    
    queue = LegoPlansDB['DownloadQueue'].find_one({'downloaded': {'$in' : [None,False]},'download':True})
    
    if queue:
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
            ''' and flag as downloaded '''
            LegoPlansDB['DownloadQueue'].update_one({'key':queue['key']},{'$set':{'downloaded':True}})
        else:
            print('Flag as unavailable')
            LegoPlansDB['DownloadQueue'].update({'key':queue['key']},{'$unset':{'download':True,'downloadeded':True},'$set':{'unavailable':True}})
        
    else:
        print('Nothing to do...')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--db_server',default='localhost')
    parser.add_argument('-p','--db_port',default=27017, type=int)
    parser.add_argument('-c','--db_collection',default='LegoPlans')
    args = parser.parse_args()
    
    start_fetcher(args.db_server, args.db_port, args.db_collection)
