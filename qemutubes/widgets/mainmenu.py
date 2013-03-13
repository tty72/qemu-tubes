from . import ddmenu
from pyramid.request import Request

class MainMenu(ddmenu.DDMenu):
    id = 'main_menu'
    #FIXME: We should be generating URLs from route_url(), but I can't
    # think of an elegant way to do so.
    dbmenu = [{ 'label': 'Export', 'target': '/dbexport', },
              { 'label': 'Import', 'target': '/dbimport', 
                'attrs': {'class': 'qtpopup'}},
              ]
    toolsmenu = [{ 'label': 'DB', 'target': '#',
                   'submenu': dbmenu, } 
                  ]
    menu = { 'main': { 'label': 'Main', 'target': '/' },
             'tools': { 'label': 'Tools', 'target': '#',
                        'submenu': toolsmenu, }
             }
    active = ['main', 'tools']
                    
                    
                
