class Service(object):
    """Interface for running services."""

    def validate(self):
        """
        Return if it's okay to run the service or not return error details when needed
        :return: bool|dict
        """
        raise NotImplementedError

    def run(self):
        """
        Return the result of service
        :return: str
        """
        raise NotImplementedError
