from qemutubes.models import (
    DBSession, 
    Base,
    DRIVE_IFS,
    MEDIA,
    CACHE_TYPES,
    AIO_TYPES,
    PathConfig,
    )
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    UniqueConstraint,
    Boolean,
    ForeignKey,
    )

class Drive(Base, PathConfig):
    __tablename__ = 'drives'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id', ondelete='CASCADE'))
    filepath = Column(Text, nullable=False)
    interface = Column(Enum(*DRIVE_IFS, name='enum_iface'), 
                       nullable=False)
    media = Column(Enum(*MEDIA, name='enum_media'), 
                   nullable=False)
    bus = Column(Integer)
    unit = Column(Integer)
    ind = Column(Integer)
    cyls = Column(Integer)
    heads = Column(Integer)
    secs = Column(Integer)
    trans = Column(Integer)
    snapshot = Column(Boolean, default=False)
    cache = Column(Enum(*CACHE_TYPES, name='enum_cache'),
                   default=CACHE_TYPES[0])
    aio = Column(Enum(*AIO_TYPES, name='enum_aio'), 
                 default=AIO_TYPES[0])
    ser = Column(Text)
    __table_args__ = (UniqueConstraint('ind','machine_id'),)

    @property
    def args(self):
        settings = self.settings
        imgdir = settings and settings['qtubes.image_dir'] or '/tmp'
        filepath = self.filepath if path.isabs(self.filepath) else path.join(
            imgdir, self.filepath)
        #FIXME: Double commas in file names where applicable
        x = 'file=%s,media=%s,if=%s' % (filepath,
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
        if self.ind != None:
            x += ',index=%d' % self.ind
        if self.snapshot != None:
            x += ',snapshot=%s' % ('on' if self.snapshot else 'off')
        if self.cache:
            x += ',cache=%s' % self.cache
        if self.aio:
            x += ',aio=%s' % self.aio
        if self.ser:
            x +=  ',serial=%s' % self.ser
        return [('-drive', x)]

