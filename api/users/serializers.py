from marshmallow.fields import Email, Integer, String
from marshmallow import validate

from core.serializers import BasePaginatedRequestSchema, BaseSearchSortGetRequestSchema, StrictSchema
from organisations.validators import validate_organisation_exists
from users.validators import validate_unique_user_email


class UserGetRequestSchema(BaseSearchSortGetRequestSchema, BasePaginatedRequestSchema):
    pass


class UserPostRequestSchema(StrictSchema):
    first_name = String(
        required=True,
        validate=validate.Length(max=128)
    )
    last_name = String(
        required=True,
        validate=validate.Length(max=128)
    )
    email = Email(
        required=True,
        validate=[validate.Length(max=254), validate.Email(), validate_unique_user_email],
        allow_none=False
    )
    organisation_id = Integer(
        required=True,
        validate=validate_organisation_exists
    )


class UserPatchRequestSchema(StrictSchema):
    first_name = String(
        required=True,
        validate=validate.Length(max=128)
    )
    last_name = String(
        required=True,
        validate=validate.Length(max=128)
    )
    organisation_id = Integer(
        required=True,
        validate=validate_organisation_exists
    )
