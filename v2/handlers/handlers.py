import repository.database as db
# do an enum of downloaded states?

def queue_page(
        page_num:int = 0, 
        queued_for_download:bool=False,
        is_downloaded=False):
    ''' retrieve a page of download queue items. 
    Need to use ORM abstraction here!'''
    return db.get_queue_page(page_num,queued_for_download,is_downloaded)
    # return {"status":"ok","input":{
    #     "page_num":page_num,
    #     "queued_for_download":queued_for_download,
    #     "is_downloaded":is_downloaded
    # }}


def queue_data():
    # return {"item_count":-1, "page_length":-1}
    print("handlers: queue_data()")
    return db.get_queue_data()

def queue_item(item_id: int):
    return {"item_id":item_id, "item_data":{"to":"do"}}