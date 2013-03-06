import os
import sys
import transaction
import subprocess

from sqlalchemy import engine_from_config, event
from sqlalchemy.engine import Engine
try:
    from sqlite3 import Connection as sqlite3con
    havesqlite=True
except ImportError:
    havesqlite = False

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    CPUType,
    MachineType,
    NICType,
    Machine,
    Drive,
    Net,
    Base,
    )

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if havesqlite and isinstance(dbapi_connection, sqlite3con):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def cpu_list(qemubin):
    cl = subprocess.check_output([qemubin,'-cpu', '?'])
    cl = cl.split('\n')
    clist = []
    for c in cl:
        if '[' in c:
            clist.append(c.split('[')[1][:-1])
    return clist

def machine_list(qemubin):
    ml = subprocess.check_output([qemubin,'-M', '?'])
    ml = ml.split('\n')
    mlist = []
    for m in ml[1:]:
        mid = m.split(' ')[0]
        if mid != '':
            mlist.append(mid)
    return mlist

def nic_list(qemubin):
    nl = subprocess.check_output([qemubin, '-net', 'nic,model=?'], 
                                 stderr=subprocess.STDOUT)
    nl=nl.split(' ')[-1:][0]
    return nl.strip().split(',')

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    qemubin = settings.get('qtubes.qemubin', '/usr/bin/qemu')
    cpus = cpu_list(qemubin)
    print "Supported CPUs: ",cpus
    machs = machine_list(qemubin)
    print "Supported machines: ",machs
    nics = nic_list(qemubin)
    print "Supported NICs: ",nics
    with transaction.manager:
        for i in ['']+cpus:
            DBSession.add(CPUType(i))
        for i in ['']+machs:
            DBSession.add(MachineType(i))
        for i in ['']+nics:
            DBSession.add(NICType(i))
        """
        m = Machine()
        m.name = 'Test'
        m.cpu = 'host'
        m.machtype = 'pc'
        m.mem = '128M'
        m.vncport = 0
        m.conport = 21472
        DBSession.add(m)
        d = Drive()
        d.filepath = '/tmp/drive1.img'
        d.interface='ide'
        d.media='disk'
        d.ind=0
        d.ser='SG324323'
        d.machine=m
        DBSession.add(d)
        n1 = Net()
        n1.ntype='nic'
        n1.machine = m
        n1.vlan = 1
        n1.model = 'ne2k_pci'
        n1.macaddr = 'aa:bb:cc:dd:ee:ff'
        n1.name = 'NIC 1'
        DBSession.add(n1)
    m = DBSession.query(Machine).first()
    print qemubin+' '+m.cmdline
    """
