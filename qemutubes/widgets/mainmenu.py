from . import ddmenu

class MainMenu(ddmenu.DDMenu):
    id = 'main_menu'
    dbmenu = { 'export': { 'label': 'Export', 'target': '#', },
               'import': { 'label': 'Import', 'target': '#', },
               }
    toolsmenu = { 'dbmenu': { 'label': 'DB', 'target': '#',
                              'submenu': dbmenu, } 
                  }
    menu = { 'main': { 'label': 'Main', 'target': '/' },
             'tools': { 'label': 'Tools', 'target': '#',
                        'submenu': toolsmenu, }
             }
    active = ['main', 'tools']
                    
                    
                
