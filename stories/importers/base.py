import requests


class BaseAPIConsumer:

    target = None
    meta = None
    items = []

    def fetch_items(self):
        return requests.get(url=self.target).json()

    def parse_items(self, json_content):
        if self.target is None:
            raise StopIteration()

        self.meta = json_content['meta']
        self.items = json_content['data']

        if self.meta['count'] == 0:
            raise StopIteration()

        self.target = self.meta['next']

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
