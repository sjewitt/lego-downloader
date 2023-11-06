import repository.mongo as mongo

# wrapper over mongo (do as UOW eventually?)
def get_queue_page(page_num:int = 0, 
        queued_for_download:bool=False,
        is_downloaded=False):
    return mongo.get_plans_paginated(page_num,50,is_downloaded,queued_for_download)

def get_queue_data(queued_for_download:bool=False,
        is_downloaded=False):
    print("database:get_queue_data")
    return mongo.get_plans_data(queued_for_download,is_downloaded)