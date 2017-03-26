from .unknown import UnknownSubject

class FileBasedSubject(UnknownSubject):
    def __init__(self, config, service):
        super().__init__(service)
        self.config = config
        self.service = service
