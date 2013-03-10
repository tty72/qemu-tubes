from . import ddmenu

class MainMenu(ddmenu.DDMenu):
    id = 'main_menu'
    dbmenu = [{ 'label': 'Export', 'target': '#', },
              { 'label': 'Import', 'target': '#', },
              ]
    toolsmenu = [{ 'label': 'DB', 'target': '#',
                   'submenu': dbmenu, } 
                  ]
    menu = { 'main': { 'label': 'Main', 'target': '/' },
             'tools': { 'label': 'Tools', 'target': '#',
                        'submenu': toolsmenu, }
             }
    active = ['main', 'tools']
                    
                    
                
