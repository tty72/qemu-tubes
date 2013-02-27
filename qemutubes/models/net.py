from qemutubes.models import (
    DBSession, 
    Base,
    NET_TYPES,
    PathConfig,
    )

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    ForeignKey,
    )

from sqlalchemy.orm import (
    relationship,
    column_property,
    backref,
    )


class NICType(Base, PathConfig):
    __tablename__ = 'nic_types'
    ntype = Column(Text, unique=True, primary_key=True)
    def __init__(self, ntype):
        self.ntype = ntype

class Net(Base, PathConfig):
    __tablename__ = 'nets'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='CASCADE'))
    ntype = Column(Enum(*NET_TYPES, name='enum_net'),
                   default=NET_TYPES[0])
    vlan = Column(Integer)
    name = Column(Text)
    # NIC cols
    nicmodel = Column(Text, ForeignKey('nic_types.ntype'))
    macaddr = Column(Text)
    # VDE cols
    vde_id = Column(Integer, ForeignKey('vdes.id'))
    port = Column(Integer)
    # Tap cols
    script = Column(Text)
    downscript = Column(Text)
    ifname = Column(Text)

    @property
    def args(self):
        if self.ntype == 'nic':
            return self.args_nic
        elif self.ntype == 'vde':
            return self.args_vde
        elif self.ntype == 'tap':
            return self.args_tap
        elif self.ntype == 'user':
            raise NotImplementedError
        elif self.ntype == 'socket':
            raise NotImplementedError
        elif self.type == 'dump':
            raise NotImplementedError
            
    @property
    def args_nic(self):
        x = 'nic'
        if self.nicmodel:
            x += ',model=%s' % self.nicmodel
        if self.vlan != None:
            x += ',vlan=%d' % self.vlan
        if self.macaddr:
            x += ',macaddr=%s' %self.macaddr
        if self.name:
            x += ',name=%s' % self.name
        return [('-net', x)]
    
    @property
    def args_vde(self):
        settings = self.settings
        sockdir = settings and settings['qtubes.vde_socks'] or '/tmp'
        socket = self.vde.sock if path.isabs(self.vde.sock) else path.join(
            sockdir, self.vde.sock)
        x = 'vde'
        x += ',sock=%s' % socket
        if self.port:
            x += ',port=%d' % self.port 
        if self.vlan != None:
            x += ',vlan=%d' % self.vlan
        if self.name:
            x += ',name=%s' % self.name
        return [('-net', x)]

    @property
    def args_tap(self):
        x = 'tap,ifname=%s' % self.ifname
        if self.vlan != None:
            x += ',vlan=%d' % self.vlan
        if self.name:
            x += ',name=%s' % self.name
        if self.script:
            x += ',script=%s' % self.script
        else:
            x += ',script=no'
        if self.downscript:
            x += ',downscript=%s' % self.downscript
        else:
            x += ',downscript=no'
        return [('-net', x)]
    
    @property
    def vde_name(self):
        return self.vde.name if self.vde else ''

