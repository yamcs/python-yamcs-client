import datetime
from typing import Iterable, Optional

from yamcs.client.core import pagination
from yamcs.client.core.context import Context
from yamcs.client.core.helpers import to_isostring
from yamcs.client.timeline.model import Band, Item, View
from yamcs.protobuf.timeline import timeline_pb2

__all__ = [
    "TimelineClient",
]


class TimelineClient:
    """
    Client for working with Yamcs timeline.
    """

    def __init__(self, ctx: Context, instance: str):
        super(TimelineClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_views(self) -> Iterable[View]:
        """
        List the views.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(f"/timeline/{self._instance}/views")
        message = timeline_pb2.ListViewsResponse()
        message.ParseFromString(response.content)
        return iter([View(proto) for proto in getattr(message, "views")])

    def get_view(self, id: str) -> View:
        """
        Fetch a view by its identifier.

        :param id:
            View identifier
        """
        url = f"/timeline/{self._instance}/views/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineView()
        message.ParseFromString(response.content)
        return View(message)

    def save_view(self, view: View):
        """
        Save or update a view.

        :param view:
            View object
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

    def delete_view(self, view: str):
        """
        Delete a view.

        :param view:
            View identifier.
        """
        url = f"/timeline/{self._instance}/views/{view}"
        self.ctx.delete_proto(url)

    def list_bands(self) -> Iterable[Band]:
        """
        List the bands.
        """
        # Server does not do pagination on listings of this resource.
        # Return an iterator anyway for similarity with other API methods
        response = self.ctx.get_proto(f"/timeline/{self._instance}/bands")
        message = timeline_pb2.ListBandsResponse()
        message.ParseFromString(response.content)
        return iter([Band._as_subclass(proto) for proto in getattr(message, "bands")])

    def get_band(self, id: str) -> Band:
        """
        Fetch a band by its identifier.

        :param id:
            Band identifier
        """
        url = f"/timeline/{self._instance}/bands/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineBand()
        message.ParseFromString(response.content)
        return Band._as_subclass(message)

    def save_band(self, band: Band):
        """
        Save or update a band.

        :param band:
            Band object
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
        for k, v in band._as_properties().items():
            req.properties[k] = v

        if band.id:
            response = self.ctx.put_proto(url, data=req.SerializeToString())
        else:
            response = self.ctx.post_proto(url, data=req.SerializeToString())

        message = timeline_pb2.TimelineBand()
        message.ParseFromString(response.content)
        band._proto = message

    def delete_band(self, band: str):
        """
        Delete a band.

        :param band:
            Band identifier.
        """
        url = f"/timeline/{self._instance}/bands/{band}"
        self.ctx.delete_proto(url)

    def list_items(
        self,
        band: Optional[str] = None,
        start: Optional[datetime.datetime] = None,
        stop: Optional[datetime.datetime] = None,
        page_size: int = 500,
    ) -> Iterable[Item]:
        """
        List the items.

        :param band:
            Return only items matching the specified band
        :param start:
            Minimum stop time of the returned items (exclusive)
        :param stop:
            Maximum start time of the returned items (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply less
            overhead, but risk hitting the maximum message size limit.
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

    def get_item(self, id: str) -> Item:
        """
        Fetch an item by its identifier.

        :param id:
            Item identifier
        """
        url = f"/timeline/{self._instance}/items/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineItem()
        message.ParseFromString(response.content)
        return Item(message)

    def save_item(self, item: Item):
        """
        Save or update an item.

        :param item:
            Item object
        """
        if item.id:
            url = f"/timeline/{self._instance}/items/{item.id}"
            req = timeline_pb2.UpdateItemRequest()
        else:
            url = f"/timeline/{self._instance}/items"
            req = timeline_pb2.CreateItemRequest()
            req.type = item._proto.type

        if item._proto.HasField("name"):
            req.name = item._proto.name

        if item._proto.tags:
            req.tags.MergeFrom(item._proto.tags)
        elif item.id:
            req.clearTags = True

        if item._proto.properties:
            req.properties.MergeFrom(item._proto.properties)
        elif item.id:
            req.clearProperties = True

        req.start.MergeFrom(item._proto.start)
        if item._proto.HasField("duration"):
            req.duration.MergeFrom(item._proto.duration)
        if item._proto.HasField("activityDefinition"):
            req.activityDefinition.MergeFrom(item._proto.activityDefinition)

        if item.id:
            response = self.ctx.put_proto(url, data=req.SerializeToString())
        else:
            response = self.ctx.post_proto(url, data=req.SerializeToString())

        message = timeline_pb2.TimelineItem()
        message.ParseFromString(response.content)
        item._proto = message

    def delete_item(self, item: str):
        """
        Delete an item.

        :param item:
            Item identifier.
        """
        url = f"/timeline/{self._instance}/items/{item}"
        self.ctx.delete_proto(url)
