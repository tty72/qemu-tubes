import tw2.core
import tw2.forms
import tw2.sqla
import tw2.jqplugins.jqgrid
from .. import models as model
from . import DBForm

def list_vdes():
    return [(vde.id, vde.name) for vde in model.VDE.query.all()]

def list_nictypes():
    return [nic.ntype for nic in  model.NICType.query.all()]

class NetGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'net_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/netedit?machine_id=' + GetNetMac()}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/netedit?id=' + row_id }"),
                      'deltitle': 'Delete net',
                      'edittitle': 'Edit net',
                      'addtitle': 'Add net',
                      }
    options = {
        'pager': 'module-net-demo_pager',
        'url': '/json/netgrid',
        'datatype': 'json',
        'mtype': 'GET',
        'caption': 'Net Interfaces',
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 898,
        'height': 'auto',
        'colNames': ['Type', 'Name', 'VLan', 'NIC Model', 'MacAddr', 'VDE', 
                    'VDE Port', 'Tap Iface',],
        'colModel': [
            { 'name': 'type', 'index': 'ntype', },
            { 'name': 'name', 'index': 'name', 'width': '100', 'align': 'center', },
            { 'name': 'vlan', 'width': '80', 'align': 'center', },
            { 'name': 'nicmodel', 'width': '60', 'align': 'center', },
            { 'name': 'macaddr', 'width': '60', 'align': 'center', },
            { 'name': 'vde', 'index': 'vde_name', 'width': '60', 'align': 'center', },
            { 'name': 'port', 'width': '80', 'align': 'center', },
            { 'name': 'ifname', 'width': '80', 'align': 'center', },
            ]
                    
    }
    prmDel = {'url': '/netdelete'}
    def prepare(self):
        super(NetGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function GetNetMac() { return $('#%s').jqGrid('getGridParam', 'userData'); }""" %self.selector)
        self.resources.append(edmac)

class NetForm(tw2.forms.TableForm, DBForm):
    entity = model.Net
    id = tw2.forms.HiddenField(validator=tw2.core.IntValidator)
    machine_id = tw2.forms.HiddenField(validator=tw2.core.IntValidator)
    name = tw2.forms.TextField(validator=tw2.core.Required)
    ntype = tw2.forms.SingleSelectField(
        options=model.NET_TYPES,
        validator=tw2.core.Required)
    vlan = tw2.forms.TextField(validator=tw2.core.IntValidator)
    nicmodel = tw2.forms.SingleSelectField(options=list_nictypes())
    macaddr = tw2.forms.TextField()
    vde_id = tw2.forms.SingleSelectField(options=list_vdes())
    port = tw2.forms.TextField(validator=tw2.core.IntValidator)
    script = tw2.forms.TextField()
    downscript = tw2.forms.TextField()
    ifname = tw2.forms.TextField()
    action = '/netedit'

    def prepare(self):
        super(NetForm, self).prepare()
        self.child.c.vde_id.options = list_vdes()
        self.child.c.nicmodel.options = list_nictypes()
