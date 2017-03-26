import json
import os

class SubjectFactory():
    def __init__(self, path, service):
        self.path = path
        self.service = service

    def new_from_json(self, name):
        if not os.path.exists(os.path.join(self.path, name)):
            return None
        with open(os.path.join(self.path, name), 'r') as f:
            config = json.loads(f.read())

        return self.new_from_config(config)

    def new_from_config(self, config):
        return FileBasedSubject(config, self.service)