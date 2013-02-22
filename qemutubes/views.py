from pyramid.response import Response
from pyramid.view import view_config
import qemutubes.widgets
import tw2.core
from sqlalchemy.exc import DBAPIError
from pyramid.httpexceptions import HTTPFound
from .models import (
    DBSession,
    Machine,
    Drive,
    )

class ViewClass(object):
    """ Base class for views """
    def __init__(self, request):
        self.request = request

class MachineView(ViewClass):
    
    @view_config(route_name='machine_grid', 
                 renderer='templates/mac_grid.genshi')
    def machine_grid(self):
        widget = qemutubes.widgets.MachineGrid.req()
        tw2.core.register_controller(widget, 'db_jqgrid')
        return {'machinegrid': widget}

    @view_config(route_name='machine_edit', renderer='templates/edit.genshi')
    def machine_edit(self):
        mid = self.request.params.get('id', None)
        if self.request.method == 'GET':
            widget = qemutubes.widgets.MachineForm.req()
            if mid:
                widget.fetch_data(self.request)
        elif self.request.method == 'POST':
            try:
                data = qemutubes.widgets.MachineForm.validate(
                    self.request.POST)
                #FIXME: Cacth constraint violations here
                qemutubes.widgets.MachineForm.insert_or_update(data)
                url = self.request.route_url('machine_grid') 
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}

    @view_config(route_name='machine_del')
    def machine_del(self):
        DBSession.query(Machine).filter(
            Machine.id==self.request.params['id']).delete()
        #print mac
        #print "#@#@#@ID: ",self.request.params['id']
        return Response("Ok")


    @view_config(route_name='machine_view', 
                 renderer='templates/machine_view.genshi')
    def machine_view(self):
        m = DBSession.query(Machine).filter(
            Machine.id==self.request.params['id']).first()
        dwidget = qemutubes.widgets.DriveGrid.req()
        dwidget.options['url'] = '/json/drivegrid?mac_id=%d' % m.id
        return {'drivegrid': dwidget, 'machine': m}

class DriveView(ViewClass):

    @view_config(route_name='drive_edit', renderer='templates/edit.genshi')
    def drive_edit(self):
        did = self.request.params.get('id', None)
        mid = self.request.params.get('machine_id', None)
        if not mid:
            d = DBSession.query(Drive).filter(Drive.id == did).first()
            mid = d.machine_id
        if self.request.method == 'GET':
            widget = qemutubes.widgets.DriveForm.req()
            if did:
                widget.fetch_data(self.request)
            else:
                widget.value = {'machine_id': mid}
        elif self.request.method == 'POST':
            try:
                data = qemutubes.widgets.DriveForm.validate(
                    self.request.POST)
                #FIXME: Cacth constraint violations here
                qemutubes.widgets.DriveForm.insert_or_update(data)
                url = self.request.route_url('machine_view')
                print "URL#$#$##$#$$#URL: ",url
                url += '?id=%s'%str(mid)
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}
#        widget = qemutubes.widgets.DriveForm(
#            redirect='/machineview?id=%s'%str(macid)).req()
#        widget.fetch_data(self.request)
#        if not widget.value:
#            widget.value = {'machine_id': macid}
#        tw2.core.register_controller(widget, 'drive_submit')
#        return {'form': widget}

    @view_config(route_name='drive_grid', renderer='json')
    def drive_grid(self):
        mac = self.request.params.get('mac_id', None)
        if mac == None:
            return []
        drives = DBSession.query(Drive).filter(Drive.machine_id==mac)
        dlist = [{ 'id': x.id, 'cell': [x.filepath, x.interface, x.media,
                x.bus, x.unit, x.ind,
                x.snapshot, x.cache, x.aio,
                x.ser]} for x in drives]
        res = { 'total': 1, 'page': 1, 'records': len(dlist), 
                'rows': dlist, 'userdata': mac }
        return res
      
