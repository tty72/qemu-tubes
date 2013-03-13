import tw2.core as twc
import base
import os

class DDMenu(twc.Widget):
    """ Create a jquery drop-down menu.
        menu entries: {label: 'Label String',
                       target: 'HREF value',
                       attrs: { optional dictionary of attributes },
                       submenu { Optional sub entry }
    """
    resources = [base.ddmenu_js, base.ddmenu_css]
    menu = twc.Param('Deep dictionary of menu entries')
    active = twc.Param('List of top level menus to display')
    # FIXME: There has to be a better way...?
    template = 'genshi:%s' % os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'templates/ddmenu.html')
    
