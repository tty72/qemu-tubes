import tw2.core
import tw2.forms
import tw2.sqla
import tw2.jqplugins.jqgrid
import qemutubes.models as model
import sqlalchemy as sa
from tw2.sqla import utils as sautil

def list_vdes():
    return [vde.name for vde in model.VDE.query.all()]

def list_cputypes():
    return [cpu.ctype for cpu in model.CPUType.query.all()]

def list_machinetypes():
    return [machine.mtype for machine in model.MachineType.query.all()]

def list_nictypes():
    return [nic.ntype for nic in  model.NICType.query.all()]

class DBForm(object):
    """ Base class for DB related form widgets
    Provides helper methods for fetching and storing data to a model
    """
    def fetch_data(self, req):
        """ Load form values from given Model (entity) given appropriate 
            Primary keys.
            Copied from tw2.sqla.DbFormPage class
        """
        data = req.GET.mixed()
        filter = dict((col.name, data.get(col.name))
                        for col in sa.orm.class_mapper(self.entity).primary_key)
        self.value = req.GET and self.entity.query.filter_by(**filter).first() or None

    @classmethod
    def insert_or_update(cls, data):
        """ Wrapper for tw2.sqla.utils update_or_create() """
        sautil.update_or_create(cls.entity, data)

class MachineGrid(tw2.jqplugins.jqgrid.SQLAjqGridWidget):
    id = 'machine_grid'
    entity = model.Machine
    #FIXME: Including Nets and Drives breaks SQLAjqGridWidget
    excluded_columns = ['id', 'drives', 'nets',]
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/machineedit'}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/machineedit?id=' + row_id}"),
                      }
    options = {
        'pager': 'module-machine-demo_pager',
        'url': '/tw2_controllers/db_jqgrid/',
        'caption': 'Machines',
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 900,
        'height': 'auto',
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
        ]
    prmDel = {'url': '/machinedelete'}

    def prepare(self):
        super(MachineGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function ViewMachine() { var row=$('#%s').jqGrid('getGridParam', 'selrow');; 
                                         window.location='/machineview?id=' + row }""" %self.selector)
        self.resources.append(edmac)

class DriveGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'drive_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/driveedit?machine_id=' + GetMac()}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/driveedit?id=' + row_id }"),
                      }
    options = {
        'pager': 'module-drive-demo_pager',
        'url': '/json/drivegrid',
        'datatype': 'json',
        'mtype': 'GET',
        'caption': 'Drives',
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 900,
        'height': 'auto',
        'colNames': ['Filepath', 'Interface', 'Media', 'Bus', 'Unit', 'Index', 
                    'Snapshot', 'Cache', 'AIO', 'Serial'],
        'colModel': [
            { 'name': 'filepath', 'index': 'filepath', },
            { 'name': 'interface', 'index': 'interface', 'width': '100', 'align': 'center', },
            { 'name': 'media', 'width': '80', 'align': 'center', },
            { 'name': 'bus', 'width': '60', 'align': 'center', },
            { 'name': 'unit', 'width': '60', 'align': 'center', },
            { 'name': 'ind', 'width': '60', 'align': 'center', },
            { 'name': 'snapshot', 'width': '80', 'align': 'center', },
            { 'name': 'cache', 'width': '80', 'align': 'center', },
            { 'name': 'aio', 'width': '80', 'align': 'center', },
            { 'name': 'ser' },
            ]
                    
    }
    prmDel = {'url': '/drivedelete'}
    def prepare(self):
        super(DriveGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function GetMac() { return $('#%s').jqGrid('getGridParam', 'userData'); }""" %self.selector)
        self.resources.append(edmac)

class NetGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'net_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/netedit?machine_id=' + GetMac()}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/netedit?id=' + row_id }"),
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
        'width': 900,
        'height': 'auto',
        'colNames': ['Type', 'Name', 'VLan', 'NIC Model', 'MacAddr', 'VDE', 
                    'VDE Port', 'Tap Iface',],
        'colModel': [
            { 'name': 'type', 'index': 'filepath', },
            { 'name': 'name', 'index': 'interface', 'width': '100', 'align': 'center', },
            { 'name': 'vlan', 'width': '80', 'align': 'center', },
            { 'name': 'nicmodel', 'width': '60', 'align': 'center', },
            { 'name': 'macaddr', 'width': '60', 'align': 'center', },
            { 'name': 'vde', 'width': '60', 'align': 'center', },
            { 'name': 'port', 'width': '80', 'align': 'center', },
            { 'name': 'ifname', 'width': '80', 'align': 'center', },
            ]
                    
    }
    prmDel = {'url': '/netdelete'}
    def prepare(self):
        super(NetGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function GetMac() { return $('#%s').jqGrid('getGridParam', 'userData'); }""" %self.selector)
        self.resources.append(edmac)

class VDEGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'vde_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/vdeedit'}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/vdeedit?id=' + row_id }"),
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
        'width': 900,
        'height': 'auto',
        'colNames': ['Name', 'Socket', 'Management', 'Tap', 'Perms', 'Group', 
                    'RC File', 'Ports', 'Hub', 'FSTP', 'MacAddr'],
        'colModel': [
            { 'name': 'name', 'index': 'filepath', },
            { 'name': 'sock', 'index': 'interface', 'width': '100', 'align': 'center', },
            { 'name': 'mgmt', 'width': '80', 'align': 'center', },
            { 'name': 'tap', 'width': '60', 'align': 'center', },
            { 'name': 'mode', 'width': '60', 'align': 'center', },
            { 'name': 'group', 'width': '60', 'align': 'center', },
            { 'name': 'rcfile', 'width': '80', 'align': 'center', },
            { 'name': 'ports', 'width': '80', 'align': 'center', },
            { 'name': 'hub', 'width': '80', 'align': 'center', },
            { 'name': 'fstp', 'width': '80', 'align': 'center', },
            { 'name': 'macaddr', 'width': '80', 'align': 'center', },
            ]
                    
    }
    prmDel = {'url': '/vdedelete'}

class MachineForm(tw2.forms.TableForm, DBForm):
    entity = model.Machine
    id = tw2.forms.HiddenField()
    name = tw2.forms.TextField(validator=tw2.core.Required)
    mem = tw2.forms.TextField()
    vncport = tw2.forms.TextField(validator=tw2.core.IntValidator)
    conport = tw2.forms.TextField(validator=tw2.core.IntValidator)
    netnone = tw2.forms.CheckBox()
    cpu = tw2.forms.SingleSelectField(options=list_cputypes())
    machtype = tw2.forms.SingleSelectField(options=list_machinetypes())
    action = '/machineedit' 

    def prepare(self):
        super(MachineForm, self).prepare()
        self.child.c.cpu.options = list_cputypes()
        self.child.c.machtype.options = list_machinetypes()


class DriveForm(tw2.forms.TableForm, DBForm):
    entity = model.Drive
    id = tw2.forms.HiddenField()
    machine_id = tw2.forms.HiddenField()
    filepath = tw2.forms.TextField(validator=tw2.core.Required)
    interface = tw2.forms.SingleSelectField(
        options=model.DRIVE_IFS, value=model.DRIVE_IFS[0])
    media = tw2.forms.SingleSelectField(options=model.MEDIA, 
                                        value=model.MEDIA[0],
                                        validator=tw2.core.Required)
    bus = tw2.forms.TextField(validator=tw2.core.IntValidator)
    unit = tw2.forms.TextField(validator=tw2.core.IntValidator)
    ind = tw2.forms.TextField(validator=tw2.core.IntValidator(min=0, 
                                                              max=3))
    cyls = tw2.forms.TextField(validator=tw2.core.IntValidator)
    heads = tw2.forms.TextField(validator=tw2.core.IntValidator)
    secs = tw2.forms.TextField(validator=tw2.core.IntValidator)
    trans = tw2.forms.TextField(validator=tw2.core.IntValidator)
    snapshot = tw2.forms.CheckBox()
    cache = tw2.forms.SingleSelectField(
        options=model.CACHE_TYPES, value=model.CACHE_TYPES[0])
    aio = tw2.forms.SingleSelectField(
        options=model.AIO_TYPES, value=model.AIO_TYPES[0])
    ser = tw2.forms.TextField()
    action = '/driveedit'

class NetForm(tw2.forms.TableForm, DBForm):
    entity = model.Net
    id = tw2.forms.HiddenField()
    machine_id = tw2.forms.HiddenField()
    name = tw2.forms.TextField(validator=tw2.core.Required)
    ntype = tw2.forms.SingleSelectField(
        options=model.NET_TYPES,
        validator=tw2.core.Required)
    vlan = tw2.forms.TextField(validator=tw2.core.IntValidator)
    nicmodel = tw2.forms.SingleSelectField(options=list_nictypes())
    macaddr = tw2.forms.TextField()
    vde = tw2.forms.SingleSelectField(options=list_vdes())
    port = tw2.forms.TextField(validator=tw2.core.IntValidator)
    script = tw2.forms.TextField()
    downscript = tw2.forms.TextField()
    ifname = tw2.forms.TextField()
    action = '/netedit'

    def prepare(self):
        super(NetForm, self).prepare()
        self.child.c.vde.options = list_vdes()
        self.child.c.nicmodel.options = list_nictypes()

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

