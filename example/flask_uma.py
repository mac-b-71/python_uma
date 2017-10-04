from flask import Flask, request
import jwt

import uma


app = Flask(__name__)


def define_resource(resource_server, resource):
    _id = resource_server.register_resource(resource)
    return _id, resource


def main():
    uma.UmaConfig.token_endpoint = "http://myhightech.org:9000/auth/realms/python/protocol/openid-connect/token"
    uma.UmaConfig.authz_endpoint = "http://myhightech.org:9000/auth/realms/python/authz/protection"

    uma.UmaConfig.authenticator = uma.ClientCredentialsAuthenticator("resource-server",
                                                       "508efdf3-63c2-4f0e-9c81-7711673c2f99")

    resource_server = uma.ResourceServer()
    resource_control = uma.ResourceControl()

    database_resource = define_resource(resource_server, uma.Resource("database", ["view", "create", "delete"]))

    @app.route('/')
    def hello_world():
        constraint = uma.ResourceConstraint(database_resource[0], ["view"])

        if "Authorization" not in request.headers:
            return resource_control.get_ticket(constraint)

        rpt = request.headers["Authorization"].replace("Bearer ", "")

        claims = jwt.decode(rpt, verify=False)
        if not resource_control.check(constraint, claims):
            return resource_control.get_ticket(constraint)

        return 'Hello, World!'

    app.run("0.0.0.0", debug=True)

if __name__ == "__main__":
    main()
