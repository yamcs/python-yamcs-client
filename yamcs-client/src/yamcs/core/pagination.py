class Iterator:
    def __init__(
        self, ctx, path, params, response_class, items_key="items", item_mapper=None
    ):
        self.ctx = ctx
        self.path = path
        self.params = params
        self.response_class = response_class
        self.items_key = items_key
        self.item_mapper = item_mapper

        self.num_results = 0
        self.page_number = 0
        self._continuation_token = None

    def __iter__(self):
        page_items = self._next_page()
        while page_items:
            self.page_number += 1

            for item in page_items:
                self.num_results += 1
                if self.item_mapper:
                    yield self.item_mapper(item)
                else:
                    yield item

            page_items = self._next_page()

    def _next_page(self):
        if self.page_number == 0 or self._continuation_token:
            params = dict(self.params)

            # 'next' is only allowed to be used by this class
            params.pop("next", None)
            if self._continuation_token is not None:
                params["next"] = self._continuation_token

            response = self.ctx.get_proto(path=self.path, params=params)
            message = self.response_class()
            message.ParseFromString(response.content)
            items = getattr(message, self.items_key)
            self._continuation_token = getattr(message, "continuationToken")
            return items
        else:
            return None
