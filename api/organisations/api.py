import falcon

from webargs.falconparser import use_args

from core.hooks import get_instance
from core.validators import validate_object_id
from organisations.models import Organisation
from organisations.serializers import (
    OrganisationGetRequestSchema,
    OrganisationPatchRequestSchema
)
from organisations.v1.api import OrganisationCollectionResourceV1, OrganisationResourceV1
from organisations.v2.api import OrganisationCollectionResourceV2, OrganisationResourceV2


class OrganisationCollectionResourceProxy:
    """
    OrganisationCollection Resource proxy.
    """
    @use_args(OrganisationGetRequestSchema)
    def on_get(self, req, resp, params):
        """
        Get Proxy

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            params (dict): Query params

        Returns:
            (dict): Organisation instance list and total number
        """

        version = req.context['version']
        if version == 1:
            controller = OrganisationCollectionResourceV1()

        elif version == 2:
            controller = OrganisationCollectionResourceV2()

        controller.on_get(req, resp, params)

    def on_post(self, req, resp):
        """
        Post proxy

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
        """
        version = req.context['version']
        if version == 1:
            controller = OrganisationCollectionResourceV1()

        elif version == 2:
            controller = OrganisationCollectionResourceV2()

        controller.on_post(req, resp)


@falcon.before(validate_object_id, Organisation)
@falcon.before(get_instance, Organisation)
class OrganisationResourceProxy:
    """
    Organisation resourceproxy.
    """

    def on_get(self, req, resp, object_id):
        """
        Get Object instance details

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            object_id: (int): Object instance ID

        Returns:
            (falcon.response.Response): Organisation instance details
        """
        version = req.context['version']
        if version == 1:
            controller = OrganisationResourceV1()

        elif version == 2:
            controller = OrganisationResourceV2()

        controller.on_get(req, resp, object_id)

    def on_patch(self, req, resp, object_id):
        """
        Update Object instance details

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            object_id: (int): Object instance ID

        Raises::
            (HTTPNotFound): Organisation instance does not exist
        """
        version = req.context['version']
        if version == 1:
            controller = OrganisationResourceV1()

        elif version == 2:
            controller = OrganisationResourceV2()

        controller.on_patch(req, resp, object_id)

    def on_delete(self, req, resp, object_id):
        """
        Delete Object instance

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            object_id: (int): Object instance ID

        Raises::
            (HTTPNotFound): Organisation instance does not exist
        """
        version = req.context['version']
        if version == 1:
            controller = OrganisationResourceV1()

        elif version == 2:
            controller = OrganisationResourceV2()

        controller.on_delete(req, resp, object_id)

