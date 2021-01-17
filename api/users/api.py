import falcon

from webargs.falconparser import use_args

from core.hooks import get_instance
from users.models import User
from users.serializers import UserGetRequestSchema, OrganisationPatchRequestSchema, UserPostRequestSchema
from core.validators import validate_object_id

from users.v1.api import UserCollectionResourceV1, UserResourceV1
from users.v2.api import UserCollectionResourceV2, UserResourceV2


class UserCollectionResourceProxy:
    """
    User API methods to handle listing, searching, sorting and create new instance.
    """
    serializers = {
        'post': UserPostRequestSchema
    }

    @use_args(UserGetRequestSchema, location="query")
    def on_get(self, req, resp, params):
        """
        Get Post UserCollection Proxy

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
        """
        version = req.context['version']
        if not version or version == 1:
            controller = UserCollectionResourceV1()

        elif version == 2:
            controller = UserCollectionResourceV2()

        controller.on_get(req, resp, params)

    def on_post(self, req, resp):
        """
        Post UserCollection Proxy

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
        """
        version = req.context['version']
        if not version or version == 1:
            controller = UserCollectionResourceV1()

        elif version == 2:
            controller = UserCollectionResourceV2()

        controller.on_post(req, resp)


@falcon.before(validate_object_id, User)
@falcon.before(get_instance, User)
class UserResourceProxy:
    """
    Organisation API methods to handle single instance.
    """
    serializers = {
        'patch': OrganisationPatchRequestSchema
    }

    def on_get(self, req, resp, object_id):
        """
        Get Object instance details

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            object_id: (int): Object instance ID

        Returns:
            (falcon.response.Response): User instance details
        """
        version = req.context['version']
        if not version or version == 1:
            controller = UserResourceV1()

        elif version == 2:
            controller = UserResourceV2()

        controller.on_get(req, resp, object_id)

    def on_patch(self, req, resp, object_id):
        """
        Update Object instance details

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            object_id: (int): Object instance ID

        Raises::
            (HTTPNotFound): User instance does not exist
        """
        version = req.context['version']
        if not version or version == 1:
            controller = UserResourceV1()

        elif version == 2:
            controller = UserResourceV2()

        controller.on_patch(req, resp, object_id)

    def on_delete(self, req, resp, object_id):
        """
        Delete Object instance

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            object_id: (int): Object instance ID

        Raises::
            (HTTPNotFound): User instance does not exist
        """
        version = req.context['version']
        if not version or version == 1:
            controller = UserResourceV1()

        elif version == 2:
            controller = UserResourceV2()

        controller.on_delete(req, resp, object_id)
