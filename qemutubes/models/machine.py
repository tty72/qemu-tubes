import os.path as path
from .. import qmp

from qemutubes.models import (
    DBSession, 
    Base,
    PathConfig,
    Launchable,
)

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

from sqlalchemy.orm import (
    relationship,
    column_property,
    backref,
    )

class CPUType(Base, PathConfig):
    __tablename__ = 'cpu_types'
    ctype = Column(Text, unique=True, primary_key=True)
    def __init__(self, ctype):
        self.ctype = ctype
    
    def __str__(self):
        return self.ctype

class MachineType(Base, PathConfig):
    __tablename__ = 'machine_types'
    mtype = Column(Text, unique=True, primary_key=True)
    def __init__(self, mtype):
        self.mtype = mtype

    def __str__(self):
        return self.mtype

class Machine(Base, PathConfig, Launchable):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    cpu = Column(Text, ForeignKey('cpu_types.ctype'))
    machtype = Column(Text, ForeignKey('machine_types.mtype'))
    mem = Column(Text)
    vncport = Column(Integer, unique=True, nullable=False)
    #conport = Column(Integer, unique=True, nullable=False)
    netnone = Column(Boolean, default=False)
    drives = relationship('Drive', cascade='all, delete, delete-orphan',
                          backref=backref('machine', single_parent=True))
    nets = relationship('Net', cascade='all, delete, delete-orphan',
                        backref=backref('machine', single_parent=True))

    def stop(self):
        return self.qmp.cmd('stop')['return']

    def cont(self):
        return self.qmp.cmd('cont')['return']

    def power_down(self):
        return self.qmp.cmd('system_powerdown')['return']

    def reset(self):
        return self.qmp.cmd('system_reset')['return']

    @property
    def status(self):
        return self.qmp.cmd('query-status')['return']

    @property
    def args(self):
        qemu = self.settings and self.settings['qtubes.qemubin'] or 'qemu'
        a = [(qemu,),
             ('-vnc', ':%d' % self.vncport),
             ('-chardev', 
              'socket,id=defaultmon,path=%s,server,nowait' % self.monsock),
             ('-mon', 'chardev=defaultmon,mode=control'),
             ('-name', '%s' % self.name),
             ('-pidfile', self.pidfile),
             ('-daemonize',),
             ]
        if self.mem:
            a.extend([('-m', '%s' % self.mem)])
        if self.cpu:
            a.extend([('-cpu', '%s' % self.cpu)])
        if self.machtype:
            a.extend([('-M', '%s' % self.machtype)])
        if not self.netnone:
            for n in self.nets:
                n.configure(self.settings)
                a.extend(n.args)
        for d in self.drives:
            d.configure(self.settings)
            a.extend(d.args)
        return a

    @property
    def qmp(self):
        try:
            return self._qmp
        except AttributeError:
            self._qmp = qmp.QEMUMonitorProtocol(self.monsock)
            self._qmp.connect()
            return self._qmp

    @property
    def monsock(self):
        """ Return our monitor socket """
        return '/tmp/qemu_mon%d' % self.id

    @property
    def cmdline(self):
        cmd = []
        for x in self.args:
            cmd.append(' '.join(x))
        return '  '.join(cmd)

    @property
    def pidfile(self):
        """ Return the PID file for this machine """
        piddir = self.settings and self.settings['qtubes.pid_dir'] or '/tmp'
        return path.join(piddir, 'qemu_%d.pid' % self.id)

    @property
    def use_net(self):
        """ True if netnone is not set, else False """
        return bool(True - (self.netnone or False))
        
    def __str__(self):
        return self.cmdline(None)
    

