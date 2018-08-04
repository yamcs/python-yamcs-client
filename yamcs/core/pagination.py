import json


class Iterator(object):

    def __init__(self, client, path, params, items_key='items'):
        self.client = client
        self.path = path
        self.params = params
        self.items_key = items_key

        self.num_results = 0
        self.page_number = 0
        self._continuation_token = None

    def __iter__(self):
        page_items = self._next_page()
        while page_items:
            self.page_number += 1

            for item in page_items:
                self.num_results += 1
                yield item

            page_items = self._next_page()

    def _next_page(self):
        if self.page_number == 0 or self._continuation_token:
            params = dict(self.params)

            # 'continue' is only allowed to be used by this class
            params.pop('continue', None)
            if self._continuation_token is not None:
                params['continue'] = self._continuation_token

            response = self.client._get(path=self.path, params=params)
            response_dict = json.loads(response.content)

            items = response_dict.get(self.items_key, [])
            self._continuation_token = response_dict.get('continuationToken')
            return items
