import requests

from uma.resource import Resource


class ResourceServer:
    def __init__(self, authenticator, authz_endpoint):
        self.authenticator = authenticator
        self.authz_endpoint = authz_endpoint

    def register_resource(self, resource):
        resource_data = {
            "name": resource.name,
            "scopes": resource.scopes
        }
        res = requests.post(self.authz_endpoint+"/resource_set", headers=self._get_json_headers(), json=resource_data)
        return res.json()["_id"]

    def get_resource(self, resource_id):
        response = requests.get("{}/resource_set/{}".format(self.authz_endpoint, resource_id),
                                headers=self._get_auth_header())
        body = response.json()

        scopes = []
        for scope_data in body["scopes"]:
            scopes.append(scope_data["name"])

        return Resource(body["name"], scopes)

    def update_resource(self, resource_id, resource):
        resource_data = {
            "name": resource.name,
            "scopes": resource.scopes
        }
        requests.put("{}/resource_set/{}".format(self.authz_endpoint, resource_id), headers=self._get_json_headers(),
                     json=resource_data)

    def delete_resource(self, resource_id):
        requests.delete("{}/resource_set/{}".format(self.authz_endpoint, resource_id), headers=self._get_auth_header())

    def list_resources(self):
        response = requests.get("{}/resource_set".format(self.authz_endpoint), headers=self._get_auth_header())
        return response.json()

    def _get_json_headers(self):
        headers = {
            "Content-Type": "application/json",
        }
        headers.update(self._get_auth_header())
        return headers

    def _get_auth_header(self):
        return {
            "Authorization": "Bearer {}".format(self.authenticator.authenticate())
        }


class ResourceControl:
    def check(self, resource_constraint, rpt_claims):
        if rpt_claims is None:
            return False
        resource_claim = self._find_resource(resource_constraint.resource_id, rpt_claims)
        if resource_claim is None:
            return False
        return self._has_scopes(resource_constraint.scopes, resource_claim)

    def _find_resource(self, resource, rpt_claims):
        for res in rpt_claims['permissions']:
            if resource == res['resource_set_id']:
                return res
        return None

    def _has_scopes(self, scopes, resource_claim):
        scope_claims = resource_claim['scopes']
        for scope in scopes:
            if scope not in scope_claims:
                return False
        return True