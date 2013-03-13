import tw2.core
import tw2.forms
import tw2.sqla
from .. import models as model
from . import DBForm

class DBImportForm(tw2.forms.TableForm):
    upfile = tw2.forms.FileField(validator=tw2.core.Required)

