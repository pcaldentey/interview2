"""
    User creation, deletion, update and query tests
"""

import pytest

from unittest.mock import ANY

from falcon import HTTP_200, HTTP_201, HTTP_204, HTTP_404, HTTP_422

from users.tests.test_api import BaseUserTestCase


VERSION_URL = 'v2'
PATH = '/{}/users'.format(VERSION_URL)


@pytest.mark.apiv2
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
            {"id": ANY, "name": "Hans Gruber", "email": "john@example.com", "organisation": "Die Hard",
             "state_name": "ENABLED"}
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


@pytest.mark.apiv2
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
            {"id": ANY, "name": "John McClane", "email": "john@example.com", "organisation": "Die Hard",
             "state_name": "ENABLED"}
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


@pytest.mark.apiv2
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
            {"id": ANY, "name": "John McClane", "email": "john@example.com", "organisation": "Die Hard",
             "state_name": "ENABLED"}
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


@pytest.mark.apiv2
class UserPostTestCase(BaseUserTestCase):
    def test_create_user(self):
        organisation = self.create_organisation('Die Hard')

        response = self.request_post(
            path=PATH,
            status=HTTP_201,
            body={
                'first_name': 'John',
                'last_name': 'McClane',
                'email': 'john@example.com',
                'organisation_id': organisation.id
            }
        )
        self.assertDictEqual(
            response.json,
            {"id": ANY, "name": "John McClane", "email": "john@example.com", "state_name": "ENABLED"}
        )

    def test_create_user_unexisting_organisation_error(self):
        """ User of a non existing organisation """
        response = self.request_post(
            path=PATH,
            status=HTTP_422,
            body={
                'first_name': 'John',
                'last_name': 'McClane',
                'email': 'john@example.com',
                'organisation_id': 0
            }
        )
        self.assertDictEqual(
            response.json,
            {"title": "422 Unprocessable Entity",
             "errors": {
                "organisation_id": ["Organisation with given ID (0) does not exist"]
                }
             }
        )

    def test_create_user_null_values_error(self):
        """ User with None values """
        response = self.request_post(
            path=PATH,
            status=HTTP_422,
            body={
                'first_name': None,
                'last_name': None,
                'email': None,
                'organisation_id': None
            }
        )
        self.assertDictEqual(
            response.json,
            {"title": "422 Unprocessable Entity",
             "errors": {
                "email": ["Field may not be null."],
                "first_name": ["Field may not be null."],
                "last_name": ["Field may not be null."],
                "organisation_id": ["Field may not be null."]
                }
             }
        )

    def test_create_user_validation_error(self):
        """ User with not valid values """
        response = self.request_post(
            path=PATH,
            status=HTTP_422,
            body={
                'first_name': 1,
                'last_name': 1,
                'email': 'johnexample.com',
                'organisation_id': 'fake_id'
            }
        )
        self.assertDictEqual(
            response.json,
            {"title": "422 Unprocessable Entity",
             "errors": {
                'email': ['Not a valid email address.', 'Not a valid email address.'],
                'first_name': ['Not a valid string.'],
                'last_name': ['Not a valid string.'],
                'organisation_id': ['Not a valid integer.']
                }
             }
        )
