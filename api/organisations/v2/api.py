import falcon

from sqlalchemy import cast, or_, String, func
from webargs.falconparser import use_args

from core.api import BaseSortingAPI
from core.hooks import get_instance
from core.validators import validate_object_id
from organisations.models import Organisation
from organisations.serializers import (
    OrganisationGetRequestSchema,
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

