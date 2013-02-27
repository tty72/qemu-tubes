from qemutubes.models import Machine, Drive, Net, VDE
from xml.dom import minidom

class Exporter(object):
    """ DB to XML export class """
    version = '1.0'
    
    def __init__(self):
        self.grow_tree()

    def grow_tree(self):
        self.doc = minidom.Document()
        self.root = self.doc.createElement('qtubesdump')
        self.root.setAttribute('version', self.version)
        self.doc.appendChild(self.root)
        self.graft_machines()
        
    def graft_machines(self):
        """ Iterate over all machines in DB and graft to document root """
        saved_cols = ['name', 'cpu', 'machtype', 'mem', 'vncport',
                      'conport', 'netnone']
        machines = Machine.query.all()
        for m in machines:
            mt = self.doc.createElement('machine')
            mt.setAttribute('id', str(m.id))
            self.graft_items([(c,c) for c in saved_cols],
                             mt, m)
            for drive in m.drives:
                self.graft_drive(mt, m.id)
            for net in m.nets:
                self.graft_net(mt, m.id)
            self.root.appendChild(mt)

    def graft_drive(self, mt, mid):
        saved_cols = ['filepath', 'interface', 'media', 'bus', 'unit', 'ind',
                      'cyls', 'heads', 'secs', 'trans', 'snapshot', 'cache',
                      'aio', 'ser']
        drives = Drive.query.filter(Drive.machine_id == mid).all()
        for d in drives:
            dt = self.doc.createElement('drive')
            dt.setAttribute('id', str(d.id))
            self.graft_items([(c,c) for c in saved_cols],
                             dt, d)
            mt.appendChild(dt)
            
    def graft_net(self, mt, mid):
        saved_cols = ['ntype', 'vlan', 'name', 'nicmodel', 'macaddr',
                      'port', 'script', 'downscript', 'ifname']
        nets = Net.query.filter(Net.machine_id == mid).all()
        for n in nets:
            nt = self.doc.createElement('net')
            nt.setAttribute('id', str(n.id))
            self.graft_items([(c,c) for c in saved_cols],
                             nt, n)
            ct = self.doc.createElement('vde')
            if n.vde_name:
                t = self.doc.createTextNode(n.vde_name)
                ct.appendChild(t)
            nt.appendChild(ct)
            mt.appendChild(nt)

    def graft_items(self, ilist, element, ob):
        """ Graft attributes from object into tree at element
        ilist - List of tuples (attribute name, tag name) to graft
        ob - Ojbect from which to graft
        element - Document element at which to graft
           e.g. graft_items([('name', 'nametag'), ('someval', 'tag')],
                            el, ob)
           Values of None generate an empty tag
        """
        for c in ilist:
            ct = self.doc.createElement(c[1])
            v = getattr(ob, c[0])
            if v is not None:
                t = self.doc.createTextNode(str(v))
                ct.appendChild(t)
            element.appendChild(ct)
            
    def write(self, fd):
        f=open(fd,'w')
        self.doc.writexml(f,indent='', newl='\n', addindent='   ')
