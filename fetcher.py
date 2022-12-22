
''' fetcher for LEGO plans queue '''
import argparse
from pymongo import MongoClient
import gridfs
import requests


def start_fetcher(db_server, db_port, collection):
    ''' check for and process next unfetched queued plan entry '''
    legoplans_database = MongoClient(db_server, db_port)[collection]

    queue = legoplans_database['DownloadQueue'].find_one({'downloaded': {'$in' : [None,False]},'download':True})

    if queue:
        if 'url' in queue:
            plan_file_url = requests.get(queue['url'],timeout=50)
        elif 'URL' in queue:
            plan_file_url = requests.get(queue['URL'],timeout=50)
        file_name = queue['key'] + '.pdf'
        print(file_name)

        #test for response code. If 200, proceed, if not, abort and set a ststus of unavailable on the document.
        print(plan_file_url.status_code)
        if plan_file_url.status_code == 200:

            grid_fs = gridfs.GridFS(legoplans_database)
            key = grid_fs.put(plan_file_url.content,filename=file_name)
            print(key)
            # and flag as downloaded
            legoplans_database['DownloadQueue'].update_one({'key':queue['key']},{'$set':{'downloaded':True}})
        else:
            print('Flag as unavailable')
            legoplans_database['DownloadQueue'].update({'key':queue['key']},{'$unset':{'download':True,'downloadeded':True},'$set':{'unavailable':True}})

    else:
        print('Nothing to do...')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--db_server',default='localhost')
    parser.add_argument('-p','--db_port',default=27017, type=int)
    parser.add_argument('-c','--db_collection',default='LegoPlans')
    args = parser.parse_args()

    start_fetcher(args.db_server, args.db_port, args.db_collection)
