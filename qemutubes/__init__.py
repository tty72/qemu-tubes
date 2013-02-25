from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

from pyramid.session import UnencryptedCookieSessionFactoryConfig
qtubes_session_factory = UnencryptedCookieSessionFactoryConfig('qemutubeskey')

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
    #config.add_route('home', '/')
    config.add_route('main', '/')
    config.add_route('machine_edit', '/machineedit')
    config.add_route('machine_delete', '/machinedelete')
    config.add_route('machine_view', '/machineview')
    config.add_route('machine_launch', '/machinelaunch')
    config.add_route('drive_grid', '/json/drivegrid')
    config.add_route('drive_edit', '/driveedit')
    config.add_route('drive_delete', '/drivedelete')
    config.add_route('net_grid', '/json/netgrid')
    config.add_route('net_edit', '/netedit')
    config.add_route('net_delete', '/netdelete')
    config.add_route('vde_grid', '/json/vdegrid')
    config.add_route('vde_edit', '/vdeedit')
    config.add_route('vde_delete', '/vdedelete')
    config.add_route('switch_launch', '/switchlaunch')
    config.scan()
    return config.make_wsgi_app()
