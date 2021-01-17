import falcon

from core.db.session import Session
from core.middleware.db import SQLAlchemySessionManager
from core.middleware.require_json import RequireJSON
from core.middleware.serializers import SerializerMiddleware
from core.middleware.version import VersionMiddleware
from core.serializers.errors import error_serializer

from organisations.api import OrganisationResourceProxy, OrganisationCollectionResourceProxy
from users.api import UserResourceProxy, UserCollectionResourceProxy


app = falcon.API(middleware=[
    RequireJSON(),
    VersionMiddleware(),
    SQLAlchemySessionManager(Session),
    SerializerMiddleware(),
])

app.set_error_serializer(error_serializer)

app.add_route('/{api_version}/organisations/', OrganisationCollectionResourceProxy())
app.add_route('/{api_version}/organisations/{object_id}', OrganisationResourceProxy())
app.add_route('/{api_version}/users/', UserCollectionResourceProxy())
app.add_route('/{api_version}/users/{object_id}', UserResourceProxy())
