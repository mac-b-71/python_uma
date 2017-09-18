import logging
import time

import docker
import requests


class Keycloak:
    def __init__(self):
        self.tag = "3.1.0.Final"
        self.username = "admin"
        self.password = "password"

        self._docker = docker.from_env()
        self._container = None

    def start(self):
        environment = {
            "KEYCLOAK_USER": self.username,
            "KEYCLOAK_PASSWORD": self.password
        }

        logging.info("Starting Keycloak...")
        self._container = self._docker.containers.run("jboss/keycloak:{}".format(self.tag), detach=True,
                                                      environment=environment,
                                                      ports={"8080": "8080"}
                                                      )
        logging.info("Keycloak started")
        self._wait()

    def _wait(self):
        while True:
            try:
                res = requests.get("http://localhost:8080/auth")
                if res.status_code == 200:
                    break
            except Exception:
                pass
            logging.info("Waiting for Keycloak...")
            time.sleep(5)
        logging.info("Keycloak ready")

    def stop(self):
        self._container.stop()
        self._container.remove()
        logging.info("Keycloak stopped and removed")

    def get_admin_token(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = "grant_type=password&client_id=admin-cli&username={}&password={}".format(self.username, self.password)
        res = requests.post("http://localhost:8080/auth/realms/master/protocol/openid-connect/token", data=body,
                            headers=headers)
        return res.json()['access_token']


class ClientUtils:
    def __init__(self):
        self.id = "resource-server"
        self.secret = "508efdf3-63c2-4f0e-9c81-7711673c2f99"

    def register(self, token):
        url = "http://localhost:8080/auth/admin/realms/master/clients"
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }

        with open("config/create_client.json") as f:
            body = f.read().replace("<CLIENT_ID>", self.id).replace("<CLIENT_SECRET>", self.secret)
        requests.post(url, data=body, headers=headers)
        logging.info("Client '{}' registered".format(self.id))

    def get_resource(self, resource_id):
        headers = {
            "Authorization": "Bearer {}".format(self.get_client_token()),
        }
        return requests.get("http://localhost:8080/auth/realms/master/authz/protection/resource_set/{}"
                            .format(resource_id), headers=headers).json()

    def get_client_token(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = "grant_type=client_credentials&client_id={}&client_secret={}".format(self.id, self.secret)
        res = requests.post("http://localhost:8080/auth/realms/master/protocol/openid-connect/token", data=body,
                            headers=headers)
        return res.json()['access_token']
