import json
from urllib.parse import urlencode

import falcon
from falcon.testing import TestCase
from sqlalchemy.orm import scoped_session

from app import app
from core.db.session import Session


class BaseDBTestCase(TestCase):
    """Assign Session to TestCase."""

    def setUp(self):
        super().setUp()
        ScopedSession = scoped_session(Session)
        self.db_session = ScopedSession()


class BaseApiTestCase(BaseDBTestCase):
    """Prepare helpers to simulate API requests."""

    def setUp(self):
        super().setUp()
        self.app = app

        self.request_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        self.request_methods = {
            'DELETE': self.simulate_delete,
            'GET': self.simulate_get,
            'POST': self.simulate_post,
            'PUT': self.simulate_put,
            'PATCH': self.simulate_patch,
        }

    def _request_method(self, method_name, path, status, headers, body=None, params=None):
        if headers:
            self.request_headers.update(headers)

        request_method = self.request_methods[method_name]

        request_body = json.dumps(body, ensure_ascii=False) if body else None
        request_params = urlencode(params, safe=',') if params else None

        response = request_method(
            path,
            body=request_body,
            headers=self.request_headers,
            query_string=request_params,
        )
        self.assertEqual(response.status, status, response.content)

        return response

    def request_get(self, path, params=None, status=falcon.HTTP_200, headers=None):
        return self._request_method('GET', path, status, headers, params=params)

    def request_post(self, path, body=None, params=None, status=falcon.HTTP_200, headers=None):
        return self._request_method('POST', path, status, headers, body, params)

    def request_patch(self, path, body=None, status=falcon.HTTP_200, headers=None):
        return self._request_method('PATCH', path, status, headers, body)

    def request_delete(self, path, status=falcon.HTTP_204, headers=None):
        return self._request_method('DELETE', path, status, headers)

    def request_put(self, path, body, status=falcon.HTTP_200, headers=None):
        return self._request_method('PUT', path, status, headers, body)
