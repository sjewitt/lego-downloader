from fastapi import FastAPI
import uvicorn
from handlers.handlers import queue_page, queue_data, queue_item
# from domain.domain import Config

app = FastAPI()


@app.get("/")
def root():
    return {"root":True}


# retrieve queue data (count, items per page)
@app.get("/queue/")
def get_queue_data():
    print("API:get_queeu_data")
    return queue_data()

# type as QueuePage. This is 
# {
#   pagenum:n, 
#   items:QueueItem[], 
#   status:all/pending/downloaded/not-downloaded - enum?
# }
@app.get("/queue/page")
def get_queue_page():
    return queue_page(1)

# type as QueuePage
@app.get("/queue/page/{page_num}")
def get_queue_page( page_num: int ):
    return queue_page(page_num)

# type as QueuePage
@app.get("/queue/page/{page_num}/queued/{queued_for_download}")
def get_queue_page( page_num:int, queued_for_download: bool ):
    return queue_page(page_num,queued_for_download, False)

# type as QueuePage
@app.get("/queue/page/{page_num}/downloaded/{is_downloaded}")
def get_queue_page( page_num:int, is_downloaded: bool ):
    return queue_page(page_num, True, is_downloaded)

# type as QueuePage
@app.get("/queue/page/{page_num}/downloaded/{is_downloaded}")
def get_queue_page( page_num:int, is_downloaded: bool ):
    return queue_page(page_num,True,is_downloaded)

# type as QueueItem
@app.get("/queue/item/{item_id}")
def get_queue_item(item_id: int):
    return queue_item(item_id)


# def run(config:Config):
def run():
    # https://www.uvicorn.org/
    print("uvicorn running...")
    uvicorn.run(app)


