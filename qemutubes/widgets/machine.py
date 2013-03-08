import tw2.core
import tw2.forms
import tw2.sqla
import tw2.jqplugins.jqgrid
from .. import models as model
from . import DBForm

def list_cputypes():
    return [cpu.ctype for cpu in model.CPUType.query.all()]

def list_machinetypes():
    return [machine.mtype for machine in model.MachineType.query.all()]

class MachineGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'machine_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/machineedit'}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/machineedit?id=' + row_id}"),
                      'deltitle': 'Delete machine',
                      'edittitle': 'Edit machine',
                      'addtitle': 'Add machine',
                      }
    options = {
        'pager': 'module-machine-demo_pager',
        'url': '/json/machinegrid',
        'datatype': 'json',
        'mtype': 'GET',
        'caption': 'Machines',
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 898,
        'height': 'auto',
        'colNames': ['Name', 'CPU', 'Type', 'Memory', 'VNC Port', 'Network', 'Active'],
        'colModel': [
            { 'name': 'name', 'index': 'name', },
            { 'name': 'cpu', 'index': 'cpu', 'width': '100', 'align': 'center', },
            { 'name': 'machtype', 'width': '80', 'align': 'center', },
            { 'name': 'mem', 'width': '60', 'align': 'center', },
            { 'name': 'vncport', 'width': '60', 'align': 'center', 'formatter': 'showlink',
              'formatoptions': {'baseLinkUrl': '/machinevnc'}, },
            { 'name': 'netnone', 'width': '80', 'align': 'center', 
              'formatter': 'checkbox', },
            { 'name': 'running', 'width': '80', 'align': 'center',
              'formatter': 'checkbox', },
            ],        
    }
    custom_pager_buttons = [
        {
            'caption': '',
            'buttonicon': 'ui-icon-gear',
            'onClickButton': tw2.core.js_callback("ViewMachine"),
            'position': 'last',
            'title': 'Configure',
            'cursor': 'pointer'
        },
        {
            'caption': '',
            'buttonicon': 'ui-icon-stop',
            'onClickButton': tw2.core.js_callback("PDMachine"),
            'position': 'last',
            'title': 'Power Down',
            'cursor': 'pointer'
        },
        {
            'caption': '',
            'buttonicon': 'ui-icon-play',
            'onClickButton': tw2.core.js_callback("LaunchMachine"),
            'position': 'last',
            'title': 'Launch',
            'cursor': 'pointer'
        },
        {
            'caption': '',
            'buttonicon': 'ui-icon-closethick',
            'onClickButton': tw2.core.js_callback("KillMachine"),
            'position': 'last',
            'title': 'Kill Machine',
            'cursor': 'pointer'
        },
        ]
    prmDel = {'url': '/machinedelete',}
    
    def prepare(self):
        super(MachineGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function ViewMachine() { var row=$('#%s').jqGrid('getGridParam', 'selrow');; 
                                         window.location='/machineview?id=' + row }""" %self.selector)
        launchmac = tw2.core.JSSource(location='head',
                                      src="""function LaunchMachine() { var row=$('#%s').jqGrid('getGridParam', 'selrow');; 
                                         window.location='/machinelaunch?id=' + row }""" %self.selector)
        stopmac = tw2.core.JSSource(location='head',
                                    src="""function PDMachine() { var row=$('#%s').jqGrid('getGridParam', 'selrow');; 
                                         window.location='/machinepowerdown?id=' + row }""" %self.selector)
        killmac = tw2.core.JSSource(location='head',
                                    src="""function KillMachine() { var row=$('#%s').jqGrid('getGridParam', 'selrow');; 
                                         window.location='/machinekill?id=' + row }""" %self.selector)
        self.resources.append(edmac)
        self.resources.append(launchmac)
        self.resources.append(stopmac)
        self.resources.append(killmac)

class MachineForm(tw2.forms.TableForm, DBForm):
    entity = model.Machine
    id = tw2.forms.HiddenField()
    name = tw2.forms.TextField(validator=tw2.core.Required)
    mem = tw2.forms.TextField()
    vncport = tw2.forms.TextField(validator=tw2.core.IntValidator)
    netnone = tw2.forms.CheckBox()
    cpu = tw2.forms.SingleSelectField(options=list_cputypes())
    machtype = tw2.forms.SingleSelectField(options=list_machinetypes())
    action = '/machineedit' 

    def prepare(self):
        super(MachineForm, self).prepare()
        self.child.c.cpu.options = list_cputypes()
        self.child.c.machtype.options = list_machinetypes()

