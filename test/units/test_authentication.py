import unittest
from unittest.mock import patch, MagicMock

from uma.authentication import ClientCredentialsAuthenticator


class ClientCredentialsAuthenticatorTestCase(unittest.TestCase):
    @patch("uma.authentication.requests")
    def test_should_post_to_token_endpoint_for_access_token(self, requests):
        endpoint = "endpoint"
        client_id = "cid"
        secret = "topsecret"

        response = MagicMock()
        response.json.return_value = {"access_token": "some_token"}
        requests.post.return_value = response

        auth = ClientCredentialsAuthenticator(endpoint, client_id, secret)
        token = auth.authenticate()
        self.assertEqual("some_token", token)
        requests.post.assert_called_with(endpoint,
                                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                                         data="grant_type=client_credentials&client_id=cid&client_secret=topsecret"
                                         )
