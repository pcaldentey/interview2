import falcon

from webargs.falconparser import use_args

from core.hooks import get_instance
from core.validators import validate_object_id
from organisations.models import Organisation
from organisations.serializers import (
    OrganisationGetRequestSchema,
    OrganisationPatchRequestSchema
)
from organisations.v1.api import OrganisationCollectionResourceV1
from organisations.v2.api import OrganisationCollectionResourceV2


class OrganisationCollectionResourceProxy:
    """
    Organisation API methods to handle listing, searching, sorting and create new instance.
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
class OrganisationResource:
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
            (falcon.response.Response): Organisation instance details
        """
        resp.media = self.build_response(req.context['instance'], req.context['version'])

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
        serialized_data = req.context['serializer']
        db_session = req.context['db_session']
        instance = req.context['instance']

        if serialized_data:
            instance.update(db_session, commit=False, **serialized_data)

        db_session.commit()
        resp.status = falcon.HTTP_204

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
        instance = req.context['instance']

        users_no = len(instance.users)
        if users_no > 0:
            raise falcon.HTTPConflict(
                f'This Organisation is assign to {users_no} airport(s). Remove users before delete!'
            )

        response = Organisation.delete_by_id(req.context['db_session'], object_id)
        resp.status = falcon.HTTP_204 if response else falcon.HTTP_404

    @staticmethod
    def build_response(instance, version):
        """
        Create dict with full organisation data.

        Args:
            instance (Organisation): Organisation instance
            version (str|None): Current API version

        Returns:
            (dict): Organisation instance details
        """
        keys = ('id', 'name', 'status_name')

        if version and version > 1.0:
            keys += ('enable_user_login', )

        response = instance.convert_object_to_dict(keys)

        if version and version > 1.0:
            response['users'] = [
                item.convert_object_to_dict(('id', 'name', 'email', 'state_name'))
                for item in instance.users
            ]

        return response
