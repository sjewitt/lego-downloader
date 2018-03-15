import cherrypy
import os
from legoPlans import LegoPlans
from legoPlansUI import LegoPlansUI

'''
Simple REST-based utility to list and download Lego plans using the API at https://brickset.com/exportscripts/instructions.

 - The CherryPy server start, defining URL roots for REST API and user interface.
'''

def error_page_404(status, message, traceback, version):
    return "404 Error!"



def start_server():
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
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'tools.mako.directories' : [os.path.join(root_dir,'templates')],    #silas
        })
    cherrypy.engine.start()
    
    #API:
    cherrypy.tree.mount(LegoPlans(), '/api',conf)
    
    #UI:
    cherrypy.tree.mount(LegoPlansUI(), '/',conf)
    
    #And load the plans:

if __name__ == '__main__':
    start_server()