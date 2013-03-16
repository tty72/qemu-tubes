from . import ddmenu
from pyramid.request import Request

class MainMenu(ddmenu.DDMenu):
    id = 'main_menu'
    active = ['main', 'tools']
                    
                    
                
