'''
Simple REST-based utility to list and download Lego plans using the API at https://brickset.com/exportscripts/instructions.

 - The CherryPy server start, defining URL roots for REST API and user interface.
'''
import os
import cherrypy
import yaml


from include.legoPlans import LegoPlans
from include.legoPlansUI import LegoPlansUI
# from bson.json_util import default

def error_page_404(status, message, traceback, version):
    return iter([status, message, traceback, version])

def start_server(app_server, app_port, db_server, db_port, db_collection):
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
        'server.socket_host': app_server,
        'server.socket_port': app_port,
        'tools.mako.directories' : [os.path.join(root_dir,'templates')],    #silas
        })
    cherrypy.engine.start()

    #API:
    cherrypy.tree.mount(LegoPlans(db_server, db_port,db_collection), '/api/',conf)

    #UI:
    cherrypy.tree.mount(LegoPlansUI(), '/',conf)

if __name__ == '__main__':
    with(open('settings/config.yaml') as config_file):
        conf = yaml.safe_load(config_file)
        print(conf['server'])

    start_server(
        app_server=conf['server']['app_server'],
        app_port=conf['server']['app_port'],
        db_server=conf['database']['db_server'],
        db_port=conf['database']['db_port'],
        db_collection=conf['database']['db_collection'],
    )
