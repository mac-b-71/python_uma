from flask import Flask

import uma


app = Flask(__name__)


def define_resource(resource_server, resource):
    _id = resource_server.register_resource(resource)
    return _id, resource


def main():
    token_endpoint = "http://myhightech.org:9000/auth/realms/python/protocol/openid-connect/token"
    authz_endpoint = "http://myhightech.org:9000/auth/realms/python/authz/protection"

    authenticator = uma.ClientCredentialsAuthenticator(token_endpoint, "resource-server",
                                                       "508efdf3-63c2-4f0e-9c81-7711673c2f99")
    resource_server = uma.ResourceServer(authenticator, authz_endpoint)
    resource_control = uma.ResourceControl()

    database_resource = define_resource(resource_server, uma.Resource("database", ["view", "create", "delete"]))

    @app.route('/')
    def hello_world():
        constraint = uma.ResourceConstraint(database_resource[0], ["view"])
        claims = {
            "permissions": [
                {
                    "resource_set_id": database_resource[0],
                    "scopes": ["create"]
                }
            ]
        }
        if resource_control.check(constraint, claims):
            return 'Hello, World!'
        else:
            return "NO ACCESS!!!"

    app.run("0.0.0.0", debug=True)

if __name__ == "__main__":
    main()
