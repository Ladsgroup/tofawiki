class Cache(object):
    def get_value(self, key):
        """Main function"""
        raise NotImplementedError

    def blow_cahce(self):
        raise NotImplementedError