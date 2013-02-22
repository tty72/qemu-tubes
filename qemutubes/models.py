from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    func,
    select,
    or_,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    column_property,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
Base.query = DBSession.query_property()

DRIVE_IFS = ('ide', 'scsi', 'sd', 'mtd', 'floppy', 'pflash', 'virtio',)
MEDIA = ('disk', 'cdrom',)
CACHE_TYPES = ('writeback', 'none', 'unsafe', 'writethrough',)
AIO_TYPES = ('native', 'threads')

class CPUType(Base):
    __tablename__ = 'cpu_types'
    ctype = Column(Text, unique=True, primary_key=True)
    def __init__(self, ctype):
        self.ctype = ctype
    
    def __str__(self):
        return self.ctype

class MachineType(Base):
    __tablename__ = 'machine_types'
    mtype = Column(Text, unique=True, primary_key=True)
    def __init__(self, mtype):
        self.mtype = mtype

    def __str__(self):
        return self.mtype

class NICType(Base):
    __tablename__ = 'nic_types'
    ntype = Column(Text, unique=True, primary_key=True)
    def __init__(self, ntype):
        self.ntype = ntype

class VDE(Base):
    __tablename__='vdes'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    sock = Column(Text, nullable=False)
    mgmt = Column(Text, nullable=False)

class Drive(Base):
    __tablename__ = 'drives'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'))
    filepath = Column(Text, nullable=False)
    interface = Column(Enum(*DRIVE_IFS), nullable=False)
    media = Column(Enum(*MEDIA), nullable=False)
    bus = Column(Integer)
    unit = Column(Integer)
    ind = Column(Integer)
    cyls = Column(Integer)
    heads = Column(Integer)
    secs = Column(Integer)
    trans = Column(Integer)
    snapshot = Column(Boolean, default=False)
    cache = Column(Enum(*CACHE_TYPES), default=CACHE_TYPES[0])
    aio = Column(Enum(*AIO_TYPES), default=AIO_TYPES[0])
    ser = Column(Text)
    #machine = relationship('Machine')
    __table_args__ = (UniqueConstraint('ind','machine_id'),)

    @property
    def args(self):
        #FIXME: Double commas in file names where applicable
        x = 'file=%s,media=%s,if=%s' % (self.filepath,
                                        self.media,
                                        self.interface,
                                        )
        if self.bus:
            x += ',bus=%d,unit=%d' % (self.bus, self.unit,)
        if self.ind:
            x += ',index=%d' % self.ind
        if self.cyls:
            x += ',cyls=%d,heads=%d,secs=%s' % (self.cyls,
                                                self.heads,
                                                self.secs,)
        if self.trans:
            x += ',trans=%d' % self.trans
        if self.snapshot != None:
            x += ',snapshot=%s' % ('on' if self.snapshot else 'off')
        if self.cache:
            x += ',cache=%s' % self.cache
        if self.aio:
            x += ',aio=%s' % self.aio
        if self.ser:
            x +=  ',serial=%s' % self.ser
        return ['-drive', x]

class NetNIC(Base):
    __tablename__ = 'net_nics'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'))
    model = Column(Text, ForeignKey('nic_types.ntype'))
    vlan = Column(Integer)
    macaddr = Column(Text)
    name = Column(Text)
    machine = relationship('Machine')

    @property
    def args(self):
        x = 'nic'
        if self.model:
            x += ',model=%s' % self.model
        if self.vlan:
            x += ',vlan=%d' % self.vlan
        if self.macaddr:
            x += ',macaddr=%s' %self.macaddr
        if self.name:
            x += ',name="%s"' % self.name
        return ['-net', x]

class NetVDE(Base):
    __tablename__ = 'net_vdes'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'))
    vlan = Column(Integer)
    name = Column(Text)
    vde = Column(Integer, ForeignKey('vdes.id'), nullable=False)
    port = Column(Integer)
    machine = relationship('Machine')

    @property
    def args(self):
        x = 'vde'
        x += ',sock="%s"' % self.vde.sock
        if self.port:
            x += ',port=%d' % self.port
        if self.vlan:
            x += ',vlan=%d' % self.vlan
        if self.name:
            x += ',name="%s"' % self.name
        return ['-net', x]

class NetTap(Base):
    __tablename__ = 'net_taps'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'))
    vlan = Column(Integer)
    name = Column(Text)
    script = Column(Text)
    downscript = Column(Text)
    ifname = Column(Text, nullable=False)
    machine = relationship('Machine')

    @property
    def args(self):
        x = 'tap,ifname=%s' % self.ifname
        if self.vlan:
            x += ',vlan=%d' % self.vlan
        if self.name:
            x += ',name="%s"' % self.name
        if self.script:
            x += ',script="%s"' % self.script
        else:
            x += ',script=no'
        if self.downscript:
            x += ',downscript="%s"' % self.downscript
        else:
            x += ',downscript=no'
        return ['-net', x]

class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    cpu = Column(Text, ForeignKey('cpu_types.ctype'))
    machtype = Column(Text, ForeignKey('machine_types.mtype'))
    mem = Column(Text)
    vncport = Column(Integer, unique=True, nullable=False)
    conport = Column(Integer, unique=True, nullable=False)
    netnone = Column(Boolean, default=False)
    drives = relationship('Drive', backref='machine')
    net_nics = relationship('NetNIC')
    net_vdes = relationship('NetVDE')
    net_taps = relationship('NetTap')
#    drive_count = column_property(
#        select([func.count(Drive.id)]).where(Drive.id == id))
#    net_count = column_property(
#        select([func.count(NetNIC.id)+func.count(NetVDE.id)+
#                         func.count(NetTap.id)]).where(
#                or_(NetNIC.id == id, NetVDE.id == id, NetTap.id == id)))

    @property
    def args(self):
        a = ['-vnc', ':%d' % self.vncport,
             '-monitor', 'telnet::%d,server,nowait' % self.conport,
             '-name', '"%s"' % self.name,
             '-pidfile', '/var/run/qemu/%d.pid' % self.id,
             ]
        if self.mem:
            a.extend(['-m', '%s' % self.mem])
        if self.cpu:
            a.extend(['-cpu', '%s' % self.cpu])
        if self.machtype:
            a.extend(['-M', '%s' % self.machtype])
        if not self.netnone:
            for n in self.net_nics:
                a.extend(n.args)
            for n in self.net_vdes:
                a.extend(n.args)
            for n in self.net_taps:
                a.extend(n.args)
        for d in self.drives:
            a.extend(d.args)
        return a

    @property
    def cmdline(self):
        return ' '.join(self.args)
        
    def __str__(self):
        return self.cmdline
    
