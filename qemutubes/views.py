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
        """ View grid of Machines """
        # Replace this with more flexible, non-sqla type?
        widget = qemutubes.widgets.MachineGrid.req()
        tw2.core.register_controller(widget, 'db_jqgrid')
        return {'machinegrid': widget}

    @view_config(route_name='machine_edit', renderer='templates/edit.genshi')
    def machine_edit(self):
        """ Begin editing a Machine or validate and store an edit
        Set request.params['id'] if submitting data for an update.
        """
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
        """ Delete a Machine instance.
        Requires request.params['id'] point to a valid Machine id
        """
        DBSession.query(Machine).filter(
            Machine.id==self.request.params['id']).delete()
        return Response("Ok")


    @view_config(route_name='machine_view', 
                 renderer='templates/machine_view.genshi')
    def machine_view(self):
        """ View Drive and Net* grids for an individual Machine
        Requires request.params['id'] points to a valid Machine id
        """
        m = DBSession.query(Machine).filter(
            Machine.id==self.request.params['id']).first()
        dwidget = qemutubes.widgets.DriveGrid.req()
        dwidget.options['url'] = '/json/drivegrid?mac_id=%d' % m.id
        return {'drivegrid': dwidget, 'machine': m}

class DriveView(ViewClass):
    """ Methods and views to manipulate a Drive model """
    @view_config(route_name='drive_edit', renderer='templates/edit.genshi')
    def drive_edit(self):
        """ Begin editing a new Drive unit, or validate and store an edit """
        # We should either have a machine_id or a drive_id coming in here
        did = self.request.params.get('id', None)
        mid = self.request.params.get('machine_id', None)
        if not mid:
            # Get machine_if from the drive we're editing
            d = DBSession.query(Drive).filter(Drive.id == did).first()
            mid = d.machine_id
        if self.request.method == 'GET':
            # Assume GET is a request to begin editing
            widget = qemutubes.widgets.DriveForm.req()
            if did:
                widget.fetch_data(self.request)
            else:
                widget.value = {'machine_id': mid}
        elif self.request.method == 'POST':
            # Assume post is an edit coming in. Validate and store it.
            try:
                data = qemutubes.widgets.DriveForm.validate(
                    self.request.POST)
                #FIXME: Cacth constraint violations here
                qemutubes.widgets.DriveForm.insert_or_update(data)
                url = self.request.route_url('machine_view')
                url += '?id=%s'%str(mid) # Better method for this?
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}

    @view_config(route_name='drive_grid', renderer='json')
    def drive_grid(self):
        """ Return JSON data for widget.DriveGrid request 
        Requires request.params['mac-id'] points to a valid Machine id
        """
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
      
