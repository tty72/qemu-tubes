import sqlalchemy as sa
from tw2.sqla import utils as sautil

class DBForm(object):
    """ Base mixin class for DB related form widgets
    Provides helper methods for fetching and storing data to a model
    """
    def fetch_data(self, req):
        """ Load form values from given Model (entity) given appropriate 
            Primary keys.
            Copied from tw2.sqla.DbFormPage class
        """
        data = req.GET.mixed()
        filter = dict((col.name, data.get(col.name))
                        for col in sa.orm.class_mapper(self.entity).primary_key)
        self.value = req.GET and self.entity.query.filter_by(**filter).first() or None

    @classmethod
    def insert_or_update(cls, data):
        """ Wrapper for tw2.sqla.utils update_or_create() 
            Basically checks object for primary key values then
            either inserts into or updates the DB accordingly""" 
        sautil.update_or_create(cls.entity, data)

