from country_workspace.models import User
from django_webtest import DjangoTestApp

class CWTestApp(DjangoTestApp):
    _user: User | None
