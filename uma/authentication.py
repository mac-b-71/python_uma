import requests


class ClientCredentialsAuthenticator:
    def __init__(self, token_endpoint, client_id, secret):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.secret = secret

    def authenticate(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = "grant_type=client_credentials&client_id={}&client_secret={}"\
            .format(self.client_id, self.secret)
        response = requests.post(self.token_endpoint, headers=headers, data=payload)
        return response.json()["access_token"]
