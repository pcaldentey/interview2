"""
    (VERSION 1) User creation, deletion, update and query tests
"""

import pytest

from unittest.mock import ANY

from falcon import HTTP_200, HTTP_204, HTTP_404, HTTP_422

from users.tests.test_api import BaseUserTestCase


VERSION_URL = 'v1'
PATH = '/{}/users'.format(VERSION_URL)


@pytest.mark.apiv1
class UserPatchTestCase(BaseUserTestCase):
    def test_patch_user(self):
        """ Update specific user """
        organisation = self.create_organisation('Die Hard')
        user = self.create_user(organisation.id)
        path = '{}/{}'.format(PATH, user.id)

        # Update created user
        response = self.request_patch(
            path=path,
            status=HTTP_204,
            body={
                'first_name': 'Hans',
                'last_name': 'Gruber',
                'organisation_id': organisation.id
                }
        )

        # Check changes
        response = self.request_get(
            path=path,
            status=HTTP_200
        )
        self.assertDictEqual(
            response.json,
            {"id": ANY, "name": "Hans Gruber", "email": "john@example.com", "organisation": "Die Hard"}
        )

    def test_patch_unexisting_user_error(self):
        """ Update non existing user """

        organisation = self.create_organisation('Die Hard')
        path = '{}/{}'.format(PATH, 45)
        response = self.request_patch(
            path=path,
            status=HTTP_404,
            body={
                'first_name': 'Hans',
                'last_name': 'Gruber',
                'organisation_id': organisation.id
                }
        )

        self.assertDictEqual(
            response.json,
            {"title": "404 Not Found"}
        )

    def test_patch_validation_error(self):
        """ Update non existing user """
        path = '{}/{}'.format(PATH, 45)
        response = self.request_patch(
            path=path,
            status=HTTP_422,
            body={'test': 'testin'}
        )

        self.assertDictEqual(
            response.json,
            {"title": "422 Unprocessable Entity",
             "errors": {"first_name": ["Missing data for required field."],
                        "last_name": ["Missing data for required field."],
                        "organisation_id": ["Missing data for required field."],
                        "test": ["Unknown field."]}}
        )


@pytest.mark.apiv1
class UserDeleteTestCase(BaseUserTestCase):
    def test_delete_user(self):
        """ Delete specific user """
        organisation = self.create_organisation('Die Hard')
        user = self.create_user(organisation.id)
        path = '{}/{}'.format(PATH, user.id)

        # Check user exist via api
        response = self.request_get(
            path=path,
            status=HTTP_200
        )
        self.assertDictEqual(
            response.json,
            {"id": ANY, "name": "John McClane", "email": "john@example.com", "organisation": "Die Hard"}
        )

        # Delete created user
        response = self.request_delete(
            path=path,
            status=HTTP_204
        )

        # Checking user does not exist anymore
        response = self.request_get(
            path=path,
            status=HTTP_404
        )

        self.assertDictEqual(
            response.json,
            {"title": "404 Not Found"}
        )

    def test_delete_unexisting_user(self):
        """ Delete non existing user """
        path = '{}/{}'.format(PATH, 45)
        response = self.request_delete(
            path=path,
            status=HTTP_404
        )

        self.assertDictEqual(
            response.json,
            {"title": "404 Not Found"}
        )


@pytest.mark.apiv1
class UserGetTestCase(BaseUserTestCase):
    def test_get_user(self):
        """ Retrieve specific user """
        organisation = self.create_organisation('Die Hard')
        user = self.create_user(organisation.id)

        path = '{}/{}'.format(PATH, user.id)
        response = self.request_get(
            path=path,
            status=HTTP_200
        )

        self.assertDictEqual(
            response.json,
            {"id": ANY, "name": "John McClane", "email": "john@example.com", "organisation": "Die Hard"}
        )

    def test_get_unexisting_user(self):
        """ Retrieve non existing user """
        path = '{}/{}'.format(PATH, 45)
        response = self.request_get(
            path=path,
            status=HTTP_404
        )

        self.assertDictEqual(
            response.json,
            {"title": "404 Not Found"}
        )
