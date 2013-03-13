from pyramid.config import Configurator
from sqlalchemy import engine_from_config, event
from sqlalchemy.engine import Engine
try:
    from sqlite3 import Connection as sqlite3con
    havesqlite=True
except ImportError:
    havesqlite = False

from .models import (
    DBSession,
    Base,
    )

from pyramid.session import UnencryptedCookieSessionFactoryConfig
qtubes_session_factory = UnencryptedCookieSessionFactoryConfig('qemutubeskey')

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if havesqlite and isinstance(dbapi_connection, sqlite3con):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, 
                          session_factory=qtubes_session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('css', 'css', cache_max_age=3600)
    config.add_static_view('js', 'static/js', cache_max_age=3600)
    config.add_route('main', '/')
    # Machine routes
    config.add_route('machine_grid', '/json/machinegrid')
    config.add_route('machine_edit', '/machineedit')
    config.add_route('machine_delete', '/machinedelete')
    config.add_route('machine_view', '/machineview')
    config.add_route('machine_launch', '/machinelaunch')
    config.add_route('machine_stop', '/machinestop')
    config.add_route('machine_kill', '/machinekill')
    config.add_route('machine_powerdown', '/machinepowerdown')
    config.add_route('machine_vnc', '/machinevnc')
    # Drive routes
    config.add_route('drive_grid', '/json/drivegrid')
    config.add_route('drive_edit', '/driveedit')
    config.add_route('drive_delete', '/drivedelete')
    # Net routes
    config.add_route('net_grid', '/json/netgrid')
    config.add_route('net_edit', '/netedit')
    config.add_route('net_delete', '/netdelete')
    # VDE routes
    config.add_route('vde_grid', '/json/vdegrid')
    config.add_route('vde_edit', '/vdeedit')
    config.add_route('vde_delete', '/vdedelete')
    config.add_route('switch_launch', '/switchlaunch')
    # DB Routes
    config.add_route('db_import', '/dbimport')
    config.add_route('db_export', '/dbexport')
    config.scan()
    return config.make_wsgi_app()
