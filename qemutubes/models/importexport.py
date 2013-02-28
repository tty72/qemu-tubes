from qemutubes.models import Machine, Drive, Net, VDE
from xml.dom import minidom
import StringIO

class Exporter(object):
    """ DB to XML export class """
    version = '1.0'
    
    def __init__(self, indent='', addindent='', newl=''):
        """ Construct an Exporter object. DB is querried immediately 
        indent, addindent, newl - passed directly to minidom.write()
        """
        self.indent = indent
        self.addindent = addindent
        self.newl = newl
        self.grow_tree()

    def grow_tree(self):
        self.doc = minidom.Document()
        self.root = self.doc.createElement('qtubesdump')
        self.root.setAttribute('version', self.version)
        self.doc.appendChild(self.root)
        self.graft_vdes()
        self.graft_machines()
        
    def graft_vdes(self):
        """ Iterate over all VDEs in DB and graft to document root """
        saved_cols = ['sock', 'mgmt', 'tap', 'mode', 'group',
                      'rcfile', 'ports', 'hub', 'fstp', 'macaddr']
        vdes = VDE.query.all()
        for v in vdes:
            vt = self.doc.createElement('vdeswitch')
            vt.setAttribute('id', str(v.id))
            vt.setAttribute('name', v.name)
            self.graft_items([(c,c) for c in saved_cols],
                             vt, v)
            self.root.appendChild(vt)
        
    def graft_machines(self):
        """ Iterate over all machines in DB and graft to document root """
        saved_cols = ['cpu', 'machtype', 'mem', 'vncport',
                      'conport', 'netnone']
        machines = Machine.query.all()
        for m in machines:
            mt = self.doc.createElement('machine')
            mt.setAttribute('id', str(m.id))
            mt.setAttribute('name', m.name)
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
        saved_cols = ['ntype', 'vlan', 'nicmodel', 'macaddr',
                      'port', 'script', 'downscript', 'ifname']
        nets = Net.query.filter(Net.machine_id == mid).all()
        for n in nets:
            nt = self.doc.createElement('net')
            nt.setAttribute('id', str(n.id))
            nt.setAttribute('name', n.name)
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
            if v or v==0:
                t = self.doc.createTextNode(str(v))
                ct.appendChild(t)
            element.appendChild(ct)
            
    def write(self, fd):
        if type(fd) is not file:
            fd = open(fd, 'w')
        self.doc.writexml(fd,indent='', newl='\n', addindent='   ')

    @property
    def file(self):
        f = StringIO.StringIO()
        self.doc.writexml(f, indent=self.indent, 
                          addindent=self.addindent,
                          newl=self.newl)
        f.seek(0)
        return f


class Importer(object):
    """ XML to DB Importer class """
    def __init__(self, fd):
        if type(fd) is not file:
            fd = open(fd,'r')
        self.doc = minidom.parse(fd)
        self.root = self.doc.documentElement
        if (not self.root.attributes.has_key('version') or
            self.root.tagName != 'qtubesdump'):
            raise Exception('Unknown document type')
        if self.root.attributes['version'].value != Exporter.version:
            raise Exception('Incorrect version: %s' %
                            root.attributes['version'].value)
        self.vdes = {}
        self.machines = {}
        self.parse_xml()

    def parse_xml(self):
        """ Parse DB fields from XML """
        vdeents = self.root.getElementsByTagName('vdeswitch')
        machines = self.root.getElementsByTagName('machine')
        for v in vdeents:
            (name, data) = self.parse_vde(v)
            self.vdes[name] = data
        for m in machines:
            (name, data) = self.parse_machines(m)
            self.machines[name] = data

    def parse_vde(self, vde):
        saved_cols = ['sock', 'mgmt', 'tap', 'mode', 'group',
                      'rcfile', 'ports', 'hub', 'fstp', 'macaddr']
        name = vde.attributes['name'].value
        data = self.parse_cols(vde, saved_cols)
        return (name, data)

    def parse_machines(self, machine):
        saved_cols = ['cpu', 'machtype', 'mem', 'vncport',
                      'conport', 'netnone']
        name = machine.attributes['name'].value
        data = self.parse_cols(machine, saved_cols)
        return (name, data)


    def parse_cols(self, node, cols):
        """ Parse all children of node matching one of cols
        node - parent node to search
        cols - list of node/columns
        returns dict with cols as keys
        """
        ret = {}
        for c in cols:
            ret[c] = self.get_data(node.getElementsByTagName(c)[0])
        return ret

    def get_data(self, node):
        """ Get text data from a node. Whitespace is collapsed between nodes """
        val = []
        ch = node.childNodes
        for n in ch:
            if n.nodeType == n.TEXT_NODE:
              val.append(n.data.strip())
        return ' '.join(val)
