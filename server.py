'''
Simple REST-based utility to list and download Lego plans using the API at https://brickset.com/exportscripts/instructions.

 - The CherryPy server start, defining URL roots for REST API and user interface.
'''
import os
import argparse
import cherrypy


from legoPlans import LegoPlans
from legoPlansUI import LegoPlansUI
# from bson.json_util import default

def error_page_404(status, message, traceback, version):
    return iter([status, message, traceback, version])

def start_server(server, port, db_server, db_port, collection):
    root_dir = os.path.abspath( os.path.dirname(__file__))
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static' : {
            'tools.staticdir.on'    : True,
            'tools.staticdir.dir'   : os.path.join(os.getcwd(), 'static'),
            'tools.gzip.on'         : True
        }
    }

    cherrypy.config.update({
        'error_page.404': error_page_404,
        'server.socket_host': server,
        'server.socket_port': port,
        'tools.mako.directories' : [os.path.join(root_dir,'templates')],    #silas
        })
    cherrypy.engine.start()

    #API:
    cherrypy.tree.mount(LegoPlans(db_server, db_port,collection), '/api/',conf)

    #UI:
    cherrypy.tree.mount(LegoPlansUI(), '/',conf)

    #And load the plans:

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--app_server',default='127.0.0.1')
    parser.add_argument('-b','--app_port',default=8081, type=int)
    parser.add_argument('-d','--db_server',default='localhost')
    parser.add_argument('-p','--db_port',default=27017, type=int)
    parser.add_argument('-c','--db_collection',default='LegoPlans')
    args = parser.parse_args()

    start_server(args.app_server,args.app_port, args.db_server, args.db_port, args.db_collection)
