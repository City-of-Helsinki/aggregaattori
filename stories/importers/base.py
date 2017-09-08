import requests


class BaseAPIConsumer:
    target = None
    items = []

    def get_items_from_json(self, json_content):
        raise NotImplementedError('get_items_from_json must be implemented')

    def get_next_target_from_json(self, json_content):
        raise NotImplementedError('get_next_target_from_json must be implemented')

    def fetch_items(self):
        return requests.get(url=self.target).json()

    def parse_items(self, json_content):
        if self.target is None:
            raise StopIteration()

        self.items = self.get_items_from_json(json_content)

        if len(self.items) == 0:
            raise StopIteration()

        self.target = self.get_next_target_from_json(json_content)

    def __iter__(self):
        return self

    def __next__(self):
        if self.items:
            return self.items.pop(0)

        if self.target is None:
            raise StopIteration()

        self.parse_items(self.fetch_items())

        if self.items:
            return self.items.pop(0)

        raise StopIteration()
