from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'], output_encoding='utf-8', encoding_errors='replace')
import cherrypy


class LegoPlansUI():
    def __init__(self):
        print('bootstrapping UI...')
        
    @cherrypy.expose
    def default(self):
        tmpl = lookup.get_template("index.html")
        return tmpl.render()
    
    @cherrypy.expose
    def listplans(self):
        tmpl = lookup.get_template("list-plans.html")
        return tmpl.render()
        
        

    
    
    