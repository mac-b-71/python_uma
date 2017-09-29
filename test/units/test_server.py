import unittest
from unittest.mock import patch, Mock

from uma.resource import Resource
from uma.server import ResourceServer


class RegisterResourceTestCase(unittest.TestCase):

    @patch("uma.server.requests")
    def test_server_should_call_resource_registration_endpoint_with_token_and_resource_data(self, requests):
        authz_endpoint = "someendpoint"
        resource = Resource("res1", ["view", "create"])
        authenticator = Mock()
        token = Mock()
        authenticator.authenticate.return_value = token

        server = ResourceServer(authenticator, authz_endpoint)
        server.register_resource(resource)

        requests.post.assert_called_with(authz_endpoint+"/resource_set", headers={
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }, json={
            "name": "res1",
            "scopes": ["view", "create"]
        })
