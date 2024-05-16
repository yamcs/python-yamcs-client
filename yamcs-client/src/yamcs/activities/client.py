import functools
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Union
from datetime import datetime
from yamcs.core import pagination
from yamcs.core.context import Context
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import to_isostring
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.activities.model import ActivityInfo, ActivityLogInfo, ExecutorInfo
from yamcs.client.activities import ManualActivity, ScriptActivity, CommandActivity, CommandStackActivity
from yamcs.protobuf.activities import activities_pb2, activities_service_pb2

class GlobalActivityStatusSubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to global ongoing activities status updates.

    A subscription object stores the number of ongoing activities.
    """
    def __init__(self, manager):
        super(GlobalActivityStatusSubscription, self).__init__(manager)

        self.ongoingCount: Optional[int] = None
        """The number of ongoing activities."""

    def _process(self, ongoingCount):
        self.ongoingCount = ongoingCount

def _wrap_callback_parse_global_activity_status(subscription, on_data, message):
    """
    Wraps a user callback to parse GlobalActivityStatus
    from a WebSocket data message
    """
    pb = activities_service_pb2.GlobalActivityStatus()
    message.Unpack(pb)
    ongoingCount = pb.ongoingCount
    subscription._process(ongoingCount)
    if on_data:
        on_data(ongoingCount)

def _wrap_callback_parse_activity(on_data, message):
    """
    Wraps a user callback to parse ActivityInfo
    from a WebSocket data message
    """
    pb = activities_pb2.ActivityInfo()
    message.Unpack(pb)
    on_data(ActivityInfo(pb))

def _wrap_callback_parse_activity_log(on_data, message):
    """
    Wraps a user callback to parse ActivityLogInfo
    from a WebSocket data message
    """
    pb = activities_pb2.ActivityLogInfo()
    message.Unpack(pb)
    on_data(ActivityLogInfo(pb))

class ActivitiesClient:
    def __init__(self, ctx: Context, instance: str):
        super(ActivitiesClient, self).__init__()
        self.ctx = ctx
        self._instance = instance

    def list_activities(self,
        type: Optional[str] = None,
        status: Optional[str] = None,
        text_filter: Optional[str] = None,
        start: Optional[datetime] = None,
        stop: Optional[datetime] = None,
        page_size: int = 100,
        descending: bool = False) -> Iterable[ActivityInfo]:
        """
        Reads activities between the specified start and stop time.

        .. note::

            This method will send out multiple requests when more than
            ``page_size`` activities are queried. For large queries, consider
            using :meth:`stream_activities` instead, it uses server-streaming
            based on a single request.

        :param type:
            The type of the returned activity.
        :param status:
            Filter on activity status.
            One of ``RUNNING``, ``CANCELLED``, ``SUCCESSFUL``, ``FAILED``.
        :param text_filter:
            Filter the description of the returned activities
        :param start:
            Minimum start date of the returned activities (inclusive)
        :param stop:
            Maximum start date of the returned activities (exclusive)
        :param page_size:
            Page size of underlying requests. Higher values imply
            less overhead, but risk hitting the maximum message size
            limit.
        :param descending:
            If set to ``True`` events are fetched in reverse
            order (most recent first).
        """

        params: Dict[str, Any] = {
            "order": "desc" if descending else "desc",
        }

        if type is not None:
            params["type"] = type
        if status is not None:
            params["status"] = status
        if page_size is not None:
            params["limit"] = page_size
        if start is not None:
            params["start"] = to_isostring(start)
        if stop is not None:
            params["stop"] = to_isostring(stop)
        if text_filter is not None:
            params["q"] = text_filter

        return pagination.Iterator(
            ctx=self.ctx,
            path=f"/activities/{self._instance}/activities",
            params=params,
            response_class=activities_service_pb2.ListActivitiesResponse,
            items_key="activities",
            item_mapper=ActivityInfo,
        )

    def list_executors(self) -> List[ExecutorInfo]:
        """
        List available executors
        """
        url = f"/activities/{self._instance}/executors"
        response = self.ctx.get_proto(url)
        message = activities_service_pb2.ListExecutorsResponse()
        message.ParseFromString(response.content)
        return [ExecutorInfo(executor) for executor in message.executors]

    def list_scripts(self) -> List[str]:
        """
        List scripts available for activities of type SCRIPT
        """
        url = f"/activities/{self._instance}/scripts"
        response = self.ctx.get_proto(url)
        message = activities_service_pb2.ListScriptsResponse()
        message.ParseFromString(response.content)
        return [script for script in message.scripts]

    def get_activity_log(self, activity: str) -> List[ActivityLogInfo]:
        """
        Get the activity log
        """
        url = f"/activities/{self._instance}/activities/{activity}/log"
        response = self.ctx.get_proto(url)
        message = activities_service_pb2.GetActivityLogResponse()
        message.ParseFromString(response.content)
        return [ActivityLogInfo(log) for log in message.logs]

    def get_activity(self, activity: str) -> ActivityInfo:
        """
        Get an activity
        """
        url = f"/activities/{self._instance}/activities/{activity}"
        response = self.ctx.get_proto(url)
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def cancel_activity(self, activity: str):
        """
        Cancel an ongoing activity
        """
        url = f"/activities/{self._instance}/activities/{activity}:cancel"
        response = self.ctx.post_proto(url)
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def complete_manual_activity(self, activity : str, failureReason : Optional[str] = None):
        """
        Mark an ongoing activity as completed.

        This method may only be used with manual activities.
        """
        req = activities_service_pb2.CompleteManualActivityRequest()
        req.instance = self._instance
        req.activity = activity
        if failureReason:
            req.failureReason = failureReason

        url = f"/activities/{self._instance}/activities/{activity}:complete"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def start_manual_activity(self, name: str, comment: Optional[str] = None):
        """
        Start a manual activity
        """
        activity = ManualActivity(name, comment=comment)
        req = activity._to_proto()

        url = f"/activities/{self._instance}/activities"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def start_script_activity(self, script: str, args: Optional[Union[str, List[str]]] = None, processor: Optional[str] = None, comment: Optional[str] = None):
        """
        Start a script activity
        """
        activity = ScriptActivity(script, args, processor=processor, comment=comment)
        req = activity._to_proto()

        url = f"/activities/{self._instance}/activities"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def start_command_activity(self, command: str, args: Optional[dict] = None, extra: Optional[dict] = None, processor: Optional[str] = None, comment: Optional[str] = None):
        """
        Start a command activity
        """
        activity = CommandActivity(command, extra=extra, processor=processor, comment=comment)
        if args:
            activity.args = args
        if extra:
            activity.extra = extra
        req = activity._to_proto()

        url = f"/activities/{self._instance}/activities"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def start_command_stack_activity(self, bucket: str, stack: str, processor: Optional[str] = None, comment: Optional[str] = None):
        """
        Start a command activity
        """
        activity = CommandStackActivity(bucket, stack, processor=processor, comment=comment)
        req = activity._to_proto()

        url = f"/activities/{self._instance}/activities"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    # This function is for 'CUSTOM' activities; for SCRIPT, COMMAND, COMMAND_STACK, MANUAL see functions above
    def start_activity(self, type: str, args: Optional[Mapping[str, Any]] = None, comment: Optional[str] = None):
        """
        Start an activity
        """
        req = activities_pb2.ActivityDefinitionInfo()
        req.type = type
        if args:
            for key, value in args.items():
                req.args[key] = value
        if comment:
            req.comment = comment

        url = f"/activities/{self._instance}/activities"
        response = self.ctx.post_proto(url, data=req.SerializeToString())
        message = activities_pb2.ActivityInfo()
        message.ParseFromString(response.content)
        return ActivityInfo(message)

    def create_global_status_subscription(self,
                                          on_data: Optional[Callable[[int], None]] = None,
                                          timeout: float = 60,
                                         ) -> GlobalActivityStatusSubscription:
        """
        Create a new subscription for receiving global status updates on the number of ongoing activites.

        This method returns a future, then returns immediately. Stop the
        subscription by canceling the future.

        :param on_data:
            Function that gets called with :class:`.int` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.

        :return:
            A Future that can be used to manage the background websocket subscription.
        """
        options = activities_service_pb2.SubscribeGlobalStatusRequest()
        options.instance = self._instance
        manager = WebSocketSubscriptionManager(self.ctx, topic="global-activity-status", options=options)

        # Represent subscription as a future
        subscription = GlobalActivityStatusSubscription(manager)

        wrapped_callback = functools.partial(_wrap_callback_parse_global_activity_status, subscription, on_data)

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_activities_subscription(self,
                                       on_data: Callable[[ActivityInfo], None],
                                       timeout: float = 60,
                                      ) -> WebSocketSubscriptionFuture:
        """
        :param on_data:
            Function that gets called with :class:`.ActivityInfo` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.

        :return:
            A Future that can be used to manage the background websocket subscription.
        """
        options = activities_service_pb2.SubscribeActivitiesRequest()
        options.instance = self._instance
        manager = WebSocketSubscriptionManager(self.ctx, topic="activities", options=options)

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(_wrap_callback_parse_activity, on_data)

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_activity_log_subscription(self,
                                         activity: str,
                                         on_data: Callable[[ActivityInfo], None],
                                         timeout: float = 60,
                                        ) -> WebSocketSubscriptionFuture:
        """
        :param activity:
            Activity identifier.
        :param on_data:
            Function that gets called with :class:`.ActivityInfo` updates.
        :param timeout:
            The amount of seconds to wait for the request to complete.

        :return:
            A Future that can be used to manage the background websocket subscription.
        """
        options = activities_service_pb2.SubscribeActivityLogRequest()
        options.instance = self._instance
        options.activity = activity
        manager = WebSocketSubscriptionManager(self.ctx, topic="activity-log", options=options)

        # Represent subscription as a future
        subscription = WebSocketSubscriptionFuture(manager)

        wrapped_callback = functools.partial(_wrap_callback_parse_activity_log, on_data)

        manager.open(wrapped_callback)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
