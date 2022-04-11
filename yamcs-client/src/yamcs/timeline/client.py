from yamcs.core import pagination
from yamcs.core.helpers import to_isostring
from yamcs.protobuf.timeline import timeline_pb2
from yamcs.timeline.model import Band, Item, View


class TimelineClient:
    """
    Client for working with Yamcs timeline.
    """

    def __init__(self, ctx, instance):
        super(TimelineClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_views(self):
        """
        List the views.

        :rtype: ~collections.abc.Iterable[.View]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(f"/timeline/{self._instance}/views")
        message = timeline_pb2.ListViewsResponse()
        message.ParseFromString(response.content)
        return [View(proto) for proto in getattr(message, "views")]

    def get_view(self, id):
        """
        Fetch a view by its identifier.

        :param str id: View identifier
        :rtype: .View
        """
        url = f"/timeline/{self._instance}/views/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineView()
        message.ParseFromString(response.content)
        return View(message)

    def save_view(self, view):
        """
        Save or update a view.

        :param .View view: View object
        """
        if view.id:
            url = f"/timeline/{self._instance}/views/{view.id}"
            req = timeline_pb2.UpdateViewRequest()
        else:
            url = f"/timeline/{self._instance}/views"
            req = timeline_pb2.AddViewRequest()

        req.name = view._proto.name
        req.description = view._proto.description
        req.bands[:] = [band.id for band in view._proto.bands]

        if view.id:
            response = self.ctx.put_proto(url, data=req.SerializeToString())
        else:
            response = self.ctx.post_proto(url, data=req.SerializeToString())

        message = timeline_pb2.TimelineView()
        message.ParseFromString(response.content)
        view._proto = message

    def delete_view(self, view):
        """
        Delete a view.

        :param string view: View identifier.
        """
        url = f"/timeline/{self._instance}/views/{view}"
        self.ctx.delete_proto(url)

    def list_bands(self):
        """
        List the bands.

        :rtype: ~collections.abc.Iterable[.Band]
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(f"/timeline/{self._instance}/bands")
        message = timeline_pb2.ListBandsResponse()
        message.ParseFromString(response.content)
        return [Band._as_subclass(proto) for proto in getattr(message, "bands")]

    def get_band(self, id):
        """
        Fetch a band by its identifier.

        :param str id: Band identifier
        :rtype: .Band
        """
        url = f"/timeline/{self._instance}/bands/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineBand()
        message.ParseFromString(response.content)
        return Band._as_subclass(message)

    def save_band(self, band):
        """
        Save or update a band.

        :param .Band band: Band object
        """
        if band.id:
            url = f"/timeline/{self._instance}/bands/{band.id}"
            req = timeline_pb2.UpdateBandRequest()
        else:
            url = f"/timeline/{self._instance}/bands"
            req = timeline_pb2.AddBandRequest()
            req.source = "rdb"
            req.type = band._proto.type

        req.shared = True
        req.name = band._proto.name
        req.description = band._proto.description
        for k in band._proto.tags:
            req.tags.append(k)
        for k, v in band._proto.properties.items():
            req.properties[k] = v

        if band.id:
            response = self.ctx.put_proto(url, data=req.SerializeToString())
        else:
            response = self.ctx.post_proto(url, data=req.SerializeToString())

        message = timeline_pb2.TimelineBand()
        message.ParseFromString(response.content)
        band._proto = message

    def delete_band(self, band):
        """
        Delete a band.

        :param string band: Band identifier.
        """
        url = f"/timeline/{self._instance}/bands/{band}"
        self.ctx.delete_proto(url)

    def list_items(self, band=None, start=None, stop=None, page_size=500):
        """
        List the items.

        :param str band: Return only items matching the specified band
        :param ~datetime.datetime start: Minimum stop time of the returned
                                         items (exclusive)
        :param ~datetime.datetime stop: Maximum start time of the returned
                                        items (exclusive)
        :param int page_size: Page size of underlying requests. Higher values imply
                              less overhead, but risk hitting the maximum message size
                              limit.
        :rtype: ~collections.abc.Iterable[.Item]
        """
        params = {}
        if band is not None:
            params["band"] = band
        if page_size is not None:
            params["limit"] = page_size
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/timeline/{self._instance}/items",
            params=params,
            response_class=timeline_pb2.ListItemsResponse,
            items_key="items",
            item_mapper=Item,
        )

    def get_item(self, id):
        """
        Fetch an item by its identifier.

        :param str id: Item identifier
        :rtype: .Item
        """
        url = f"/timeline/{self._instance}/items/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineItem()
        message.ParseFromString(response.content)
        return Item(message)

    def save_item(self, item):
        """
        Save or update an item.

        :param .Item item: Item object
        """
        if item.id:
            url = f"/timeline/{self._instance}/items/{item.id}"
            req = timeline_pb2.UpdateItemRequest()
        else:
            url = f"/timeline/{self._instance}/items"
            req = timeline_pb2.CreateItemRequest()
            req.type = item._proto.type

        req.name = item._proto.name
        req.tags.MergeFrom(item._proto.tags)
        req.start.MergeFrom(item._proto.start)
        req.duration.MergeFrom(item._proto.duration)

        if item.id:
            response = self.ctx.put_proto(url, data=req.SerializeToString())
        else:
            response = self.ctx.post_proto(url, data=req.SerializeToString())

        message = timeline_pb2.TimelineItem()
        message.ParseFromString(response.content)
        item._proto = message

    def delete_item(self, item):
        """
        Delete an item.

        :param string item: Item identifier.
        """
        url = f"/timeline/{self._instance}/items/{item}"
        self.ctx.delete_proto(url)
