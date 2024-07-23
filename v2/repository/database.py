import repository.mongo as mongo

# wrapper over mongo (do as UOW eventually?)
def get_queue_page(page_num:int = 0, 
        queued_for_download:bool=False,
        is_downloaded=False,
        not_queued=False):
    return mongo.get_plans_paginated(page_num,50,is_downloaded,queued_for_download,not_queued)

def get_queue_data(queued_for_download:bool=False,
        is_downloaded=False):
    print("database:get_queue_data")
    return mongo.get_plans_data(queued_for_download,is_downloaded)

def get_item_data(item_id:str):
    return mongo.get_item_data(item_id)

def get_item_download(item_id:str):
    return mongo.get_item_download(item_id)