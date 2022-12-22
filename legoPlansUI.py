''' expose UI templaes '''
import cherrypy
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'], output_encoding='utf-8', encoding_errors='replace')

class LegoPlansUI():
    ''' expose UI templates, using Mako Templates '''
    def __init__(self):
        ''' startup of UI '''
        print('bootstrapping UI...')

    @cherrypy.expose
    def default(self):
        ''' render start page '''
        tmpl = lookup.get_template("index.html")
        return tmpl.render()

    @cherrypy.expose
    def manage(self):
        ''' render manage page '''
        tmpl = lookup.get_template("manage.html")
        return tmpl.render()

    # @cherrypy.expose
    # def listplans(self):
    #     ''' NOT USED. load client-side list '''
    #     tmpl = lookup.get_template("list-plans.html")
    #     return tmpl.render()

    # @cherrypy.expose
    # def listplans_paginated(self):
    #     ''' NOT USED. load server-side list '''
    #     tmpl = lookup.get_template("list-plans-paginated.html")
    #     return tmpl.render()
