import falcon

from core.db.session import Session
from core.middleware.db import SQLAlchemySessionManager
from core.middleware.require_json import RequireJSON
from core.middleware.serializers import SerializerMiddleware
from core.middleware.version import VersionMiddleware
from core.serializers.errors import error_serializer

from organisations.api import OrganisationResource, OrganisationCollectionResource
from users.api import UserResource, UserCollectionResource


app = falcon.API(middleware=[
    RequireJSON(),
    VersionMiddleware(),
    SQLAlchemySessionManager(Session),
    SerializerMiddleware(),
])

app.set_error_serializer(error_serializer)

app.add_route('/{api_version}/organisations/', OrganisationCollectionResource())
app.add_route('/{api_version}/organisations/{object_id}', OrganisationResource())
app.add_route('/{api_version}/users/', UserCollectionResource())
app.add_route('/{api_version}/users/{object_id}', UserResource())
