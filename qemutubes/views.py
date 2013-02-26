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
    Net,
    VDE,
    )

class ViewClass(object):
    """ Base class for views """
    # Entity we map
    entity = None
    # List of properties on Entity we care about
    enum_props = None

    def __init__(self, request):
        self.request = request

    def get_slice(self):
        """ Determine slice, offset, sort order and column for grid from request
        returns: (count, offset, order, sortcol)
        """
        #FIXME: Assume jqgrid for now. Add heuristic later for other clients
        count = int(self.request.params.get('rows', 0))
        offset = (int(self.request.params.get('page', 0))-1) * count
        order = self.request.params.get('sord', None)
        sortcol = self.request.params.get('sidx', None)
        return (count, offset, order, sortcol)
        
    def grid(self, filter=None):
        if not self.entity:
            return []
        (count, offset, order, sortcol) = self.get_slice()
        if sortcol and sortcol not in self.enum_props:
            raise Exception('Sort requested on irrelevant column %s' % sortcol)
        sort_sql = True if sortcol in self.entity.__mapper__.columns else False
        total_rows = self.entity.query.count()
        total_pages = total_rows / count if count else 1
        rows = self.entity.query
        if filter:
            rows.filter(filter)
        if sort_sql and sortcol:
            rows = rows.order_by(sortcol+' '+order)
        if count:
            rows = rows.limit(count)
        if offset:
            rows = rows.offset(offset)
        rows = rows.all()
        elist = [{'id': entity.id, 
                  'cell': [getattr(entity, prop) for prop in self.enum_props]
                  } for entity in rows]
        if not sort_sql and sortcol:
            # Do the sort in python, so we can sort on non-ORM columns
            reverse = False if order == 'asc' else True
            elist.sort(key=lambda x: x['cell'][self.enum_props.index(sortcol)],
                       reverse=reverse)
        print "###$$$### HERE"
        return {'total': total_pages, 'page': offset, 'records': len(elist),
                'rows': elist}
                
            
class Main(ViewClass):

    @view_config(route_name='main', 
                 renderer='templates/mac_grid.genshi')
    def grid(self):
        """ View grid of Machines """
        # Replace this with more flexible, non-sqla type?
        mwidget = qemutubes.widgets.MachineGrid.req()
        vwidget = qemutubes.widgets.VDEGrid.req()
        tw2.core.register_controller(mwidget, 'db_jqgrid')
        vwidget.options['url'] = '/json/vdegrid'
        return {'machinegrid': mwidget, 'vdegrid': vwidget}


class MachineView(ViewClass):
    entity = Machine
    enum_props = ['name', 'cpu', 'machtype', 'mem', 'vncport',
                  'conport', 'use_net', 'running']

    @view_config(route_name='machine_grid', renderer='json')
    def grid(self):
        return super(MachineView, self).grid()

    @view_config(route_name='machine_edit', renderer='templates/edit.genshi')
    def edit(self):
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
                #FIXME: Catch constraint violations here
                qemutubes.widgets.MachineForm.insert_or_update(data)
                url = self.request.route_url('main') 
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}

    @view_config(route_name='machine_delete')
    def delete(self):
        """ Delete a Machine instance.
        Requires request.params['id'] point to a valid Machine id
        """
        DBSession.query(Machine).filter(
            Machine.id==self.request.params['id']).delete()
        return Response("Ok")


    @view_config(route_name='machine_view', 
                 renderer='templates/machine_view.genshi')
    def view(self):
        """ View Drive and Net* grids for an individual Machine
        Requires request.params['id'] points to a valid Machine id
        """
#        m = DBSession.query(Machine).filter(
#            Machine.id==self.request.params['id']).first()
        m = Machine.query.filter(Machine.id==self.request.params['id']).first()
        m.configure(self.request.registry.settings)
        dwidget = qemutubes.widgets.DriveGrid.req()
        dwidget.options['url'] = '/json/drivegrid?mac_id=%d' % m.id
        nwidget = qemutubes.widgets.NetGrid.req()
        nwidget.options['url'] = '/json/netgrid?mac_id=%d' % m.id
        return {'drivegrid': dwidget, 'netgrid': nwidget, 'machine': m,
                'cmdline': m.cmdline.replace('  ',' \\\n')}

    @view_config(route_name='machine_launch') 
    def launch(self):
        """ Launch machine
        Requires request.params['id'] points to a valid Machine id
        """
        mid = self.request.params['id']
        m = Machine.query.filter(Machine.id==mid).first()
        (retcode, output) = m.launch()
        if retcode != 0:
            self.request.session.flash('Launch failed: '+output)
        return HTTPFound(location='/')
        
class DriveView(ViewClass):
    """ Methods and views to manipulate a Drive model """
    entity = Drive
    enum_props= ['filepath', 'interface', 'media', 'bus', 'unit', 'ind',
                 'snapshot', 'cache', 'aio', 'ser']

    @view_config(route_name='drive_grid', renderer='json')
    def grid(self):
        """ Return JSON data for widget.DriveGrid request 
        Requires request.params['mac-id'] points to a valid Machine id
        """
        mac = self.request.params.get('mac_id', None)
        if mac == None:
            return []
        return super(DriveView, self).grid(
            filter=Drive.query.filter(Drive.id==mac))

    @view_config(route_name='drive_edit', renderer='templates/edit.genshi')
    def edit(self):
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
                widget.child.c.machine_id.value = mid
        elif self.request.method == 'POST':
            # Assume post is an edit coming in. Validate and store it.
            try:
                data = qemutubes.widgets.DriveForm.validate(
                    self.request.POST)
                #FIXME: Catch constraint violations here
                qemutubes.widgets.DriveForm.insert_or_update(data)
                url = self.request.route_url('machine_view')
                url += '?id=%s'%str(mid) # Better method for this?
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}

    @view_config(route_name='drive_delete')
    def delete(self):
        """ Delete a Drive instance.
        Requires request.params['id'] point to a valid Drive id
        """
        Drive.query.filter(Drive.id==self.request.params['id']).delete()
        return Response("Ok")

class NetView(ViewClass):
    """ Methods and views to manipulate a Net model """
    entity = Net
    enum_props = ['ntype', 'name', 'vlan', 'nicmodel', 'macaddr',
                  'vde_name', 'port', 'ifname']

    @view_config(route_name='net_grid', renderer='json')
    def grid(self):
        """ Return JSON data for widget.NetGrid request 
        Requires request.params['mac-id'] points to a valid Machine id
        """
        mac = self.request.params.get('mac_id', None)
        if mac == None:
            return []
        return super(NetView, self).grid(filter=Net.query.filter(Net.id==mac))

    @view_config(route_name='net_edit', renderer='templates/edit.genshi')
    def edit(self):
        """ Begin editing a new Net unit, or validate and store an edit """
        # We should either have a machine_id or a net_id coming in here
        nid = self.request.params.get('id', None)
        mid = self.request.params.get('machine_id', None)
        if not mid:
            # Get machine_if from the nic we're editing
            n = DBSession.query(Net).filter(Net.id == nid).first()
            mid = n.machine_id
        if self.request.method == 'GET':
            # Assume GET is a request to begin editing
            widget = qemutubes.widgets.NetForm.req()
            if nid:
                widget.fetch_data(self.request)
            else:
                widget.child.c.machine_id.value = mid
        elif self.request.method == 'POST':
            # Assume post is an edit coming in. Validate and store it.
            try:
                data = qemutubes.widgets.NetForm.validate(
                    self.request.POST)
                #FIXME: Catch constraint violations here
                qemutubes.widgets.NetForm.insert_or_update(data)
                url = self.request.route_url('machine_view')
                url += '?id=%s'%str(mid) # Better method for this?
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}

    @view_config(route_name='net_delete')
    def delete(self):
        """ Delete a Net instance.
        Requires request.params['id'] point to a valid Net id
        """
        Net.query.filter(Net.id==self.request.params['id']).delete()
        return Response("Ok")

class VDEView(ViewClass):
    """ Methods and views to manipulate a VDE model """
    entity = VDE
    enum_props = ['name', 'sock', 'mgmt', 'tap', 'mode', 'group',
                  'rcfile', 'ports', 'hub', 'fstp', 'macaddr',
                  'running']
    @view_config(route_name='vde_grid', renderer='json')
    def grid(self):
        """ Return JSON data for widget.VDEGrid request 
        """
        return super(VDEView, self).grid()
        '''
        vdes = DBSession.query(VDE).all()
        vlist = [{ 'id': x.id, 'cell': [x.name, x.sock, x.mgmt,
                x.tap, x.mode, x.group, x.rcfile, x.ports,
                x.hub, x.fstp, x.macaddr, x.running]} for x in vdes]
        res = { 'total': 1, 'page': 1, 'records': len(vlist), 
                'rows': vlist,}
        return res
        '''
    @view_config(route_name='vde_edit', renderer='templates/edit.genshi')
    def edit(self):
        """ Begin editing a VDE or validate and store an edit
        Set request.params['id'] if submitting data for an update.
        """
        vid = self.request.params.get('id', None)
        if self.request.method == 'GET':
            widget = qemutubes.widgets.VDEForm.req()
            if vid:
                widget.fetch_data(self.request)
        elif self.request.method == 'POST':
            try:
                data = qemutubes.widgets.VDEForm.validate(
                    self.request.POST)
                #FIXME: Catch constraint violations here
                qemutubes.widgets.VDEForm.insert_or_update(data)
                url = self.request.route_url('main') 
                return HTTPFound(location=url)
            except tw2.core.ValidationError, e:
                widget = e.widget.req()
        return {'form': widget}

    @view_config(route_name='vde_delete')
    def delete(self):
        """ Delete a VDE instance.
        Requires request.params['id'] point to a valid VDE id
        """
        VDE.query.filter(VDE.id==self.request.params['id']).delete()
        return Response("Ok")

    @view_config(route_name='switch_launch') 
    def launch(self):
        """ Launch switch
        Requires request.params['id'] points to a valid VDE id
        """
        vid = self.request.params['id']
        v = VDE.query.filter(VDE.id==vid).first()
        (retcode, output) = v.launch()
        if retcode != 0:
            self.request.session.flash('Launch failed: '+output)
        return HTTPFound(location='/')

