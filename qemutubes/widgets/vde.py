import tw2.core
import tw2.forms
import tw2.sqla
import tw2.jqplugins.jqgrid
from .. import models as model
from . import DBForm

class VDEGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'vde_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/vdeedit'}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/vdeedit?id=' + row_id }"),
                      'deltitle': 'Delete VDE switch',
                      'edittitle': 'Edit VDE switch',
                      'addtitle': 'Add VDE switch',
                      }
    options = {
        'pager': 'module-vde-demo_pager',
        'url': '/json/vdegrid',
        'datatype': 'json',
        'mtype': 'GET',
        'caption': 'VDE Instances',
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 898,
        'height': 'auto',
        'colNames': ['Name', 'Socket', 'Management', 'Tap', 'Perms', 'Group', 
                    'RC File', 'Ports', 'Hub', 'FSTP', 'MacAddr', 'Active'],
        'colModel': [
            { 'name': 'name', 'index': 'filepath', },
            { 'name': 'sock', 'index': 'interface', 'width': '100', 'align': 'center', },
            { 'name': 'mgmt', 'width': '80', 'align': 'center', },
            { 'name': 'tap', 'width': '60', 'align': 'center', },
            { 'name': 'mode', 'width': '60', 'align': 'center', },
            { 'name': 'group', 'width': '60', 'align': 'center', },
            { 'name': 'rcfile', 'width': '80', 'align': 'center', },
            { 'name': 'ports', 'width': '80', 'align': 'center', },
            { 'name': 'hub', 'width': '80', 'align': 'center', 'formatter': 'checkbox', },
            { 'name': 'fstp', 'width': '80', 'align': 'center', 'formatter': 'checkbox', },
            { 'name': 'macaddr', 'width': '80', 'align': 'center', },
            { 'name': 'running', 'width': '80', 'align': 'center', 'formatter': 'checkbox', },
            ]
                    
    }
    custom_pager_buttons = [
        {
            'caption': '',
            'buttonicon': 'ui-icon-play',
            'onClickButton': tw2.core.js_callback("LaunchSwitch"),
            'position': 'last',
            'title': 'Launch',
            'cursor': 'pointer'
        },
        ]
    
    prmDel = {'url': '/vdedelete'}

    def prepare(self):
        super(VDEGrid, self).prepare()
        launchswitch = tw2.core.JSSource(location='head',
                                         src="""function LaunchSwitch() { var row=$('#%s').jqGrid('getGridParam', 'selrow');; 
                                         window.location='/switchlaunch?id=' + row }""" %self.selector)
        self.resources.append(launchswitch)

class VDEForm(tw2.forms.TableForm, DBForm):
    entity = model.VDE
    id = tw2.forms.HiddenField()
    name = tw2.forms.TextField(validator=tw2.core.Required)
    sock = tw2.forms.TextField(validator=tw2.core.Required)
    mgmt = tw2.forms.TextField(validator=tw2.core.Required)
    group = tw2.forms.TextField()
    rcfile = tw2.forms.TextField()
    ports = tw2.forms.TextField(validator=tw2.core.IntValidator)
    hub = tw2.forms.CheckBox()
    fstp = tw2.forms.CheckBox()
    macaddr = tw2.forms.TextField()
    action = '/vdeedit'

