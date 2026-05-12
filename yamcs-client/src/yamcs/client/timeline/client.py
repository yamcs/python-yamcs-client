import datetime
from typing import Iterable, Optional

from yamcs.client.core import pagination
from yamcs.client.core.context import Context
from yamcs.client.core.helpers import to_isostring, to_server_time
from yamcs.client.timeline.model import Band, TimelineItem, View
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
        url = f"/timeline/{self._instance}/views/{view.id}"
        req = timeline_pb2.SaveViewRequest()
        req.name = view._proto.name
        req.description = view._proto.description
        req.bands[:] = [band.id for band in view._proto.bands]
        response = self.ctx.put_proto(url, data=req.SerializeToString())

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
        url = f"/timeline/{self._instance}/bands/{band.id}"
        req = timeline_pb2.SaveBandRequest()
        req.source = "rdb"
        req.type = band._proto.type
        req.shared = True
        req.name = band._proto.name
        req.description = band._proto.description
        for k in band._proto.tags:
            req.tags.append(k)
        for k, v in band._as_properties().items():
            req.properties[k] = v
        for k, v in band.extra.items():
            req.extra[k] = v

        response = self.ctx.put_proto(url, data=req.SerializeToString())

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
    ) -> Iterable[TimelineItem]:
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
            item_mapper=TimelineItem._as_subclass,
        )

    def get_item(self, id: str) -> TimelineItem:
        """
        Fetch an item by its identifier.

        :param id:
            Item identifier
        """
        url = f"/timeline/{self._instance}/items/{id}"
        response = self.ctx.get_proto(url)
        message = timeline_pb2.TimelineItem()
        message.ParseFromString(response.content)
        return TimelineItem._from_proto(message)

    def save_item(self, item: TimelineItem):
        """
        Save or update an item.

        :param item:
            TimelineItem object
        """
        url = f"/timeline/{self._instance}/items/{item.id}"
        req = timeline_pb2.SaveItemRequest()

        proto = item._to_proto()
        req.type = proto.type

        req.autoStart = item.auto_start
        req.name = item.name

        if proto.tags:
            req.tags.MergeFrom(proto.tags)

        if proto.properties:
            req.properties.MergeFrom(proto.properties)

        if proto.extra:
            req.extra.MergeFrom(proto.extra)

        if proto.HasField("start"):
            req.start.MergeFrom(proto.start)

        if proto.predecessors:
            req.predecessors.MergeFrom(proto.predecessors)

        if proto.HasField("duration"):
            req.duration.MergeFrom(proto.duration)
        if proto.HasField("activityDefinition"):
            req.activityDefinition.MergeFrom(proto.activityDefinition)

        self.ctx.put_proto(url, data=req.SerializeToString())

    def delete_item(self, item: str):
        """
        Delete an item.

        :param item:
            Item identifier.
        """
        url = f"/timeline/{self._instance}/items/{item}"
        self.ctx.delete_proto(url)

    def delete_items(
        self,
        start: Optional[datetime.datetime] = None,
        stop: Optional[datetime.datetime] = None,
        filter: Optional[str] = None,
    ):
        """
        Batch-delete items.

        :param start:
            Minimum stop time of the returned items (exclusive)
        :param stop:
            Maximum start time of the returned items (exclusive)
        :param filter:
            Filter string
        """
        req = timeline_pb2.BatchDeleteItemsRequest()
        if start:
            req.start.MergeFrom(to_server_time(start))
        if stop:
            req.stop.MergeFrom(to_server_time(stop))
        if filter:
            req.filter = filter

        url = f"/timeline/{self._instance}/items:batchDelete"
        self.ctx.post_proto(url, data=req.SerializeToString())
