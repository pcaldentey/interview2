import falcon

from sqlalchemy import cast, or_, String, func

from core.api import BaseSortingAPI
from core.hooks import get_instance
from core.validators import validate_object_id
from organisations.models import Organisation
from organisations.serializers import (
    OrganisationPatchRequestSchema,
    OrganisationPostRequestSchema
)


class OrganisationCollectionResourceV2(BaseSortingAPI):
    """
    Organisation API methods to handle listing, searching, sorting and create new instance.
    """
    serializers = {
        'post': OrganisationPostRequestSchema
    }
    model = Organisation
    sorting_mapper = {
        'name': func.lower(Organisation.name),
        'id': Organisation.id,
    }

    def on_get(self, req, resp, params):
        """
        Get Organisation instance list

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
            params (dict): Query params

        Returns:
            (dict): Organisation instance list and total number
        """

        paginated_filtered_result, total_objects = self.get_objects(req.context.db_session, params)

        resp.media = self.build_response(
            total=total_objects,
            data=paginated_filtered_result
        )

    def on_post(self, req, resp):
        """
        Post create Organisation instance

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
        """
        serializer = req.context['serializer']
        db_session = req.context['db_session']

        organisation = self.model.create(db_session, **serializer)
        resp.status = falcon.HTTP_201
        resp.media = organisation.convert_object_to_dict(('id', 'name', 'status_name'))

    def build_query_filters(self, params):
        """
        Create filter for search purpose

        Args:
            params (dict): Query params

        Returns:
            (list): List of filters to be applied
        """
        search_terms = params.get('search')

        if not search_terms:
            return []

        filters = []

        for search_term in search_terms:
            search_term = f'%{search_term.strip()}%'
            filters.append(or_(*[
                self.model.name.ilike(search_term),
                cast(self.model.id, String).ilike(search_term),
            ]))

        return filters

    @staticmethod
    def build_response(total, data):
        """
        Build response in proper format

        Args:
            total (int): total number of airports
            data (list): list of Airport instances

        Returns:
            (dict) with basic airport data
        """
        keys = ('id', 'name', 'status_name')

        return {
            'total': total,
            'data': [item.convert_object_to_dict(keys) for item in data]
        }


@falcon.before(validate_object_id, Organisation)
@falcon.before(get_instance, Organisation)
class OrganisationResourceV2:
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
        resp.media = self.build_response(req.context['instance'])

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
    def build_response(instance):
        """
        Create dict with full organisation data.

        Args:
            instance (Organisation): Organisation instance

        Returns:
            (dict): Organisation instance details
        """
        keys = ('id', 'name', 'status_name', 'enable_user_login')

        response = instance.convert_object_to_dict(keys)

        response['users'] = [
            item.convert_object_to_dict(('id', 'name', 'email', 'state_name'))
            for item in instance.users
        ]

        return response
