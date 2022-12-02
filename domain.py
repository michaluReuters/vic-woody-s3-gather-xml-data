class Sources:

    def __init__(self):
        self.metadatas = []

    def add_metadata(self, metadata: dict):
        self.metadatas.append(metadata)


class Workflow:

    def __init__(self):
        self.data = {}

    def add_data(self, key, data_to_add):
        self.data[key] = data_to_add
