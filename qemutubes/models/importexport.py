from qemutubes.models import __version__ as dbversion
from xml.dom import minidom
import StringIO

class Exchange(object):
    """ Object used to export and import DB data to and from XML
    Export workflow:
       x=Exchange(metadata, ignlist=['ignored_table', 'some_other_ignored_table'])
       x.export_xml() # Builds internal XML doc from DB data
       x.write_xml(fd) # Write XML to a file object
    Import workflow:
       x=Exchange(metadata)
       x.import_xml('file.xml') # Import XML file
       x.write_db() # Write imported data to DB
       """
    def __init__(self, metadata, ignlist=None):
        """ Initialize an Exchanger with optional list of tables to ignore
        metadata - The metadata for the tables we care about
        ignlist - list of table names to ignore """
        self.tables = list(metadata.sorted_tables)
        if ignlist:
            for table in list(self.tables):
                if table.name in ignlist:
                    self.tables.remove(table)

    # Exporter code
    def export_xml(self):
        """ Create XML doc from DB data """
        self.doc = minidom.Document()
        root = self.doc.createElement('qtubesexport')
        root.setAttribute('version', dbversion)
        self.doc.appendChild(root)
        for t in self.tables:
            e = self.doc.createElement(t.name)
            root.appendChild(e)
            self.export_table(e, t)

    def export_table(self, parent, table):
        """ Create XML entries for each row in a given table
        parent - parent XML node to graft to
        table - table to pull data from
        """
        engine = table.metadata.bind
        res = engine.execute(table.select()).fetchall()
        for row in res:
            rowel = self.doc.createElement('row')
            for (col, val) in row.items():
                e = self.doc.createElement(col)
                if val is None:
                    e.setAttribute('none', 'none')
                elif val is True or val is False:
                    e.setAttribute('bool', str(val).lower())
                else:
                    v = self.doc.createTextNode(str(val))
                    e.appendChild(v)
                rowel.appendChild(e)
            parent.appendChild(rowel)

    def write_xml(self, fd, **kw):
        """ Write XML data to a file-like object.
        fd - file-like object or string containing file path
        **kw - passed directly to minidom.Document.writexml()
        """
        if not hasattr(file, 'write'):
            fd = open(fd, 'w')
        self.doc.writexml(fd, **kw)

    # Importer code
    def import_xml(self, fd):
        """ Import XML data from file-like object.
        fd - File-like object of string containing path name
        """
        if not hasattr(fd, 'read'):
            fd = open(fd, 'r')
        self.doc = minidom.parse(fd)
        root = self.doc.documentElement
        if (not root.attributes.has_key('version') or
            root.tagName != 'qtubesexport'):
            raise Exception('Unknown document type')
        if root.attributes['version'].value != dbversion:
            raise Exception('Incorrect version: %s != %s' %
                            root.attributes['version'].value,
                            dbversion)

    def parse_tables(self):
        """ Parse table entries from XML document """
        root = self.doc.documentElement
        dbdata = {}
        for table in [n for n in root.childNodes 
                      if n.nodeType==n.ELEMENT_NODE]:
            rows = self.parse_rows(table)
            dbdata[table.tagName] = rows
        return dbdata

    def parse_rows(self, table):
        """ Parse row data from XML document
        table - XML node for a given table
        """
        rowlist = []
        for row in [n for n in table.childNodes 
                    if n.nodeType==n.ELEMENT_NODE]:
            coldict = {}
            for col in [n for n in row.childNodes 
                        if n.nodeType==n.ELEMENT_NODE]:
                if col.hasAttribute('none'):
                    val = None
                elif col.hasAttribute('bool'):
                    val = True if col.getAttribute('bool') == 'true' else False
                else:
                    val = self.get_data(col)
                coldict[col.tagName] = val
            rowlist.append(coldict)
        return rowlist

    def write_db(self):
        """ Insert parsed data into database """
        data = self.parse_tables()
        for table in self.tables:
            conn = table.metadata.bind.connect()
            try:
                rows = data[table.name]
            except KeyError:
                pass # Data not in XML file, skip it
            else:
                conn.execute(table.insert(), rows)
            finally:
                conn.close()

    def get_data(self, node):
        """ Get text data from a node. Whitespace is collapsed between nodes """
        val = []
        ch = node.childNodes
        for n in ch:
            if n.nodeType == n.TEXT_NODE:
              val.append(n.data.strip())
        return ' '.join(val)

