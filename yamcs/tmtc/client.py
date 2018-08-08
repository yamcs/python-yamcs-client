import functools

from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.types import management_pb2, yamcs_pb2


def _wrap_callback_parse_parameter_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse ParameterData
    from a WebSocket data message
    """
    if message.type == message.REPLY:
        data = management_pb2.ParameterSubscriptionResponse()
        data.ParseFromString(message.reply.data)
        subscription.subscription_id = data.subscriptionId
    elif message.type == message.DATA:
        if message.data.type == yamcs_pb2.PARAMETER:
            parameter_data_message = getattr(message.data, 'parameterData')
            #pylint: disable=protected-access
            subscription._process(parameter_data_message)
            if on_data:
                on_data(parameter_data_message)


def _build_named_object_ids(parameters):
    """
    Builds a list of NamedObjectId. This is a bit more complex than it really
    should be. In Python (for convenience) we allow the user to simply address
    entries by their alias via the NAMESPACE/NAME convention. Yamcs is not
    aware of this convention so we decompose it into distinct namespace and
    name fields.
    """
    if isinstance(parameters, str):
        parameters = [parameters]

    named_object_list = []
    for parameter in parameters:
        named_object_id = yamcs_pb2.NamedObjectId()
        if parameter.startswith('/'):
            named_object_id.name = parameter
        else:
            parts = parameter.split('/', 1)
            if len(parts) < 2:
                raise ValueError('Failed to process {}. Use fully-qualified '
                                 'XTCE names or, alternatively, an alias in '
                                 'in the format NAMESPACE/NAME'
                                 .format(parameter))
            named_object_id.namespace = parts[0]
            named_object_id.name = parts[1]
        named_object_list.append(named_object_id)
    return named_object_list


class ParameterSubscriptionFuture(WebSocketSubscriptionFuture):
    """
    Local object representing a subscription of zero or more parameters.

    A subscription object stores the last received value of each
    subscribed parameter.
    """

    def __init__(self, manager):
        super(ParameterSubscriptionFuture, self).__init__(manager)
        self.value_cache = {}

        # The actual subscription_id is set async after server reply
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
        options.id.extend(_build_named_object_ids(parameters))

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
        options.id.extend(_build_named_object_ids(parameters))

        self._manager.send('unsubscribe', options)

    def get_value(self, parameter):
        pass

    def _process(self, parameter_data):
        for pval in parameter_data.parameter:
            name = pval.id.name
            if pval.id.namespace:
                name = pval.id.namespace + '/' + name
            self.value_cache[name] = pval


class ProcessorClient(object):

    def __init__(self, client, instance, processor):
        super(ProcessorClient, self).__init__()
        self._client = client
        self._instance = instance
        self._processor = processor

    def issue_command(self, command, args):
        pass

    def create_parameter_subscription(self,
                                      parameters,
                                      on_data=None,
                                      abort_on_invalid=True,
                                      update_on_expiration=False,
                                      send_from_cache=True):
        """
        Create a new parameter subscription. This method blocks and returns
        the assigned subscription id.

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
        options.id.extend(_build_named_object_ids(parameters))

        manager = WebSocketSubscriptionManager(
            self._client, resource='parameter', options=options)

        # Represent subscription as a future
        subscription = ParameterSubscriptionFuture(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_parameter_data, subscription, on_data)

        manager.open(wrapped_callback, instance=self._instance)
        return subscription
