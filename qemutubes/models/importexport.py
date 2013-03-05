from qemutubes.models import __version__ as dbversion
from xml.dom import minidom
import StringIO

class Exchange(object):
    def __init__(self, Base):
        self.tables = Base.metadata.sorted_tables        

    def export(self):
        self.doc = minidom.Document()
        root = self.doc.createElement('qtubesexport')
        root.setAttribute('version', dbversion)
        self.doc.appendChild(root)
        for t in self.tables:
            print dir(t)
            e = self.doc.createElement(t.name)
            root.appendChild(e)
            self.export_table(e, t)

    def export_table(self, parent, table):
        engine = table.metadata.bind
        res = engine.execute(table.select()).fetchall()
        for row in res:
            for (col, val) in row.items():
                e = self.doc.createElement(col)
                if val is None:
                    e.setAttribute('none', 'none')
                elif val is True or val is False:
                    e.setAttribute('bool', str(val).lower())
                else:
                    v = self.doc.createTextNode(str(val))
                    e.appendChild(v)
                parent.appendChild(e)

    def write(self, fd, **kw):
        if type(fd) is not file:
            fd = open(fd, 'w')
        self.doc.writexml(fd, **kw)

##########################################
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
            (name, data) = self.parse_machine(m)
            self.machines[name] = data

    def parse_vde(self, vde):
        saved_cols = ['sock', 'mgmt', 'tap', 'mode', 'group',
                      'rcfile', 'ports', 'hub', 'fstp', 'macaddr']
        name = vde.attributes['name'].value
        data = self.parse_cols(vde, saved_cols)
        return (name, data)

    def parse_machine(self, machine):
        saved_cols = ['cpu', 'machtype', 'mem', 'vncport',
                      'conport', 'netnone']
        name = machine.attributes['name'].value
        data = self.parse_cols(machine, saved_cols)
        data['drives']=[]
        data['nets']=[]
        drives = machine.getElementsByTagName('drive')
        for drive in drives:
            data['drives'].append(self.parse_drive(drive))
        nets = machine.getElementsByTagName('net')
        for net in nets:
            data['nets'].append(self.parse_net(net))
        return (name, data)

    def parse_drive(self, drive):
        saved_cols = ['filepath', 'interface', 'media', 'bus', 'unit', 'ind',
                      'cyls', 'heads', 'secs', 'trans', 'snapshot', 'cache',
                      'aio', 'ser']
        return self.parse_cols(drive, saved_cols)

    def parse_net(self, net):
        saved_cols = ['ntype', 'vlan', 'nicmodel', 'macaddr',
                      'port', 'script', 'downscript', 'ifname']
        print net.tagName
        name = net.attributes['name'].value
        data = self.parse_cols(net, saved_cols)
        data['name'] = name
        return data

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
