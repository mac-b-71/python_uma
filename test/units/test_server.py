import pytest
import requests

from uma import UmaConfig

from uma.resource import Resource, ResourceConstraint
from uma.server import ResourceServer, ResourceControl


@pytest.fixture
def config(mocker):
    UmaConfig.authz_endpoint = "endpoint"
    authenticator = mocker.Mock()
    UmaConfig.authenticator = authenticator


@pytest.fixture
def token():
    token = "some_token"
    UmaConfig.authenticator.authenticate.return_value = token
    return token


def test_server_should_call_resource_registration_endpoint_with_token_and_resource_data(mocker, config, token):
    mocker.patch('requests.post')

    resource = Resource("res1", ["view", "create"])
    server = ResourceServer()
    server.register_resource(resource)

    requests.post.assert_called_with(UmaConfig.authz_endpoint + "/resource_set", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token)
    }, json={
        "name": "res1",
        "scopes": ["view", "create"]
    })


def test_server_get_should_get_data_from_read_resource_endpoint(mocker, config, token):
    mocker.patch('requests.get')

    response = mocker.Mock()
    response.json.return_value = {
        "_id": "res_id",
        "name": "Resource",
        "scopes": [{"id": "scope_id", "name": "view"}]
    }
    requests.get.return_value = response

    server = ResourceServer()
    resource = server.get_resource("res_id")

    requests.get.assert_called_with(UmaConfig.authz_endpoint + "/resource_set/res_id", headers={
        "Authorization": "Bearer {}".format(token),
    })

    assert resource.name == "Resource"
    assert resource.scopes == ["view"]


def test_server_update_should_update_resource_in_update_resource_endpoint(mocker, config, token):
    mocker.patch('requests.put')

    server = ResourceServer()
    server.update_resource("res_id", Resource("Resource", ["view"]))

    requests.put.assert_called_with(UmaConfig.authz_endpoint + "/resource_set/res_id", headers={
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }, json={
        "name": "Resource",
        "scopes": ["view"]
    })


def test_server_update_should_delete_resource_in_delete_resource_endpoint(mocker, config, token):
    mocker.patch('requests.delete')
    server = ResourceServer()
    server.delete_resource("res_id")

    requests.delete.assert_called_with(UmaConfig.authz_endpoint + "/resource_set/res_id", headers={
        "Authorization": "Bearer {}".format(token),
    })


def test_server_list_should_list_resource_in_list_resource_endpoint(mocker, config, token):
    mocker.patch('requests.get')
    response = mocker.Mock()
    response.json.return_value = ["res1", "res2"]
    requests.get.return_value = response

    server = ResourceServer()
    resource_list = server.list_resources()

    assert resource_list == ["res1", "res2"]
    requests.get.assert_called_with(UmaConfig.authz_endpoint + "/resource_set", headers={
        "Authorization": "Bearer {}".format(token),
    })


def test_resource_control_check_when_no_rpt_should_return_false():
    control = ResourceControl()
    resource_constraint = ResourceConstraint("res", ["view"])
    assert control.check(resource_constraint, None) is False


def test_resource_control_check_when_there_is_not_permission_key_in_rpt_should_return_false():
    control = ResourceControl()
    resource_constraint = ResourceConstraint("res", ["view"])
    assert control.check(resource_constraint, {"sub": "123"}) is False


def test_resource_control_check_if_rpt_is_for_other_resource_should_return_false():
    control = ResourceControl()
    resource_constraint = ResourceConstraint("res", ["view"])
    claims = {
        "permissions": [
            {
                "resource_set_id": "res2",
                "scopes": ["view"]
            }
        ]
    }
    assert control.check(resource_constraint, claims) is False


def test_resource_control_check_if_rpt_has_missing_scopes_should_return_false():
    control = ResourceControl()
    resource_constraint = ResourceConstraint("res", ["view", "create"])
    claims = {
        "permissions": [
            {
                "resource_set_id": "res",
                "scopes": ["view"]
            }
        ]
    }
    assert control.check(resource_constraint, claims) is False


def test_resource_control_check_if_rpt_has_resource_and_scopes_should_return_true():
    control = ResourceControl()
    resource_constraint = ResourceConstraint("res", ["view", "create"])
    claims = {
        "permissions": [
            {
                "resource_set_id": "res",
                "scopes": ["view", "create"]
            }
        ]
    }
    assert control.check(resource_constraint, claims) is True


@pytest.fixture
def permission_ticket(mocker):
    mocker.patch('requests.post')
    expected_ticket = "some_ticket"
    response = mocker.Mock()
    response.json.return_value = {"ticket": expected_ticket}
    requests.post.return_value = response
    return expected_ticket


def test_resource_control_get_ticket_given_one_resource_constraint_should_return_the_ticket(config, token, permission_ticket):
    control = ResourceControl()
    resource_constraint = ResourceConstraint("res", ["view"])

    ticket = control.get_ticket(resource_constraint)

    requests.post.assert_called_with(UmaConfig.authz_endpoint+"/permission", json={
        "resource_set_id": "res",
        "scopes": ["view"]
    }, headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(token)})
    assert ticket == permission_ticket


def test_resource_control_get_ticket_given_list_of_resource_constraint_should_return_ticket(config, token, permission_ticket):
    control = ResourceControl()
    resource_constraints = [ResourceConstraint("res", ["view"]), ResourceConstraint("res2", ["view"])]

    ticket = control.get_ticket(resource_constraints)

    requests.post.assert_called_with(UmaConfig.authz_endpoint+"/permission", json=[{
        "resource_set_id": "res",
        "scopes": ["view"]
    }, {
        "resource_set_id": "res2",
        "scopes": ["view"]
    }], headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(token)})
    assert ticket == permission_ticket
