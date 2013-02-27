from qemutubes.models import Machine, Drive, Net, VDE
import xml.etree.ElementTree as ET

class Exporter(object):
    """ DB to XML export class """
    version = '1.0'
    
    def __init__(self):
        self.grow_tree()

    def grow_tree(self):
        self.root = ET.Element('qtubesdump', version=self.version)
        self.graft_machines()
        
    def graft_machines(self):
        """ Iterate over all machines in DB and graft to document root """
        saved_cols = ['name', 'cpu', 'machtype', 'mem', 'vncport',
                      'conport', 'netnone']
        machines = Machine.query.all()
        for m in machines:
            mt = ET.SubElement(self.root, 'machine', id=str(m.id))
            self.graft_items([(c,c) for c in saved_cols],
                             mt, m)
            for drive in m.drives:
                self.graft_drive(mt, m.id)
            for net in m.nets:
                self.graft_net(mt, m.id)

    def graft_drive(self, mt, mid):
        saved_cols = ['filepath', 'interface', 'media', 'bus', 'unit', 'ind',
                      'cyls', 'heads', 'secs', 'trans', 'snapshot', 'cache',
                      'aio', 'ser']
        drives = Drive.query.filter(Drive.machine_id == mid).all()
        for d in drives:
            dt = ET.SubElement(mt, 'drive', id=str(d.id))
            self.graft_items([(c,c) for c in saved_cols],
                             dt, d)

            
    def graft_net(self, mt, mid):
        saved_cols = ['ntype', 'vlan', 'name', 'nicmodel', 'macaddr',
                      'port', 'script', 'downscript', 'ifname']
        nets = Net.query.filter(Net.machine_id == mid).all()
        for n in nets:
            nt = ET.SubElement(mt, 'net', id=str(n.id))
            self.graft_items([(c,c) for c in saved_cols],
                             nt, n)
            ct = ET.SubElement(nt, 'vde')
            ct.text = n.vde_name

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
            ct = ET.SubElement(element, c[1])
            v = getattr(ob, c[0])
            if v is not None:
                ct.text = str(v)
            
    def write(self, fd):
        ET.ElementTree(self.root).write(fd, encoding="utf-8", 
                                        xml_declaration=True)
