import logging
import unittest

from test.integration.helpers import Keycloak, ClientUtils
from uma.authentication import ClientCredentialsAuthenticator
from uma.resource import Resource
from uma.server import ResourceServer

logging.basicConfig(level=logging.INFO)


class ResourceRegistrationTestCase(unittest.TestCase):

    def setUp(self):
        self.keycloak = Keycloak()
        self.keycloak.start()

        self.client_utils = ClientUtils()
        token = self.keycloak.get_admin_token()
        self.client_utils.register(token)

    def tearDown(self):
        self.keycloak.stop()

    def test_library_should_be_able_to_create_new_resource(self):
        authenticator = ClientCredentialsAuthenticator(self.client_utils.token_endpoint,
                                                       self.client_utils.id, self.client_utils.secret)
        server = ResourceServer(authenticator, self.client_utils.authz_endpoint)
        resource_id = server.register_resource(Resource("resource1", ["view"]))

        resource = server.get_resource(resource_id)

        self.assertEqual("resource1", resource.name)
        self.assertEqual(["view"], resource.scopes)
