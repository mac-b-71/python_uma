import requests

from uma.resource import Resource
from uma.config import UmaConfig


class ResourceServer:
    def register_resource(self, resource):
        resource_data = {
            "name": resource.name,
            "scopes": resource.scopes
        }
        res = requests.post(UmaConfig.authz_endpoint+"/resource_set", headers=self._get_json_headers(), json=resource_data)
        return res.json()["_id"]

    def get_resource(self, resource_id):
        response = requests.get("{}/resource_set/{}".format(UmaConfig.authz_endpoint, resource_id),
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
        requests.put("{}/resource_set/{}".format(UmaConfig.authz_endpoint, resource_id), headers=self._get_json_headers(),
                     json=resource_data)

    def delete_resource(self, resource_id):
        requests.delete("{}/resource_set/{}".format(UmaConfig.authz_endpoint, resource_id), headers=self._get_auth_header())

    def list_resources(self):
        response = requests.get("{}/resource_set".format(UmaConfig.authz_endpoint), headers=self._get_auth_header())
        return response.json()

    def _get_json_headers(self):
        headers = {
            "Content-Type": "application/json",
        }
        headers.update(self._get_auth_header())
        return headers

    @staticmethod
    def _get_auth_header():
        return {
            "Authorization": "Bearer {}".format(UmaConfig.authenticator.authenticate())
        }


class ResourceControl:
    def check(self, resource_constraint, rpt_claims):
        if rpt_claims is None:
            return False
        resource_claim = self._find_resource(resource_constraint.resource_id, rpt_claims)
        if resource_claim is None:
            return False
        return self._has_scopes(resource_constraint.scopes, resource_claim)

    def get_ticket(self, resource_constraints):
        payload = self._parse_resource_constraints(resource_constraints)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(UmaConfig.authenticator.authenticate())
        }
        return requests.post(UmaConfig.authz_endpoint+"/permission", json=payload, headers=headers).json()["ticket"]

    @staticmethod
    def _parse_resource_constraints(resource_constraints):
        def parse_single(res_const):
            return {
                "resource_set_id": res_const.resource_id,
                "scopes": res_const.scopes
            }

        if isinstance(resource_constraints, list):
            return list(map(parse_single, resource_constraints))
        return parse_single(resource_constraints)

    @staticmethod
    def _find_resource(resource, rpt_claims):
        if 'permissions' in rpt_claims:
            for res in rpt_claims['permissions']:
                if resource == res['resource_set_id']:
                    return res
        return None

    @staticmethod
    def _has_scopes(scopes, resource_claim):
        scope_claims = resource_claim['scopes']
        for scope in scopes:
            if scope not in scope_claims:
                return False
        return True