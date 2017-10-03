
class Resource:
    def __init__(self, name, scopes=None):
        self.name = name
        if scopes is None:
            self.scopes = []
        else:
            self.scopes = scopes


class ResourceConstraint:
    def __init__(self, resource_id, scopes=None):
        self.resource_id = resource_id
        if scopes is None:
            self.scopes = []
        else:
            self.scopes = scopes
