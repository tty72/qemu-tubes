import tw2.core
import tw2.forms
import tw2.sqla
import tw2.jqplugins.jqgrid
from .. import models as model
from . import DBForm

class DriveGrid(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'drive_grid'
    pager_options = { "search" : True, "refresh" : True, "add" : True, 
                      "addfunc":tw2.core.js_callback("function(){window.location='/driveedit?machine_id=' + GetDriveMac()}"), 
                      "editfunc":tw2.core.js_callback("function(row_id){location.href='/driveedit?id=' + row_id }"),
                      'deltitle': 'Delete drive',
                      'edittitle': 'Edit drive',
                      'addtitle': 'Add drive',
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
        'width': 898,
        'height': 'auto',
        'colNames': ['Filepath', 'Interface', 'Media', 'Bus', 'Unit', 'Index', 
                    'Snapshot', 'Cache', 'AIO', 'Serial'],
        'colModel': [
            { 'name': 'filepath', 'index': 'filepath', },
            { 'name': 'interface', 'index': 'interface', 'width': '100', 
              'align': 'center', },
            { 'name': 'media', 'width': '80', 'align': 'center', },
            { 'name': 'bus', 'width': '60', 'align': 'center', },
            { 'name': 'unit', 'width': '60', 'align': 'center', },
            { 'name': 'ind', 'width': '60', 'align': 'center', },
            { 'name': 'snapshot', 'width': '80', 'align': 'center', 
              'formatter': 'checkbox', },
            { 'name': 'cache', 'width': '80', 'align': 'center', },
            { 'name': 'aio', 'width': '80', 'align': 'center', },
            { 'name': 'ser' },
            ]
                    
    }
    prmDel = {'url': '/drivedelete'}
    def prepare(self):
        super(DriveGrid, self).prepare()
        edmac = tw2.core.JSSource(location='head',
                                  src="""function GetDriveMac() { return $('#%s').jqGrid('getGridParam', 'userData'); }""" %self.selector)
        self.resources.append(edmac)

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

