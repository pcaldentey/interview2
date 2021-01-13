import falcon
import json
from marshmallow import ValidationError

from core.errors import HTTPError


class SerializerMiddleware:
    def process_resource(self, req, resp, resource, params):
        try:
            serializer = resource.serializers[req.method.lower()]
        except (AttributeError, IndexError, KeyError):
            return
        else:
            req_data = req.stream.read(req.content_length)

            try:
                req.context.serializer = serializer().load(data=json.loads(req_data))
            except ValidationError as err:
                raise HTTPError(status=falcon.HTTP_422, errors=err.messages)
