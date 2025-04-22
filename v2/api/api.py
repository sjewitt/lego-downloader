from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, StreamingResponse
import uvicorn
import handlers
from handlers.handlers import queue_page, queue_data,item_data, item_download
# from domain.domain import Config

app = FastAPI()

print(handlers)

@app.get("/")
def root():
    return {"root":True}

'''
UPDATED API
'''
# retrieve queue data (count, items per page)
@app.get("/api/summary/")
def get_queue_data():
    print("API:get_queue_data")
    return queue_data()

@app.get("/api/{page_num}")
def get_queue_page( page_num: int ):
    return queue_page(page_num)

@app.get("/api/not_queued/")
def get_unqueued_page_1():
    return get_unqueued_page(1)

@app.get("/api/not_queued/{page_num}/")
def get_unqueued_page( page_num:int=1 ):
    try:
        return queue_page(page_num,False,False,True)
    except Exception as ex:
        print(ex)

@app.get("/api/queued/")
def get_queued_1(  ):
    x = queue_page(1,True)
    return queue_page(1,True)

@app.get("/api/queued/{page_num}/")
def get_queued( page_num:int ):
    return queue_page(page_num,True)

@app.get("/api/downloaded/")
def get_downloaded_1(  ):
    return get_downloaded(1)

@app.get("/api/downloaded/{page_num}/")
def get_downloaded( page_num:int ):
    return queue_page(page_num, True, True)

@app.get("/api/pending/{page_num}/")
def get_pending( page_num:int):
    return queue_page(page_num,True,False)

# return the item data:
@app.get("/api/info/{item_key}")
def get_item_data(item_key: str):
    return item_data(item_key)

@app.get("/api/download/{item_key}")
def get_item_download(item_key: str):   #,download:bool=False
    res = item_download(item_key)
    if res[0] == "DOWNLOAD":
        # if download:
        headers = {'Content-Disposition': f'attachment; filename="{item_key}.pdf"'}
        return Response(content=res[1].read(), headers=headers)
        # return Response(res[1].read(), media_type="application/pdf")
    # return res
'''
END UPDATED API
'''


def run():
    # https://www.uvicorn.org/
    print("uvicorn running...")
    uvicorn.run(app)


