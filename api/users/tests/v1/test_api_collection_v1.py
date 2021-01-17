"""
    (VERSION 1) User collection resource tests
"""
import pytest

from unittest.mock import ANY

from falcon import HTTP_200, HTTP_201, HTTP_422

from users.tests.test_api import BaseUserTestCase


VERSION_URL = 'v1'
PATH = '/{}/users'.format(VERSION_URL)


@pytest.mark.apiv1
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
            {"id": ANY, "name": "John McClane", "email": "john@example.com"}
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


@pytest.mark.apiv1
class UserGetTestCase(BaseUserTestCase):
    def test_list_users(self):
        organisation = self.create_organisation('Die Hard')
        self.create_user(organisation.id)
        self.create_user(organisation.id, first_name='Hans', last_name='Gruber', email='hans@example.com')
        self.create_user(organisation.id, first_name='Holly', last_name='Genaro', email='holly@example.com')
        self.create_user(organisation.id, first_name='Zeus', last_name='Carver', email='zeus@example.com')
        response = self.request_get(
            path=PATH,
            status=HTTP_200
        )
        self.assertDictEqual(
            response.json,
            {'data': [
                        {'email': 'john@example.com', 'id': ANY, 'name': 'John McClane'},
                        {'email': 'hans@example.com', 'id': ANY, 'name': 'Hans Gruber'},
                        {'email': 'holly@example.com', 'id': ANY, 'name': 'Holly Genaro'},
                        {'email': 'zeus@example.com', 'id': ANY, 'name': 'Zeus Carver'}
                     ],
             'total': 4
             }
        )

    def test_list_user_paging(self):
        organisation = self.create_organisation('Die Hard')
        self.create_user(organisation.id)
        self.create_user(organisation.id, first_name='Hans', last_name='Gruber', email='hans@example.com')
        self.create_user(organisation.id, first_name='Holly', last_name='Genaro', email='holly@example.com')
        self.create_user(organisation.id, first_name='Zeus', last_name='Carver', email='zeus@example.com')

        response = self.request_get(
            path=PATH,
            status=HTTP_200,
            params={'size': 2, 'page': 0}
        )
        self.assertDictEqual(
            response.json,
            {'data': [
                        {'email': 'john@example.com', 'id': ANY, 'name': 'John McClane'},
                        {'email': 'hans@example.com', 'id': ANY, 'name': 'Hans Gruber'}
                     ],
             'total': 4
             }
        )

    def test_list_user_search(self):
        organisation = self.create_organisation('Die Hard')
        self.create_user(organisation.id)
        self.create_user(organisation.id, first_name='Hans', last_name='Gruber', email='hans@example.com')
        self.create_user(organisation.id, first_name='Holly', last_name='Genaro', email='holly@example.com')
        self.create_user(organisation.id, first_name='Zeus', last_name='Carver', email='zeus@example.com')

        response = self.request_get(
            path=PATH,
            status=HTTP_200,
            params={'size': 2, 'page': 0, 'search': 'hans'}
        )
        self.assertDictEqual(
            response.json,
            {'data': [
                        {'email': 'hans@example.com', 'id': ANY, 'name': 'Hans Gruber'}
                     ],
             'total': 1
             }
        )

    def test_list_user_search_empty(self):
        organisation = self.create_organisation('Die Hard')
        self.create_user(organisation.id)
        self.create_user(organisation.id, first_name='Hans', last_name='Gruber', email='hans@example.com')
        self.create_user(organisation.id, first_name='Holly', last_name='Genaro', email='holly@example.com')
        self.create_user(organisation.id, first_name='Zeus', last_name='Carver', email='zeus@example.com')

        response = self.request_get(
            path=PATH,
            status=HTTP_200,
            params={'size': 2, 'page': 0, 'search': 'hanso'}
        )
        self.assertDictEqual(
            response.json,
            {'data': [], 'total': 0}
        )

    def test_list_user_sorting_first_name(self):
        organisation = self.create_organisation('Die Hard')
        self.create_user(organisation.id)
        self.create_user(organisation.id, first_name='Hans', last_name='Gruber', email='hans@example.com')
        self.create_user(organisation.id, first_name='Holly', last_name='Genaro', email='holly@example.com')
        self.create_user(organisation.id, first_name='Zeus', last_name='Carver', email='zeus@example.com')
        response = self.request_get(
            path=PATH,
            status=HTTP_200,
            params={'sorting': 'first_name'}

        )
        self.assertDictEqual(
            response.json,
            {'data': [
                        {'email': 'hans@example.com', 'id': ANY, 'name': 'Hans Gruber'},
                        {'email': 'holly@example.com', 'id': ANY, 'name': 'Holly Genaro'},
                        {'email': 'john@example.com', 'id': ANY, 'name': 'John McClane'},
                        {'email': 'zeus@example.com', 'id': ANY, 'name': 'Zeus Carver'}
                     ],
             'total': 4
             }
        )

        pass

    def test_list_user_sorting_last_name(self):
        organisation = self.create_organisation('Die Hard')
        self.create_user(organisation.id)
        self.create_user(organisation.id, first_name='Hans', last_name='Gruber', email='hans@example.com')
        self.create_user(organisation.id, first_name='Holly', last_name='Genaro', email='holly@example.com')
        self.create_user(organisation.id, first_name='Zeus', last_name='Carver', email='zeus@example.com')
        response = self.request_get(
            path=PATH,
            status=HTTP_200,
            params={'sorting': 'last_name'}

        )
        self.assertDictEqual(
            response.json,
            {'data': [
                        {'email': 'zeus@example.com', 'id': ANY, 'name': 'Zeus Carver'},
                        {'email': 'holly@example.com', 'id': ANY, 'name': 'Holly Genaro'},
                        {'email': 'hans@example.com', 'id': ANY, 'name': 'Hans Gruber'},
                        {'email': 'john@example.com', 'id': ANY, 'name': 'John McClane'},
                     ],
             'total': 4
             }
        )

    def test_list_user_sorting_invalid_method(self):
        self.create_organisation('Die Hard')
        response = self.request_get(
            path=PATH,
            status=HTTP_200,
            params={'sorting': 'agehh'}

        )
        self.assertDictEqual(
            response.json,
            {'data': [], 'total': 0}
        )
