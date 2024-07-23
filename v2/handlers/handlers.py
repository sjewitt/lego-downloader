import repository.database as db
# do an enum of downloaded states?

def queue_page(
        page_num:int = 0, 
        queued_for_download:bool=False,
        is_downloaded=False,
        not_queued=False,):
    ''' retrieve a page of download queue items. Need to use ORM abstraction here!'''
    return db.get_queue_page(page_num,queued_for_download,is_downloaded,not_queued)

def queue_data():
    return db.get_queue_data()

def item_data(item_id: str):
    return db.get_item_data(item_id)

def item_download(item_id: str):
    return db.get_item_download(item_id)
