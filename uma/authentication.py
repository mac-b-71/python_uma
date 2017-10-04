import requests

from .config import UmaConfig


class ClientCredentialsAuthenticator:
    def __init__(self, client_id, secret):
        self.client_id = client_id
        self.secret = secret

    def authenticate(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = "grant_type=client_credentials&client_id={}&client_secret={}"\
            .format(self.client_id, self.secret)
        response = requests.post(UmaConfig.token_endpoint, headers=headers, data=payload)
        return response.json()["access_token"]
