
class Resource:
    def __init__(self, name, scopes=None):
        self.name = name
        if scopes is None:
            self.scopes = []
        else:
            self.scopes = scopes
