import logging
import unittest

from test.integration.helpers import Keycloak, ClientUtils
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
        server = ResourceServer()
        resource_id = server.register_resource("resource1")

        res = self.client_utils.get_resource(resource_id)

        self.assertTrue('error' not in res)
