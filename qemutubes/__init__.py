from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('css', 'css', cache_max_age=3600)
    #config.add_route('home', '/')
    config.add_route('machine_grid', '/')
    config.add_route('machine_edit', '/machineedit')
    config.add_route('machine_del', '/machinedelete')
    config.add_route('machine_view', '/machineview')
    config.add_route('drive_grid', '/json/drivegrid')
    config.add_route('drive_edit', '/driveedit')
    config.scan()
    return config.make_wsgi_app()
