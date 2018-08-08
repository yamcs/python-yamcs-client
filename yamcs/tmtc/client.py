import functools

from yamcs.core.client import BaseClient
from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.types import management_pb2, yamcs_pb2


def _wrap_callback_parse_parameter_data(subscription, callback, message):
    """
    Wraps a user callback to parse ParameterData
    from a WebSocket data message
    """
    if message.type == message.REPLY:
        data = management_pb2.ParameterSubscriptionResponse()
        data.ParseFromString(message.reply.data)
        subscription.subscription_id = data.subscriptionId
    elif message.type == message.DATA:
        if message.data.type == yamcs_pb2.PARAMETER:
            parameter_data_message = getattr(message.data, 'parameterData')
            callback(parameter_data_message)


class ParameterSubscriptionFuture(WebSocketSubscriptionFuture):

    def __init__(self, manager):
        super(ParameterSubscriptionFuture, self).__init__(manager)
        self.subscription_id = -1

    def add(self,
            parameters,
            abort_on_invalid=True,
            send_from_cache=True):
        """
        Add one or more parameters to this subscription.

        :param str or str[] parameters: Parameter(s) to be added
        :param bool abort_on_invalid: If True one invalid parameter
                                      means any other parameter in the
                                      request will also not be added
                                      to the subscription.
        :param bool send_from_cache: If ``True`` the last processed parameter
                                     value is sent from parameter cache.
                                     When ``False`` only newly processed
                                     parameters are received.
        """

        # Verify that we already know our assigned subscription_id
        assert self.subscription_id != -1

        if not parameters:
            return

        options = management_pb2.ParameterSubscriptionRequest()
        options.subscriptionId = self.subscription_id
        options.abortOnInvalid = abort_on_invalid
        options.sendFromCache = send_from_cache
        if isinstance(parameters, str):
            named_object_id = options.id.add()
            named_object_id.name = parameters
        else:
            for parameter in parameters:
                named_object_id = options.id.add()
                named_object_id.name = parameter

        self._manager.send('subscribe', options)

    def remove(self, parameters):
        """
        Remove one or more parameters from this subscription.

        :param str or str[] parameters: Parameter(s) to be removed
        """

        # Verify that we already know our assigned subscription_id
        assert self.subscription_id != -1

        if not parameters:
            return

        options = management_pb2.ParameterSubscriptionRequest()
        options.subscriptionId = self.subscription_id
        if isinstance(parameters, str):
            named_object_id = options.id.add()
            named_object_id.name = parameters
        else:
            for parameter in parameters:
                named_object_id = options.id.add()
                named_object_id.name = parameter

        self._manager.send('unsubscribe', options)


class ProcessorClient(BaseClient):

    @classmethod
    def processor_path(cls, instance, processor):
        """
        Return the resource path for a processor.
        """
        return 'processors/{}/{}'.format(instance, processor)

    def __init__(self, address, credentials=None):
        super(ProcessorClient, self).__init__(
            address, credentials=credentials)

    def create_parameter_subscription(self,
                                      processor,
                                      parameters,
                                      callback,
                                      abort_on_invalid=True,
                                      update_on_expiration=False,
                                      send_from_cache=True):
        """
        Create a new parameter subscription. This method blocks and returns
        the assigned subscription id.

        :param str processor: Fully-qualified processor resource name.
                              Example: ``processors/INSTANCE_ID/PROCESSOR_ID``
        :param str[] parameters: Parameter names (or aliases).
        :param bool abort_on_invalid: If ``True`` an error is generated when
                                      invalid parameters are specified.
        :param bool update_on_expiration: If ``True`` an update is received
                                          when a parameter value has become
                                          expired. This update holds the
                                          same value as the last known valid
                                          value, but with status set to
                                          ``EXPIRED``.
        :param bool send_from_cache: If ``True`` the last processed parameter
                                     value is sent from parameter cache.
                                     When ``False`` only newly processed
                                     parameters are received.

        :rtype: A :class:`~yamcs.core.futures.Future` object that can be
                used to manage the background websocket subscription.
        """
        options = management_pb2.ParameterSubscriptionRequest()
        options.subscriptionId = -1  # This means 'create a new subscription'
        options.abortOnInvalid = abort_on_invalid
        options.updateOnExpiration = update_on_expiration
        options.sendFromCache = send_from_cache
        if isinstance(parameters, str):
            named_object_id = options.id.add()
            named_object_id.name = parameters
        else:
            for parameter in parameters:
                named_object_id = options.id.add()
                named_object_id.name = parameter

        manager = WebSocketSubscriptionManager(
            self, resource='parameter', options=options)

        # Represent subscription as a future
        subscription = ParameterSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_parameter_data, subscription, callback)

        manager.open(wrapped_callback, instance='simulator')
        return subscription
