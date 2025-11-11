# This is a simple object to store and retrieve paths across callbacks
class FileCache:
    def __init__(self):
        self.filepath = None

    def set(self, path):
        self.filepath = path

    def get(self):
        return self.filepath

# You can create more caches like this for other purposes
inputfileDirCache = FileCache()
