import logging
import pytest

from test.integration.helpers import Keycloak, ClientUtils
from uma import ClientCredentialsAuthenticator, Resource, ResourceServer, UmaConfig

logging.basicConfig(level=logging.INFO)


class TestResourceRegistration:
    @pytest.fixture
    def client(self):
        keycloak = Keycloak()
        keycloak.start()

        client_utils = ClientUtils()
        token = keycloak.get_admin_token()
        client_utils.register(token)

        yield client_utils

        keycloak.stop()

    @pytest.fixture
    def config(self, client):
        UmaConfig.token_endpoint = client.token_endpoint
        UmaConfig.authz_endpoint = client.authz_endpoint
        UmaConfig.authenticator = ClientCredentialsAuthenticator(client.id, client.secret)

    def test_library_should_be_able_to_create_new_resource(self, config):
        server = ResourceServer()
        resource_id = server.register_resource(Resource("resource1", ["view"]))

        resource = server.get_resource(resource_id)

        assert resource.name == "resource1"
        assert resource.scopes == ["view"]
