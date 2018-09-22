import functools
import threading

from yamcs.core.futures import WebSocketSubscriptionFuture
from yamcs.core.helpers import adapt_name_for_rest
from yamcs.core.subscriptions import WebSocketSubscriptionManager
from yamcs.protobuf import yamcs_pb2
from yamcs.protobuf.rest import rest_pb2
from yamcs.protobuf.web import web_pb2
from yamcs.tmtc.model import CommandHistory, IssuedCommand, ParameterData


class SequenceGenerator(object):
    """Static atomic counter."""
    _counter = 0
    _lock = threading.Lock()

    @classmethod
    def next(cls):
        with cls._lock:
            cls._counter += 1
            return cls._counter


def _wrap_callback_parse_parameter_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse ParameterData
    from a WebSocket data message
    """
    if message.type == message.REPLY:
        data = web_pb2.ParameterSubscriptionResponse()
        data.ParseFromString(message.reply.data)
        subscription.subscription_id = data.subscriptionId
    elif (message.type == message.DATA and
          message.data.type == yamcs_pb2.PARAMETER):
        parameter_data = ParameterData(getattr(message.data, 'parameterData'))
        #pylint: disable=protected-access
        subscription._process(parameter_data)
        if on_data:
            on_data(parameter_data)


def _wrap_callback_parse_cmdhist_data(subscription, on_data, message):
    """
    Wraps an (optional) user callback to parse CommandHistoryEntry
    from a WebSocket data message
    """
    if (message.type == message.DATA and
            message.data.type == yamcs_pb2.CMD_HISTORY):
        entry = getattr(message.data, 'command')
        #pylint: disable=protected-access
        rec = subscription._process(entry)
        if on_data:
            on_data(rec)


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


class CommandHistorySubscription(WebSocketSubscriptionFuture):
    """
    Local object providing access to command history updates.

    This object buffers all received command history. This is needed
    to stitch together incremental command history events.

    If you expect to receive a lot of command history updates
    you should periodically clear local cache via ``clear_cache()``.
    In future work, we may add automated buffer management within
    configurable watermarks.

    .. warning::
        If command history updates are received for commands
        that are not currently in the local cache, the returned
        information may be incomplete.
    """

    @staticmethod
    def _cache_key(cmd_id):
        """commandId is a tuple. Make a 'unique' key for it."""
        return '{}__{}__{}__{}'.format(
            cmd_id.generationTime, cmd_id.origin, cmd_id.sequenceNumber,
            cmd_id.commandName)

    def __init__(self, manager, buffer_size=100):
        super(CommandHistorySubscription, self).__init__(manager)
        self._cache = {}

    def clear_cache(self):
        """
        Clears local command history cache.
        """
        self._cache = {}

    def get_command_history(self, issued_command):
        """
        Gets locally cached CommandHistory for the specified command.

        :param .IssuedCommand issued_command: object representing a previously issued command.
        :rtype: .CommandHistory
        """
        #pylint: disable=protected-access
        entry = issued_command._proto.commandQueueEntry
        key = self._cache_key(entry.cmdId)
        if key in self._cache:
            return self._cache[key]
        return None

    def _process(self, entry):
        key = self._cache_key(entry.commandId)
        if key in self._cache:
            rec = self._cache[key]
        else:
            rec = CommandHistory()
            self._cache[key] = rec

        #pylint: disable=protected-access
        rec._update(entry.attr)
        return rec


class ParameterSubscription(WebSocketSubscriptionFuture):
    """
    Local object representing a subscription of zero or more parameters.

    A subscription object stores the last received value of each
    subscribed parameter.
    """

    def __init__(self, manager):
        super(ParameterSubscription, self).__init__(manager)

        self.value_cache = {}
        """Value cache keyed by parameter name."""

        self.delivery_count = 0
        """The number of parameter deliveries."""

        # The actual subscription_id is set async after server reply
        self.subscription_id = -1
        """Subscription number assigned by the server. This is set async,
        so may not be immediately available."""

    def add(self,
            parameters,
            abort_on_invalid=True,
            send_from_cache=True):
        """
        Add one or more parameters to this subscription.

        :param parameters: Parameter(s) to be added
        :type parameters: Union[str, str[]]
        :param bool abort_on_invalid: If ``True`` one invalid parameter
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

        options = web_pb2.ParameterSubscriptionRequest()
        options.subscriptionId = self.subscription_id
        options.abortOnInvalid = abort_on_invalid
        options.sendFromCache = send_from_cache
        options.id.extend(_build_named_object_ids(parameters))

        self._manager.send('subscribe', options)

    def remove(self, parameters):
        """
        Remove one or more parameters from this subscription.

        :param parameters: Parameter(s) to be removed
        :type parameters: Union[str, str[]]
        """

        # Verify that we already know our assigned subscription_id
        assert self.subscription_id != -1

        if not parameters:
            return

        options = web_pb2.ParameterSubscriptionRequest()
        options.subscriptionId = self.subscription_id
        options.id.extend(_build_named_object_ids(parameters))

        self._manager.send('unsubscribe', options)

    def get_value(self, parameter):
        """
        Returns the last value of a specific parameter from local cache.

        :rtype: .ParameterValue
        """
        return self.value_cache[parameter]

    def _process(self, parameter_data):
        self.delivery_count += 1
        for pval in parameter_data.parameters:
            self.value_cache[pval.name] = pval


class ProcessorClient(object):
    """Client object that groups operations linked to a specific processor."""

    def __init__(self, client, instance, processor):
        super(ProcessorClient, self).__init__()
        self._client = client
        self._instance = instance
        self._processor = processor

    def issue_command(self, command, args=None, dry_run=False, comment=None):
        """
        Issue the given command

        :rtype: .IssuedCommand
        """
        req = rest_pb2.IssueCommandRequest()
        req.sequenceNumber = SequenceGenerator.next()
        req.origin = 'uhuh'
        req.dryRun = dry_run
        if comment:
            req.comment = comment
        if args:
            for key in args:
                assignment = req.assignment.add()
                assignment.name = key
                assignment.value = str(args[key])

        command = adapt_name_for_rest(command)
        url = '/processors/{}/{}/commands{}'.format(
            self._instance, self._processor, command)
        response = self._client.post_proto(url, data=req.SerializeToString())
        proto = rest_pb2.IssueCommandResponse()
        proto.ParseFromString(response.content)
        return IssuedCommand(proto)

    def create_command_history_subscription(self, on_data=None, timeout=60):
        """
        Create a new command history subscription.


        :param on_data: Function that gets called with  :class:`.CommandHistory`
                        updates.
        :param float timeout: The amount of seconds to wait for the request
                              to complete.
        :return: Future that can be used to manage the background websocket subscription
        :rtype: .CommandHistorySubscription
        """
        manager = WebSocketSubscriptionManager(
            self._client, resource='cmdhistory')

        # Represent subscription as a future
        subscription = CommandHistorySubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_cmdhist_data, subscription, on_data)

        manager.open(wrapped_callback, instance=self._instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription

    def create_parameter_subscription(self,
                                      parameters,
                                      on_data=None,
                                      abort_on_invalid=True,
                                      update_on_expiration=False,
                                      send_from_cache=True,
                                      timeout=60):
        """
        Create a new parameter subscription.

        :param str[] parameters: Parameter names (or aliases).
        :param on_data: Function that gets called with  :class:`.ParameterData`
                        updates.
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
        :param float timeout: The amount of seconds to wait for the request
                              to complete.

        :return: A Future that can be used to manage the background websocket
                 subscription.
        :rtype: .ParameterSubscription
        """
        options = web_pb2.ParameterSubscriptionRequest()
        options.subscriptionId = -1  # This means 'create a new subscription'
        options.abortOnInvalid = abort_on_invalid
        options.updateOnExpiration = update_on_expiration
        options.sendFromCache = send_from_cache
        options.id.extend(_build_named_object_ids(parameters))

        manager = WebSocketSubscriptionManager(
            self._client, resource='parameter', options=options)

        # Represent subscription as a future
        subscription = ParameterSubscription(manager)

        wrapped_callback = functools.partial(
            _wrap_callback_parse_parameter_data, subscription, on_data)

        manager.open(wrapped_callback, instance=self._instance)

        # Wait until a reply or exception is received
        subscription.reply(timeout=timeout)

        return subscription
