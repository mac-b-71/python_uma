import requests


class ResourceServer:
    def __init__(self, authenticator, authz_endpoint):
        self.authenticator = authenticator
        self.authz_endpoint = authz_endpoint

    def register_resource(self, resource):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.authenticator.authenticate())
        }
        resource_data = {
            "name": resource.name,
            "scopes": resource.scopes
        }
        res = requests.post(self.authz_endpoint+"/resource_set", headers=headers, json=resource_data)
        return res.json()["_id"]
