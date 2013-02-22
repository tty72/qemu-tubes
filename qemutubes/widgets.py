import tw2.core
import tw2.forms
import tw2.sqla
import tw2.jqplugins.jqgrid
import qemutubes.models as model

class MachineGrid(tw2.jqplugins.jqgrid.SQLAjqGridWidget):
    id = 'machine_grid'
    entity = model.Machine
    excluded_columns = ['id', 'drives', 'net_nics', 'net_vdes', 'net_taps',]
    #edmachine = tw2.core.js_callback(""""function(){ var grid=$('#%s'); alert(grid.jqGrid('getGridParam', 'selarrrow')); }""" % id)
#    prmFilter = {'stringResult': True, 'searchOnEnter': False}
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/machineedit'}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/machineedit?id=' + row_id}"),
                      }
    options = {
        'pager': 'module-0-demo_pager',
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
        'pager': 'module-0-demo_pager',
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
    #prmDel = {'url': '/machinedelete'}
    def prepare(self):
        super(DriveGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function GetMac() { return $('#%s').jqGrid('getGridParam', 'userData'); }""" %self.selector)
        self.resources.append(edmac)



class MachineForm(tw2.sqla.DbFormPage):
    title = 'Machine'
    entity = model.Machine
    redirect = '/'

    class child(tw2.forms.TableForm):
        id = tw2.forms.HiddenField()
        name = tw2.forms.TextField(validator=tw2.core.Required)
        mem = tw2.forms.TextField()
        vncport = tw2.forms.TextField(validator=tw2.core.IntValidator)
        conport = tw2.forms.TextField(validator=tw2.core.IntValidator)
        netnone = tw2.forms.CheckBox()
        cpu = tw2.sqla.DbSingleSelectField(entity=model.CPUType)
        machtype = tw2.sqla.DbSingleSelectField(entity=model.MachineType)
        #FIXME: Pull prefix for action URL from config controller_prefix
        action = '/tw2_controllers/machine_submit' 


class DriveForm(tw2.sqla.DbFormPage):
    title = 'Drive'
    entity = model.Drive
    #redirect = '/machineview'
    
    class child(tw2.forms.TableForm):
        id = tw2.forms.HiddenField()
        machine_id = tw2.forms.HiddenField()
        filepath = tw2.forms.TextField(validator=tw2.core.Required)
        interface = tw2.forms.SingleSelectField(options=model.DRIVE_IFS, value=model.DRIVE_IFS[0])
        media = tw2.forms.SingleSelectField(options=model.MEDIA, value=model.MEDIA[0],
                                            validator=tw2.core.Required)
        bus = tw2.forms.TextField(validator=tw2.core.IntValidator)
        unit = tw2.forms.TextField(validator=tw2.core.IntValidator)
        ind = tw2.forms.TextField(validator=tw2.core.IntValidator(min=0, max=3))
        cyls = tw2.forms.TextField(validator=tw2.core.IntValidator)
        heads = tw2.forms.TextField(validator=tw2.core.IntValidator)
        secs = tw2.forms.TextField(validator=tw2.core.IntValidator)
        trans = tw2.forms.TextField(validator=tw2.core.IntValidator)
        snapshot = tw2.forms.CheckBox()
        cache = tw2.forms.SingleSelectField(options=model.CACHE_TYPES, value=model.CACHE_TYPES[0])
        aio = tw2.forms.SingleSelectField(options=model.AIO_TYPES, value=model.AIO_TYPES[0])
        ser = tw2.forms.TextField()
        #FIXME: Pull prefix for action URL from config controller_prefix
        action = '/tw2_controllers/drive_submit'

class NetGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'net_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/netedit?machine_id=' + GetMac()}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/netedit?id=' + row_id }"),
                      }
    options = {
        'pager': 'module-0-demo_pager',
        'url': '/json/netgrid',
        'datatype': 'json',
        'mtype': 'GET',
        'caption': 'Nets',
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
    #prmDel = {'url': '/machinedelete'}
    def prepare(self):
        super(DriveGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function GetMac() { return $('#%s').jqGrid('getGridParam', 'userData'); }""" %self.selector)
        self.resources.append(edmac)
