from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
__version__ = '0.2' # DB import/export relies on this. Increment it when the 
                    # model is altered enough to break import/export.
                    # This runs somewhat counter to PEP 396, but I can't
                    # think of a good argument against it.
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()
Base.query = DBSession.query_property()

DRIVE_IFS = ('ide', 'scsi', 'sd', 'mtd', 'floppy', 'pflash', 'virtio',)
MEDIA = ('disk', 'cdrom',)
CACHE_TYPES = ('writeback', 'none', 'unsafe', 'writethrough',)
AIO_TYPES = ('native', 'threads')
NET_TYPES = ('nic', 'vde', 'tap', 'user', 'socket', 'dump') 

from common import PathConfig, Launchable
from machine import Machine, CPUType, MachineType
from drive import Drive
from net import NICType, Net
from vde import VDE
from importexport import Exchange
