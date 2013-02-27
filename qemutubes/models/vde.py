import os.path as path
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


class VDE(Base, PathConfig, Launchable):
    __tablename__='vdes'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    sock = Column(Text, nullable=False)
    mgmt = Column(Text, nullable=False)
    tap = Column(Text)
    mode = Column(Text)
    group = Column(Text)
    rcfile = Column(Text)
    ports = Column(Integer)
    hub = Column(Boolean, default=False)
    fstp = Column(Boolean)
    macaddr = Column(Text)
    nets = relationship('Net', backref='vde', cascade='all, delete-orphan')

    @property
    def pidfile(self):
        """ Return the PID file for this switch """
        piddir = self.settings and self.settings['qtubes.pid_dir'] or '/tmp'
        return path.join(piddir, 'vde_%d.pid' % self.id)

    @property
    def sockfile(self):
        """ Return the socket file path """
        sockdir = self.settings and self.settings['qtubes.vde_socks'] or '/tmp'
        sockpath = self.sock if path.isabs(self.sock) else path.join(
            sockdir, self.sock)
        return sockpath

    @property
    def mgmtfile(self):
        """ Return the management socket file path """
        sockdir = self.settings and self.settings['qtubes.vde_socks'] or '/tmp'
        sockpath = self.mgmt if path.isabs(self.mgmt) else path.join(
            sockdir, self.mgmt)
        return sockpath

    @property
    def args(self):
        vde = self.settings and self.settings['qtubes.vdeswitch'] or 'vde_switch'
        args = [(vde, '-d'),
                ('-p', self.pidfile),
                ('-s', self.sockfile),
                ('-M', self.mgmtfile),]
        #FIXME: Handle other vde_switch options
        return args

