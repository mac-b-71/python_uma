import requests

from uma import UmaConfig
from uma import ClientCredentialsAuthenticator


def test_should_post_to_token_endpoint_for_access_token(mocker):
    mocker.patch('requests.post')

    UmaConfig.token_endpoint = "endpoint"
    client_id = "cid"
    secret = "topsecret"

    response = mocker.Mock()
    response.json.return_value = {"access_token": "some_token"}
    requests.post.return_value = response

    auth = ClientCredentialsAuthenticator(client_id, secret)
    token = auth.authenticate()
    assert token == "some_token"
    requests.post.assert_called_once_with(UmaConfig.token_endpoint,
                                          headers={"Content-Type": "application/x-www-form-urlencoded"},
                                          data="grant_type=client_credentials&client_id=cid&client_secret=topsecret"
                                          )
