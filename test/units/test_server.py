import unittest
from unittest.mock import patch, Mock

from uma.resource import Resource, ResourceConstraint
from uma.server import ResourceServer, ResourceControl


class ResourceServerTestCase(unittest.TestCase):
    def setUp(self):
        self.authz_endpoint = "endpoint"
        self.authenticator = Mock()
        self.token = "token"
        self.authenticator.authenticate.return_value = self.token

    @patch("uma.server.requests")
    def test_server_should_call_resource_registration_endpoint_with_token_and_resource_data(self, requests):
        resource = Resource("res1", ["view", "create"])
        server = ResourceServer(self.authenticator, self.authz_endpoint)
        server.register_resource(resource)

        requests.post.assert_called_with(self.authz_endpoint + "/resource_set", headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token)
        }, json={
            "name": "res1",
            "scopes": ["view", "create"]
        })

    @patch("uma.server.requests")
    def test_server_get_should_get_data_from_read_resource_endpoint(self, requests):
        response = Mock()
        response.json.return_value = {
            "_id": "res_id",
            "name": "Resource",
            "scopes": [{"id": "scope_id", "name": "view"}]
        }
        requests.get.return_value = response

        server = ResourceServer(self.authenticator, self.authz_endpoint)
        resource = server.get_resource("res_id")

        requests.get.assert_called_with(self.authz_endpoint + "/resource_set/res_id", headers={
            "Authorization": "Bearer {}".format(self.token),
        })

        self.assertEqual("Resource", resource.name)
        self.assertEqual(["view"], resource.scopes)

    @patch("uma.server.requests")
    def test_server_update_should_update_resource_in_update_resource_endpoint(self, requests):
        server = ResourceServer(self.authenticator, self.authz_endpoint)
        server.update_resource("res_id", Resource("Resource", ["view"]))

        requests.put.assert_called_with(self.authz_endpoint + "/resource_set/res_id", headers={
            "Authorization": "Bearer {}".format(self.token),
            "Content-Type": "application/json"
        }, json={
            "name": "Resource",
            "scopes": ["view"]
        })

    @patch("uma.server.requests")
    def test_server_update_should_delete_resource_in_delete_resource_endpoint(self, requests):
        server = ResourceServer(self.authenticator, self.authz_endpoint)
        server.delete_resource("res_id")

        requests.delete.assert_called_with(self.authz_endpoint + "/resource_set/res_id", headers={
            "Authorization": "Bearer {}".format(self.token),
        })

    @patch("uma.server.requests")
    def test_server_list_should_list_resource_in_list_resource_endpoint(self, requests):
        response = Mock()
        response.json.return_value = ["res1", "res2"]
        requests.get.return_value = response

        server = ResourceServer(self.authenticator, self.authz_endpoint)
        resource_list = server.list_resources()

        self.assertEqual(["res1", "res2"], resource_list)
        requests.get.assert_called_with(self.authz_endpoint + "/resource_set", headers={
            "Authorization": "Bearer {}".format(self.token),
        })


class TestResourceControl:
    def setup_method(self):
        self.control = ResourceControl()

    def test_resource_control_check_when_no_rpt_should_return_false(self):
        resource_constraint = ResourceConstraint("res", ["view"])
        assert self.control.check(resource_constraint, None) is False

    def test_resource_control_check_if_rpt_is_for_other_resource_should_return_false(self):
        resource_constraint = ResourceConstraint("res", ["view"])
        claims = {
            "permissions": [
                {
                    "resource_set_id": "res2",
                    "scopes": ["view"]
                }
            ]
        }
        assert self.control.check(resource_constraint, claims) is False

    def test_resource_control_check_if_rpt_has_missing_scopes_should_return_false(self):
        resource_constraint = ResourceConstraint("res", ["view", "create"])
        claims = {
            "permissions": [
                {
                    "resource_set_id": "res",
                    "scopes": ["view"]
                }
            ]
        }
        assert self.control.check(resource_constraint, claims) is False

    def test_resource_control_check_if_rpt_has_resource_and_scopes_should_return_true(self):
        resource_constraint = ResourceConstraint("res", ["view", "create"])
        claims = {
            "permissions": [
                {
                    "resource_set_id": "res",
                    "scopes": ["view", "create"]
                }
            ]
        }
        assert self.control.check(resource_constraint, claims) is True
