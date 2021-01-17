import falcon

from sqlalchemy import cast, or_, String, func
from webargs.falconparser import use_args

from core.api import BaseSortingAPI
from core.hooks import get_instance
from users.models import User
from users.serializers import UserGetRequestSchema, OrganisationPatchRequestSchema, UserPostRequestSchema
from core.validators import validate_object_id


class UserCollectionResource(BaseSortingAPI):
    """
    User API methods to handle listing, searching, sorting and create new instance.
    """
    serializers = {
        'post': UserPostRequestSchema
    }
    model = User
    sorting_mapper = {
        'first_name': func.lower(User.first_name),
        'last_name': func.lower(User.last_name),
    }

    @use_args(UserGetRequestSchema, location="query")
    def on_get(self, req, resp, params):
        """
        Get list of all Users

        Args:
            req (falcon.request.Request): Request object
            resp (falcon.response.Response): Response object
        """
        paginated_filtered_result, total_objects = self.get_objects(
            req.context.db_session, params
        )

        resp.media = self.build_response(
            total=total_objects,
            data=paginated_filtered_result,
            version=req.context['version']
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

        user = self.model.create(db_session, **serializer)
        resp.status = falcon.HTTP_201
        keys = ('id', 'name', 'email')

        if req.context['version'] and req.context['version'] > 1:
            keys += ('state_name', )

        resp.media = user.convert_object_to_dict(keys)

    def build_query_filters(self, params):
        """
        Build filters list based on provided query parameters.
        """
        search_terms = params.get('search')

        if not search_terms:
            return []

        filters = []

        for search_term in search_terms:
            search_term = f'%{search_term.strip()}%'
            filters.append(or_(*[
                self.model.last_name.ilike(search_term),
                self.model.first_name.ilike(search_term),
                self.model.email.ilike(search_term),
                cast(self.model.id, String).ilike(search_term),
            ]))

        return filters

    @staticmethod
    def build_response(total, data, version):
        """
        Build response in proper format

        Args:
            total (int): total number of airports
            data (list): list of Airport instances
            version (str|None): Current API version
        """
        keys = ('id', 'name', 'email')

        if version and version > 1:
            keys += ('state_name', )

        return {
            'total': total,
            'data': [item.convert_object_to_dict(keys) for item in data]
        }


@falcon.before(validate_object_id, User)
@falcon.before(get_instance, User)
class UserResource:
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
        resp.media = self.build_response(req.context['instance'], req.context['version'])

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
            (HTTPNotFound): User instance does not exist
        """
        response = User.delete_by_id(req.context['db_session'], object_id)
        resp.status = falcon.HTTP_204 if response else falcon.HTTP_404

    @staticmethod
    def build_response(instance, version):
        """
        Create dict with full user data.

        Args:
            instance (User): User instance
            version (str|None): Current API version

        Returns:
            (dict): User instance details
        """
        keys = ('id', 'name', 'email')

        if version and version > 1:
            keys += ('state_name', )

        response = instance.convert_object_to_dict(keys)
        response['organisation'] = instance.organisation.name
        return response
