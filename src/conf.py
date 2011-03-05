# TODO: this is a silly class. make it serious.

class ListConfigFile:
    def __init__(self, filename):
        # TODO: error checking
        self.file = open(filename, 'r')
    def __iter__(self):
        return self.file.readlines().__iter__()
